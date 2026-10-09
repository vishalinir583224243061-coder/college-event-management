"""
Smart College Event Management Agent - Flask Backend Application
Provides Web UI routes and JSON API endpoints for events, registrations, reports, and AI Agent.
"""

import os
import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response

import database
from ai_agent import AIAssistant, get_live_events_context

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "smart_college_event_mgmt_secret_key_2026")

# Initialize database on startup
database.init_db()

@app.context_processor
def inject_global_data():
    """Make notifications and category list available in all templates."""
    try:
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 5")
        recent_notifs = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT COUNT(*) as unread FROM notifications WHERE is_read = 0")
        unread_count = cursor.fetchone()['unread']
        conn.close()
    except Exception:
        recent_notifs = []
        unread_count = 0

    return {
        'recent_notifs': recent_notifs,
        'unread_notifs_count': unread_count,
        'categories': ['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar'],
        'current_year': datetime.now().year
    }

# ==========================================
# WEB PAGE ROUTES
# ==========================================

@app.route('/')
@app.route('/dashboard')
def dashboard():
    metrics = database.get_dashboard_metrics()
    return render_template('index.html', metrics=metrics)

@app.route('/events')
def events():
    category = request.args.get('category', 'All')
    status = request.args.get('status', 'All')
    search = request.args.get('search', '')
    events_list = database.get_all_events(category=category, status=status, search=search)
    return render_template('events.html', events=events_list, selected_category=category, selected_status=status, search=search)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = database.get_event_detail(event_id)
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for('events'))
    return render_template('event_detail.html', event=event)

