"""
Database Module for Smart College Event Management Agent
Handles SQLite schema, connection management, queries, and demo seed data.
"""

import sqlite3
import os
import random
import string
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def generate_ticket_code(category):
    prefix_map = {
        'Technical': 'TECH',
        'Cultural': 'CULT',
        'Sports': 'SPRT',
        'Workshop': 'WKSH',
        'Seminar': 'SEMN'
    }
    prefix = prefix_map.get(category, 'EVNT')
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"PASS-{prefix}-{rand_part}"

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar')),
        description TEXT NOT NULL,
        event_date TEXT NOT NULL,
        event_time TEXT NOT NULL,
        venue TEXT NOT NULL,
        poster_url TEXT,
        capacity INTEGER DEFAULT 100,
        organizer TEXT,
        status TEXT DEFAULT 'upcoming' CHECK(status IN ('upcoming', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        student_email TEXT NOT NULL,
        student_id TEXT NOT NULL,
        department TEXT NOT NULL,
        phone TEXT,
        year_of_study TEXT,
        ticket_code TEXT UNIQUE NOT NULL,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
        UNIQUE(event_id, student_email),
        UNIQUE(event_id, student_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        event_id INTEGER,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        department TEXT,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        comments TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) as cnt FROM events")
    if cursor.fetchone()['cnt'] == 0:
        seed_sample_data(conn)

    conn.close()

def seed_sample_data(conn):
    cursor = conn.cursor()
    
    # Calculate dates based on current time
    today = datetime.now()
    
    events_data = [
        (
            "InnovateX 2026: National Tech Symposium",
            "Technical",
            "Annual flagship national technical symposium featuring competitive hackathons, algorithmic coding battles, paper presentations, and robotics arena. Win prizes worth ₹1,50,000!",
            (today + timedelta(days=6)).strftime("%Y-%m-%d"),
            "09:30 AM",
            "Main Auditorium & Turing Computing Labs",
            "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
            250,
            "Dept. of Computer Science & Engineering",
            "upcoming"
        ),
        (
            "GenAI & Agentic Workflows Hands-on Workshop",
            "Workshop",
            "Intensive hands-on masterclass on building LLM agents, RAG architectures, and multimodal AI apps using Gemini and Python. All attendees receive certificates of excellence.",
            (today + timedelta(days=11)).strftime("%Y-%m-%d"),
            "10:00 AM",
            "Dr. APJ Abdul Kalam Seminar Hall",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80",
            120,
            "Centre for Artificial Intelligence & Data Science",
            "upcoming"
        ),
        (
            "Rhythm & Beats: Cultural Fiesta 2026",
            "Cultural",
            "A dazzling night of rhythm, classical fusion, battle of bands, theatrical drama, and celebrity DJ night. Celebrate talent, diversity, and creativity across campuses!",
            (today + timedelta(days=16)).strftime("%Y-%m-%d"),
            "05:00 PM",
            "Open Air Amphitheatre & Ground Stage",
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80",
            500,
            "College Fine Arts & Cultural Council",
            "upcoming"
        ),
        (
            "Inter-Departmental Premier Sports Championship",
            "Sports",
            "Unleash athletic excellence! Multi-sport tournament featuring Cricket, Football, Basketball, Badminton, and Sprint relays. Cheer for your department champions!",
            (today + timedelta(days=20)).strftime("%Y-%m-%d"),
            "08:00 AM",
            "University Sports Complex & Stadium",
            "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
            300,
            "Department of Physical Education",
            "upcoming"
        ),
        (
            "Leadership & Tech Entrepreneurship Summit",
            "Seminar",
            "Exclusive executive keynote address by unicorn startup founders and venture capitalists on scaling deep-tech startups, pitching to investors, and engineering career paths.",
            (today + timedelta(days=25)).strftime("%Y-%m-%d"),
            "11:00 AM",
            "Sir CV Raman Convention Centre",
            "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=800&q=80",
            180,
            "Entrepreneurship & Incubation Cell",
            "upcoming"
        ),
        (
            "Autonomous Robotics & Drone Derby",
            "Technical",
            "Build and race autonomous line-following rovers, obstacle navigating hexacopters, and robot combatants in our high-voltage arena.",
            (today + timedelta(days=32)).strftime("%Y-%m-%d"),
            "09:00 AM",
            "Robotics & Mechatronics Arena",
            "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80",
            100,
            "Dept. of Electronics & Robotics Club",
            "upcoming"
        ),
        (
            "Cloud Native & DevOps Bootcamp",
            "Workshop",
            "Master Docker containers, Kubernetes orchestration, and CI/CD pipelines with real-world industry deployable microservices.",
            (today - timedelta(days=12)).strftime("%Y-%m-%d"),
            "09:30 AM",
            "Server Architecture Lab 3",
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
            80,
            "Dept. of Information Technology",
            "completed"
        ),
        (
            "Freshers Inaugural Welcome & Talent Hunt",
            "Cultural",
            "Welcoming the incoming cohort of students with musical performances, standup comedy, mimicry, and fresh talent awards.",
            (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "02:00 PM",
            "Central Auditorium",
            "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80",
            400,
            "Student Union Council",
            "completed"
        )
    ]

    for ev in events_data:
        cursor.execute("""
            INSERT INTO events (title, category, description, event_date, event_time, venue, poster_url, capacity, organizer, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ev)

    # Fetch inserted event IDs
    cursor.execute("SELECT id, title, category FROM events")
    all_events = cursor.fetchall()

    sample_students = [
        ("Aarav Sharma", "aarav.sharma@college.edu", "23CSE014", "CSE", "9876543210", "3rd Year"),
        ("Ananya Iyer", "ananya.iyer@college.edu", "23AIDS009", "AI & DS", "9876543211", "3rd Year"),
        ("Rohan Verma", "rohan.verma@college.edu", "24ECE045", "ECE", "9876543212", "2nd Year"),
        ("Sneha Patel", "sneha.patel@college.edu", "23IT033", "IT", "9876543213", "3rd Year"),
        ("Vikram Singh", "vikram.singh@college.edu", "22MECH071", "MECH", "9876543214", "4th Year"),
        ("Pooja Nair", "pooja.nair@college.edu", "24CSE112", "CSE", "9876543215", "2nd Year"),
        ("Kavya Reddy", "kavya.reddy@college.edu", "23AIDS058", "AI & DS", "9876543216", "3rd Year"),
        ("Aditya Gupta", "aditya.gupta@college.edu", "25CIVIL021", "CIVIL", "9876543217", "1st Year"),
        ("Divya Mehra", "divya.mehra@college.edu", "24MBA018", "MBA", "9876543218", "2nd Year"),
        ("Rahul Desai", "rahul.desai@college.edu", "23ECE089", "ECE", "9876543219", "3rd Year"),
        ("Meera Joshi", "meera.joshi@college.edu", "24IT051", "IT", "9876543220", "2nd Year"),
        ("Siddharth Roy", "siddharth.roy@college.edu", "23CSE088", "CSE", "9876543221", "3rd Year"),
        ("Tanvi Kulkarni", "tanvi.kulkarni@college.edu", "25AIDS034", "AI & DS", "9876543222", "1st Year"),
        ("Gaurav Menon", "gaurav.menon@college.edu", "22ECE012", "ECE", "9876543223", "4th Year"),
        ("Ishita Sen", "ishita.sen@college.edu", "23MECH042", "MECH", "9876543224", "3rd Year"),
        ("Karthik Raman", "karthik.raman@college.edu", "24CSE099", "CSE", "9876543225", "2nd Year")
    ]

    # Register students across events
    for ev in all_events:
        ev_id = ev['id']
        category = ev['category']
        # Choose a random subset of students for each event
        num_students = random.randint(4, 11)
        selected_students = random.sample(sample_students, num_students)
        for s in selected_students:
            ticket = generate_ticket_code(category)
            cursor.execute("""
                INSERT OR IGNORE INTO registrations 
                (event_id, student_name, student_email, student_id, department, phone, year_of_study, ticket_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ev_id, s[0], s[1], s[2], s[3], s[4], s[5], ticket))

    # Add sample notifications
    notifications_data = [
        ("🎉 New Event Announced!", "InnovateX 2026 registration is officially live. Limited seats available in the computing labs!", "event", 1),
        ("🔔 Schedule Reminder", "GenAI Masterclass begins next week. Please bring laptops with Python 3.10+ installed.", "info", 2),
        ("🏆 Cultural Fest Auditions", "Registrations for Rhythm & Beats Battle of Bands will close 48 hours prior to the event.", "warning", 3),
        ("✅ Certificate Released", "Certificates for Cloud Native & DevOps Bootcamp are now available for registered participants.", "success", 7)
    ]
    for notif in notifications_data:
        cursor.execute("""
            INSERT INTO notifications (title, message, type, event_id)
            VALUES (?, ?, ?, ?)
        """, notif)

    # Sample feedback for completed events
    feedback_data = [
        (7, "Aarav Sharma", "CSE", 5, "Remarkable workshop! The hands-on Kubernetes cluster demo made industry practices crystal clear."),
        (7, "Sneha Patel", "IT", 4, "Extremely useful practical session. Would love an advanced part 2 on Istio service mesh."),
        (8, "Kavya Reddy", "AI & DS", 5, "Electrifying cultural evening! The audio-visual production and talent showcases were world class."),
        (8, "Divya Mehra", "MBA", 5, "Unbelievable energy and great coordination by the student volunteer council!")
    ]
    for fb in feedback_data:
        cursor.execute("""
            INSERT INTO feedback (event_id, student_name, department, rating, comments)
            VALUES (?, ?, ?, ?, ?)
        """, fb)

    conn.commit()

# Query Helper Functions

def get_dashboard_metrics():
    conn = get_db()
    cursor = conn.cursor()
    
    # Total counts
    cursor.execute("SELECT COUNT(*) as total_events FROM events")
    total_events = cursor.fetchone()['total_events']

    cursor.execute("SELECT COUNT(*) as total_registrations FROM registrations")
    total_registrations = cursor.fetchone()['total_registrations']

    cursor.execute("SELECT COUNT(*) as upcoming_events FROM events WHERE status = 'upcoming'")
    upcoming_events = cursor.fetchone()['upcoming_events']

    cursor.execute("SELECT COUNT(*) as completed_events FROM events WHERE status = 'completed'")
    completed_events = cursor.fetchone()['completed_events']

    # Category breakdown for charts
    cursor.execute("""
        SELECT e.category, COUNT(r.id) as reg_count, COUNT(DISTINCT e.id) as event_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.category
    """)
    category_stats = [dict(row) for row in cursor.fetchall()]

    # Department breakdown for charts
    cursor.execute("""
        SELECT department, COUNT(*) as count
        FROM registrations
        GROUP BY department
        ORDER BY count DESC
    """)
    dept_stats = [dict(row) for row in cursor.fetchall()]

    # Featured upcoming events (up to 4)
    cursor.execute("""
        SELECT e.*, COUNT(r.id) as registered_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        WHERE e.status = 'upcoming'
        GROUP BY e.id
        ORDER BY e.event_date ASC
        LIMIT 4
    """)
    featured_events = [dict(row) for row in cursor.fetchall()]

    # Recent notifications
    cursor.execute("""
        SELECT n.*, e.title as event_title
        FROM notifications n
        LEFT JOIN events e ON n.event_id = e.id
        ORDER BY n.created_at DESC
        LIMIT 6
    """)
    recent_notifications = [dict(row) for row in cursor.fetchall()]

    # Recent registrations activity
    cursor.execute("""
        SELECT r.*, e.title as event_title, e.category as event_category
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        ORDER BY r.registration_date DESC
        LIMIT 6
    """)
    recent_registrations = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'total_events': total_events,
        'total_registrations': total_registrations,
        'upcoming_events': upcoming_events,
        'completed_events': completed_events,
        'category_stats': category_stats,
        'dept_stats': dept_stats,
        'featured_events': featured_events,
        'recent_notifications': recent_notifications,
        'recent_registrations': recent_registrations
    }

def get_all_events(category=None, status=None, search=None):
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT e.*, COUNT(r.id) as registered_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        WHERE 1=1
    """
    params = []

    if category and category != 'All':
        query += " AND e.category = ?"
        params.append(category)

    if status and status != 'All':
        query += " AND e.status = ?"
        params.append(status)

    if search:
        query += " AND (e.title LIKE ? OR e.description LIKE ? OR e.venue LIKE ? OR e.organizer LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term, search_term])

    query += " GROUP BY e.id ORDER BY e.event_date ASC"

    cursor.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return events

def get_event_detail(event_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.*, COUNT(r.id) as registered_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        WHERE e.id = ?
        GROUP BY e.id
    """, (event_id,))
    event_row = cursor.fetchone()
    if not event_row:
        conn.close()
        return None

    event = dict(event_row)

    # Get participant list
    cursor.execute("""
        SELECT * FROM registrations
        WHERE event_id = ?
        ORDER BY registration_date DESC
    """, (event_id,))
    event['participants'] = [dict(row) for row in cursor.fetchall()]

    # Get feedback list
    cursor.execute("""
        SELECT * FROM feedback
        WHERE event_id = ?
        ORDER BY created_at DESC
    """, (event_id,))
    event['feedback'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return event

def create_event(title, category, description, event_date, event_time, venue, poster_url, capacity, organizer):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (title, category, description, event_date, event_time, venue, poster_url, capacity, organizer, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'upcoming')
    """, (title, category, description, event_date, event_time, venue, poster_url, capacity, organizer))
    new_id = cursor.lastrowid

    # Create notification
    cursor.execute("""
        INSERT INTO notifications (title, message, type, event_id)
        VALUES (?, ?, 'event', ?)
    """, (f"🎉 New Event: {title}", f"Registration is now open for {title} scheduled on {event_date} at {venue}.", new_id))

    conn.commit()
    conn.close()
    return new_id

def update_event(event_id, title, category, description, event_date, event_time, venue, poster_url, capacity, organizer, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE events
        SET title = ?, category = ?, description = ?, event_date = ?, event_time = ?,
            venue = ?, poster_url = ?, capacity = ?, organizer = ?, status = ?
        WHERE id = ?
    """, (title, category, description, event_date, event_time, venue, poster_url, capacity, organizer, status, event_id))
    conn.commit()
    conn.close()
    return True

def delete_event(event_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return True

def register_student(event_id, student_name, student_email, student_id, department, phone, year_of_study):
    conn = get_db()
    cursor = conn.cursor()

    # Verify event exists and check capacity
    cursor.execute("SELECT title, category, capacity, status FROM events WHERE id = ?", (event_id,))
    ev = cursor.fetchone()
    if not ev:
        conn.close()
        return False, "Selected event was not found."

    if ev['status'] == 'completed':
        conn.close()
        return False, "This event has already concluded. Registrations are closed."

    cursor.execute("SELECT COUNT(*) as cnt FROM registrations WHERE event_id = ?", (event_id,))
    reg_count = cursor.fetchone()['cnt']
    if reg_count >= ev['capacity']:
        conn.close()
        return False, f"Event capacity of {ev['capacity']} has been reached. Registrations are full!"

    # Check duplicate email
    cursor.execute("SELECT id FROM registrations WHERE event_id = ? AND student_email = ?", (event_id, student_email.strip().lower()))
    if cursor.fetchone():
        conn.close()
        return False, "This college email is already registered for this event."

    # Check duplicate student ID
    cursor.execute("SELECT id FROM registrations WHERE event_id = ? AND student_id = ?", (event_id, student_id.strip().upper()))
    if cursor.fetchone():
        conn.close()
        return False, "This Student ID is already registered for this event."

    ticket_code = generate_ticket_code(ev['category'])

    try:
        cursor.execute("""
            INSERT INTO registrations (event_id, student_name, student_email, student_id, department, phone, year_of_study, ticket_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (event_id, student_name.strip(), student_email.strip().lower(), student_id.strip().upper(), department, phone.strip(), year_of_study, ticket_code))
        
        # Add a notification
        cursor.execute("""
            INSERT INTO notifications (title, message, type, event_id)
            VALUES (?, ?, 'success', ?)
        """, (f"🎓 New Registration: {ev['title']}", f"{student_name} ({department}) secured pass {ticket_code}.", event_id))

        conn.commit()
        conn.close()
        return True, {
            'ticket_code': ticket_code,
            'student_name': student_name,
            'student_id': student_id.upper(),
            'department': department,
            'event_title': ev['title'],
            'category': ev['category']
        }
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, f"Duplicate registration detected: {str(e)}"
    except Exception as e:
        conn.close()
        return False, f"Error registering student: {str(e)}"

def get_all_participants(event_id=None, department=None, search=None):
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT r.*, e.title as event_title, e.category as event_category, e.event_date, e.venue
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE 1=1
    """
    params = []

    if event_id and str(event_id) != 'All':
        query += " AND r.event_id = ?"
        params.append(event_id)

    if department and department != 'All':
        query += " AND r.department = ?"
        params.append(department)

    if search:
        query += " AND (r.student_name LIKE ? OR r.student_email LIKE ? OR r.student_id LIKE ? OR r.ticket_code LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s])

    query += " ORDER BY r.registration_date DESC"

    cursor.execute(query, params)
    participants = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return participants

def add_event_feedback(event_id, student_name, department, rating, comments):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (event_id, student_name, department, rating, comments)
        VALUES (?, ?, ?, ?, ?)
    """, (event_id, student_name, department, rating, comments))
    conn.commit()
    conn.close()
    return True

def get_event_reports_data():
    conn = get_db()
    cursor = conn.cursor()

    # Event-wise stats
    cursor.execute("""
        SELECT e.id, e.title, e.category, e.event_date, e.capacity, e.status, e.venue,
               COUNT(r.id) as registered_count,
               ROUND(CAST(COUNT(r.id) AS FLOAT) / e.capacity * 100, 1) as fill_rate
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.id
        ORDER BY e.event_date ASC
    """)
    event_reports = [dict(row) for row in cursor.fetchall()]

    # Department-wise breakdown
    cursor.execute("""
        SELECT department, COUNT(*) as count
        FROM registrations
        GROUP BY department
        ORDER BY count DESC
    """)
    dept_reports = [dict(row) for row in cursor.fetchall()]

    # Category-wise breakdown
    cursor.execute("""
        SELECT e.category, COUNT(r.id) as reg_count, COUNT(DISTINCT e.id) as event_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.category
    """)
    category_reports = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        'events': event_reports,
        'departments': dept_reports,
        'categories': category_reports
    }