@app.route('/register', methods=['GET', 'POST'])
def register():
    preselected_event_id = request.args.get('event_id', type=int)
    all_events = database.get_all_events(status='upcoming')
    
    if request.method == 'POST':
        event_id = request.form.get('event_id', type=int)
        student_name = request.form.get('student_name', '').strip()
        student_email = request.form.get('student_email', '').strip()
        student_id = request.form.get('student_id', '').strip()
        department = request.form.get('department', '').strip()
        phone = request.form.get('phone', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()

        if not all([event_id, student_name, student_email, student_id, department]):
            flash("Please fill in all required fields.", "warning")
            return render_template('register.html', events=all_events, preselected_event_id=preselected_event_id)

        success, result = database.register_student(
            event_id, student_name, student_email, student_id, department, phone, year_of_study
        )
        if success:
            return render_template('register.html', events=all_events, ticket_success=result)
        else:
            flash(result, "danger")
            return render_template('register.html', events=all_events, preselected_event_id=event_id)

    return render_template('register.html', events=all_events, preselected_event_id=preselected_event_id)

@app.route('/participants')
def participants():
    event_id = request.args.get('event_id')
    department = request.args.get('department', 'All')
    search = request.args.get('search', '')
    all_events = database.get_all_events()
    participants_list = database.get_all_participants(event_id=event_id, department=department, search=search)
    return render_template('participants.html', participants=participants_list, events=all_events,
                           selected_event=event_id, selected_dept=department, search=search)

@app.route('/reports')
def reports():
    data = database.get_event_reports_data()
    return render_template('reports.html', reports=data)

@app.route('/ai-agent')
def ai_agent_page():
    all_events = database.get_all_events()
    return render_template('ai_agent.html', events=all_events)

# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route('/api/dashboard/metrics')
def api_dashboard_metrics():
    metrics = database.get_dashboard_metrics()
    return jsonify(metrics)

@app.route('/api/events', methods=['GET', 'POST'])
def api_events():
    if request.method == 'GET':
        category = request.args.get('category')
        status = request.args.get('status')
        search = request.args.get('search')
        events_list = database.get_all_events(category, status, search)
        return jsonify({'success': True, 'events': events_list})

    # POST - Create new event
    data = request.get_json() or request.form
    title = data.get('title')
    category = data.get('category')
    description = data.get('description')
    event_date = data.get('event_date')
    event_time = data.get('event_time')
    venue = data.get('venue')
    poster_url = data.get('poster_url')
    capacity = int(data.get('capacity', 100))
    organizer = data.get('organizer', 'Campus Event Council')

    # Default poster image if not provided
    if not poster_url:
        poster_map = {
            'Technical': 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80',
            'Cultural': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80',
            'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80',
            'Workshop': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80',
            'Seminar': 'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=800&q=80'
        }
        poster_url = poster_map.get(category, 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&w=800&q=80')

    if not all([title, category, description, event_date, event_time, venue]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    new_id = database.create_event(title, category, description, event_date, event_time, venue, poster_url, capacity, organizer)
    return jsonify({'success': True, 'message': 'Event created successfully!', 'event_id': new_id}), 201

@app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def api_event_item(event_id):
    if request.method == 'GET':
        ev = database.get_event_detail(event_id)
        if not ev:
            return jsonify({'success': False, 'message': 'Event not found'}), 404
        return jsonify({'success': True, 'event': ev})

    elif request.method == 'PUT':
        data = request.get_json() or request.form
        title = data.get('title')
        category = data.get('category')
        description = data.get('description')
        event_date = data.get('event_date')
        event_time = data.get('event_time')
        venue = data.get('venue')
        poster_url = data.get('poster_url')
        capacity = int(data.get('capacity', 100))
        organizer = data.get('organizer', 'Campus Event Council')
        status = data.get('status', 'upcoming')

        database.update_event(event_id, title, category, description, event_date, event_time, venue, poster_url, capacity, organizer, status)
        return jsonify({'success': True, 'message': 'Event updated successfully!'})

    elif request.method == 'DELETE':
        database.delete_event(event_id)
        return jsonify({'success': True, 'message': 'Event deleted successfully!'})

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or request.form
    event_id = data.get('event_id')
    student_name = data.get('student_name')
    student_email = data.get('student_email')
    student_id = data.get('student_id')
    department = data.get('department')
    phone = data.get('phone', '')
    year_of_study = data.get('year_of_study', '')

    if not all([event_id, student_name, student_email, student_id, department]):
        return jsonify({'success': False, 'message': 'Please fill all required registration details'}), 400

    success, result = database.register_student(
        int(event_id), student_name, student_email, student_id, department, phone, year_of_study
    )
    if success:
        return jsonify({'success': True, 'ticket': result, 'message': 'Registration confirmed! 🎉'})
    else:
        return jsonify({'success': False, 'message': result}), 400

@app.route('/api/events/<int:event_id>/feedback', methods=['POST'])
def api_add_feedback(event_id):
    data = request.get_json() or request.form
    student_name = data.get('student_name', 'Student Attendee')
    department = data.get('department', 'CSE')
    rating = int(data.get('rating', 5))
    comments = data.get('comments', '').strip()

    if not comments:
        return jsonify({'success': False, 'message': 'Please provide comments'}), 400

    database.add_event_feedback(event_id, student_name, department, rating, comments)
    return jsonify({'success': True, 'message': 'Thank you! Your feedback has been recorded.'})

@app.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
def api_mark_notif_read(notif_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ==========================================
# CSV EXPORT ROUTES
# ==========================================

@app.route('/export/participants.csv')
def export_participants_csv():
    event_id = request.args.get('event_id')
    participants = database.get_all_participants(event_id=event_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Ticket Code', 'Student Name', 'College Email', 'Student ID', 'Department', 'Phone', 'Year', 'Event Title', 'Event Category', 'Registration Date'])

    for p in participants:
        writer.writerow([
            p.get('ticket_code', ''),
            p.get('student_name', ''),
            p.get('student_email', ''),
            p.get('student_id', ''),
            p.get('department', ''),
            p.get('phone', ''),
            p.get('year_of_study', ''),
            p.get('event_title', ''),
            p.get('event_category', ''),
            p.get('registration_date', '')
        ])

    csv_data = output.getvalue()
    filename = f"participants_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route('/export/events.csv')
def export_events_csv():
    data = database.get_event_reports_data()
    events = data['events']

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Event ID', 'Title', 'Category', 'Date', 'Venue', 'Capacity', 'Registered Students', 'Seat Fill Rate (%)', 'Status'])

    for ev in events:
        writer.writerow([
            ev.get('id', ''),
            ev.get('title', ''),
            ev.get('category', ''),
            ev.get('event_date', ''),
            ev.get('venue', ''),
            ev.get('capacity', ''),
            ev.get('registered_count', 0),
            ev.get('fill_rate', 0.0),
            ev.get('status', '')
        ])

    csv_data = output.getvalue()
    filename = f"events_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

# ==========================================
# AI AGENT REST API ROUTES
# ==========================================

@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400

    reply = AIAssistant.chat_query(message)
    return jsonify({'success': True, 'reply': reply})

@app.route('/api/ai/ideas', methods=['POST'])
def api_ai_ideas():
    data = request.get_json() or {}
    category = data.get('category', 'Technical')
    theme = data.get('theme', '')
    audience = data.get('audience', 'All College Students')

    ideas = AIAssistant.suggest_event_ideas(category, theme, audience)
    return jsonify({'success': True, 'result': ideas})

@app.route('/api/ai/description', methods=['POST'])
def api_ai_description():
    data = request.get_json() or {}
    title = data.get('title', 'Campus Innovation Hackfest')
    category = data.get('category', 'Technical')
    duration = data.get('duration', 'Full Day (8 Hours)')
    audience = data.get('audience', 'Undergraduate & Postgraduate Students')

    desc = AIAssistant.generate_event_description(title, category, duration, audience)
    return jsonify({'success': True, 'result': desc})

@app.route('/api/ai/schedule', methods=['POST'])
def api_ai_schedule():
    data = request.get_json() or {}
    title = data.get('title', 'AI & Cloud Masterclass')
    start_time = data.get('start_time', '09:30 AM')
    duration = float(data.get('duration_hours', 6))
    event_type = data.get('event_type', 'Workshop')

    schedule_text = AIAssistant.generate_schedule(title, start_time, duration, event_type)
    return jsonify({'success': True, 'result': schedule_text})

@app.route('/api/ai/reminder', methods=['POST'])
def api_ai_reminder():
    data = request.get_json() or {}
    event_id = int(data.get('event_id', 1))
    channel = data.get('channel', 'Email')

    reminder_text = AIAssistant.generate_reminder(event_id, channel)
    return jsonify({'success': True, 'result': reminder_text})

@app.route('/api/ai/report', methods=['POST'])
def api_ai_report():
    data = request.get_json() or {}
    event_id = int(data.get('event_id', 1))

    report_text = AIAssistant.generate_event_report(event_id)
    return jsonify({'success': True, 'result': report_text})

@app.route('/api/ai/feedback-summary', methods=['POST'])
def api_ai_feedback_summary():
    data = request.get_json() or {}
    event_id = int(data.get('event_id', 1))

    summary_text = AIAssistant.summarize_feedback(event_id)
    return jsonify({'success': True, 'result': summary_text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Smart College Event Management Agent on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
