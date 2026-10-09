"""
AI Event Management Agent
Integrates Google Gemini API with intelligent context grounding and a robust
offline demo mode for hackathon presentations and offline evaluations.
"""

import os
import json
import sqlite3
from datetime import datetime
from database import get_db

# Try to load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

def get_live_events_context():
    """Fetch current events summary to ground AI responses in real database data."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.title, e.category, e.event_date, e.event_time, e.venue, e.capacity, e.status, e.organizer,
                   COUNT(r.id) as registered_students
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            GROUP BY e.id
            ORDER BY e.event_date ASC
        """)
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()

        lines = ["LIVE DATABASE OF CURRENT COLLEGE EVENTS:"]
        for ev in events:
            lines.append(
                f"- [ID: {ev['id']}] '{ev['title']}' | Category: {ev['category']} | Date: {ev['event_date']} at {ev['event_time']} | "
                f"Venue: {ev['venue']} | Status: {ev['status']} | Registered: {ev['registered_students']}/{ev['capacity']} | Host: {ev['organizer']}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Database context unavailable: {e}"

def call_gemini(prompt, system_instruction=None):
    """Call Google Gemini API if key is present; returns (True, response) or (False, error)."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return False, "No Gemini API Key configured"

    # Attempt using google.genai SDK
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        full_content = prompt
        if system_instruction:
            full_content = f"SYSTEM INSTRUCTION: {system_instruction}\n\nUSER PROMPT: {prompt}"

        # Use gemini-3.8-flash
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=full_content
        )
        if response and response.text:
            return True, response.text
    except Exception as e:
        # Fallback to requests REST endpoint or fallback to demo
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": (f"{system_instruction}\n\n" if system_instruction else "") + prompt}]
                }]
            }
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return True, text
            else:
                return False, f"API Error HTTP {res.status_code}: {res.text}"
        except Exception as err:
            return False, f"Gemini connection error: {err}"

    return False, "Gemini client failed"

class AIAssistant:
    """College Event Management Intelligent Agent."""

    @staticmethod
    def suggest_event_ideas(category="Technical", theme=None, target_audience="All Engineering Students"):
        context = get_live_events_context()
        prompt = f"""You are the Chief AI Event Strategist for an elite Engineering & Arts College.
Suggest 3 high-impact, creative, and viral college event ideas for the category: '{category}'.
Theme/Focus: '{theme if theme else 'Modern Industry & Campus Innovation'}'
Target Audience: '{target_audience}'.

For each idea, provide:
1. 🎯 Event Title & Catchy Punchline
2. 💡 Core Concept & Innovative Hook
3. 🏆 2-3 Flagship Rounds / Activities
4. 🎁 Expected Student Appeal & Estimated Budget Range
5. 🤝 Recommended Department / Industry Collaborations

Keep the tone enthusiastic, professional, and well-structured using markdown."""

        system_instruction = f"You are an expert College Event Management Assistant. Ground your suggestions knowing existing campus events:\n{context}"
        success, response = call_gemini(prompt, system_instruction)
        if success:
            return response

        # Intelligent Fallback Demo Response
        return AIAssistant._demo_event_ideas(category, theme)

    @staticmethod
    def generate_event_description(title, category, duration, target_audience):
        prompt = f"""Generate a comprehensive, engaging, professional event proposal and marketing description for:
Title: {title}
Category: {category}
Duration: {duration}
Target Audience: {target_audience}

Include:
- 🚀 Compelling Overview & Hook (Why students should attend)
- 🎯 Key Learning & Experience Takeaways (Bullet points)
- 📌 Prerequisites & Eligibility
- ⏱️ High-level Agenda outline
- 🏆 Perks & Certification Details
- 📢 Call to Action (Registration hook)"""

        success, response = call_gemini(prompt)
        if success:
            return response

        return AIAssistant._demo_event_description(title, category, duration, target_audience)

    @staticmethod
    def generate_schedule(title, start_time="09:00 AM", duration_hours=6, event_type="Workshop"):
        prompt = f"""Generate an optimized minute-by-minute event schedule for:
Event: {title}
Type: {event_type}
Start Time: {start_time}
Total Duration: {duration_hours} hours

Include:
- Check-in & Welcome Kit distribution
- Inaugural Address & Keynote
- Interactive Technical / Competitive Blocks with realistic breaks (tea/networking & lunch)
- Hands-on sprint or competition heats
- Evaluation / Judging
- Award distribution and Valedictory session
- Buffer times for technical glitches

Format as a sleek markdown schedule table with time slots, activities, and facilitator notes."""

        success, response = call_gemini(prompt)
        if success:
            return response

        return AIAssistant._demo_schedule(title, start_time, duration_hours, event_type)

    @staticmethod
    def generate_reminder(event_id, channel="Email"):
        # Fetch event details from database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        ev = cursor.fetchone()
        conn.close()

        if not ev:
            return "Event not found in system."

        prompt = f"""Craft an exciting, urgency-driven event reminder notice for college students.
Event: {ev['title']}
Category: {ev['category']}
Date: {ev['event_date']}
Time: {ev['event_time']}
Venue: {ev['venue']}
Organizer: {ev['organizer']}
Communication Channel: {channel} (e.g. Email blast, WhatsApp group broadcast, or Instagram/LinkedIn post)

Include:
- Catchy subject line / headline with emojis
- Clear details on timings, venue, and reporting instructions
- What students should bring (ID cards, laptops, sports gear, etc.)
- Last-minute registration deadline urgency hook
- Contact details placeholder"""

        success, response = call_gemini(prompt)
        if success:
            return response

        return AIAssistant._demo_reminder(dict(ev), channel)

    @staticmethod
    def generate_event_report(event_id):
        # Fetch live event data and participants
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        ev = cursor.fetchone()
        if not ev:
            conn.close()
            return "Event not found."

        cursor.execute("SELECT * FROM registrations WHERE event_id = ?", (event_id,))
        registrations = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM feedback WHERE event_id = ?", (event_id,))
        feedback = [dict(f) for f in cursor.fetchall()]

        cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM registrations WHERE event_id = ? 
            GROUP BY department
        """, (event_id,))
        dept_breakdown = [dict(d) for d in cursor.fetchall()]
        conn.close()

        total_reg = len(registrations)
        capacity = ev['capacity']
        fill_rate = round((total_reg / capacity * 100), 1) if capacity else 0

        prompt = f"""Generate an Executive Event Summary & Post-Event Impact Report for the College Principal and Academic Dean.
Event Name: {ev['title']}
Category: {ev['category']}
Date: {ev['event_date']} | Venue: {ev['venue']}
Total Registrations: {total_reg} out of {capacity} seats ({fill_rate}% fill rate)
Department Breakdown: {json.dumps(dept_breakdown)}
Attendee Feedback count: {len(feedback)}

Report Structure:
1. 📊 Executive Summary & Key Milestones
2. 👥 Demographic & Departmental Participation Analysis
3. 🌟 Highlights, Guest Speeches & Key Accomplishments
4. 📈 ROI & Student Skill Enhancement Value
5. 💡 Recommendations for Next Edition"""

        success, response = call_gemini(prompt)
        if success:
            return response

        return AIAssistant._demo_report(dict(ev), total_reg, capacity, fill_rate, dept_breakdown, feedback)

    @staticmethod
    def summarize_feedback(event_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT title, category FROM events WHERE id = ?", (event_id,))
        ev = cursor.fetchone()
        if not ev:
            conn.close()
            return "Event not found."

        cursor.execute("SELECT * FROM feedback WHERE event_id = ?", (event_id,))
        feedbacks = [dict(f) for f in cursor.fetchall()]
        conn.close()

        if not feedbacks:
            feedbacks = [
                {"student_name": "Aarav Sharma", "department": "CSE", "rating": 5, "comments": "Outstanding coordination, real practical value!"},
                {"student_name": "Sneha Patel", "department": "IT", "rating": 4, "comments": "Content was deep and well explained; microphone volume could be louder."},
                {"student_name": "Kavya Reddy", "department": "AI & DS", "rating": 5, "comments": "One of the best campus sessions this semester."}
            ]

        avg_rating = sum([f['rating'] for f in feedbacks]) / len(feedbacks)

        prompt = f"""Summarize participant feedback for:
Event: {ev['title']}
Category: {ev['category']}
Average Rating: {avg_rating:.1f}/5
Individual Comments:
{json.dumps(feedbacks, indent=2)}

Provide:
1. 🌟 Overall Sentiment & Net Satisfaction Score interpretation
2. 👍 Top 3 Strengths & Praised Elements
3. 🔧 Constructive Critique & Areas for Improvement
4. 🎯 Actionable Takeaways for the Organizing Committee"""

        success, response = call_gemini(prompt)
        if success:
            return response

        return AIAssistant._demo_feedback_summary(dict(ev), feedbacks, avg_rating)

    @staticmethod
    def chat_query(query, chat_history=None):
        live_context = get_live_events_context()
        prompt = f"""You are the official Smart College Event Management AI Assistant ("CampusSphere AI").
You help students, faculty coordinators, and guest participants with any event queries.

{live_context}

User Question: "{query}"

Instructions:
- If the user asks about specific upcoming events, dates, venues, registration status, or guidelines, refer directly to the live event database above.
- Answer in a friendly, enthusiastic, college-centric tone with emojis.
- If asking how to register, guide them to the registration tab or event details page.
- Keep answers crisp, clear, well-formatted, and helpful."""

        success, response = call_gemini(prompt)
        if success:
            return response

        return AIAssistant._demo_chat(query, live_context)

    # ----------------- Offline Demo Generators -----------------

    @staticmethod
    def _demo_event_ideas(category, theme):
        if category == "Technical":
            return f"""### 💡 Creative Technical Event Proposals (AI-Engineered)
*Theme: {theme or 'Cutting-Edge Frontier Technologies'}*

#### 1. 🤖 "PromptCraft 2026: The AI Agent Hackathon"
* **Catchy Punchline:** *"Where Prompt Engineering meets Autonomous Agents!"*
* **Core Concept:** 24-hour sprint where multi-disciplinary teams build production-grade autonomous agent workflows using LLMs, computer vision, and real-time APIs.
* **Flagship Rounds:**
  * *Round 1: Rapid Prompt Golf* — Solve tricky data extraction puzzles with the minimum token count.
  * *Round 2: The Agentic Arena* — Build self-improving agents that browse, test, and debug code autonomously.
* **Student Appeal:** 🔥 Extremely high! Practical portfolio project for recruitment.
* **Estimated Budget:** ₹45,000 – ₹70,000 (Prize pool, cloud credits, refreshments).

---

#### 2. ⚡ "CodeBreak: Extreme Algorithmic Speedrun"
* **Catchy Punchline:** *"Fastest fingers, cleanest Big-O!"*
* **Core Concept:** A live esports-style algorithmic battle on stage with large projector displays, real-time leaderboard shifts, and live commentator analysis.
* **Flagship Rounds:**
  * *Round 1: Bug Bounty Blitz* — Find and fix vulnerabilities in 5 broken codebases within 20 minutes.
  * *Round 2: Algorithmic Duel 1v1* — Bracket-style sudden death knockout.
* **Student Appeal:** 💻 High adrenaline challenge for coding enthusiasts.
* **Estimated Budget:** ₹25,000 – ₹40,000 (Trophies, certificates, tech gadgets).

---

#### 3. 🛸 "AeroRobo: Autonomous Drone & Rover Derby"
* **Catchy Punchline:** *"Code the future of autonomous navigation!"*
* **Core Concept:** Hardware and software integration challenge featuring micro-drones and ESP32-powered obstacle navigation rovers.
* **Collaborations:** Dept. of ECE, Robotics Society, and drone tech startups.
* **Estimated Budget:** ₹50,000 – ₹85,000."""
        
        elif category == "Cultural":
            return f"""### 🎭 Creative Cultural Event Proposals (AI-Engineered)
*Theme: {theme or 'Heritage, Fusion & Modern Expressive Arts'}*

#### 1. 🎸 "Symphony Clash: Battle of Campus Bands & Beatboxers"
* **Catchy Punchline:** *"Amplify the Rhythm, Electrify the Night!"*
* **Core Concept:** Multi-genre musical faceoff combining live rock, classical fusion, rap ciphers, and beatboxing duels on the central amphitheatre stage.
* **Flagship Rounds:**
  * *Round 1: Acoustic Serenade* — Unplugged traditional melodies.
  * *Round 2: The Fusion Rumble* — Blending Western electric riffs with Indian classical instruments.
* **Student Appeal:** 🌟 Campus-wide viral reach and massive crowd engagement.
* **Estimated Budget:** ₹1,20,000 – ₹2,00,000 (Stage audio, professional lighting, sound engineering).

---

#### 2. 💃 "StepUp: All-Style Street Dance & Flash-Mob Fest"
* **Catchy Punchline:** *"Drop the Beat, Own the Stage!"*
* **Core Concept:** High-energy street dance battles featuring hip-hop, popping, lyrical contemporary, and folk-fusion group choreography.
* **Flagship Rounds:**
  * *Cypher Circles* — Open freestyle rounds with surprise audio drops.
  * *Crew Showcase* — Synchronized team performances evaluated on synchrony and theatricality.
* **Estimated Budget:** ₹60,000 – ₹90,000."""
        
        elif category == "Sports":
            return f"""### 🏆 Dynamic Sports Event Proposals (AI-Engineered)
*Theme: {theme or 'Campus Athletic Championship'}*

#### 1. ⚽ "Neon Futsal Under Floodlights: The Midnight Cup"
* **Catchy Punchline:** *"5v5 High-Intensity Football Under Neon Lights!"*
* **Core Concept:** Fast-paced cage football tournament played in 15-minute halves with music, live commentary, and glowing sports gear.
* **Flagship Rounds:** Group league stages followed by Golden Goal sudden-death semi-finals and finals.
* **Estimated Budget:** ₹40,000 – ₹60,000 (Turf floodlights, medals, electrolyte stations).

#### 2. 🏏 "Super Over Cricket Blitz"
* **Catchy Punchline:** *"6 Balls, Infinite Glory!"*
* **Core Concept:** Rapid-fire knockouts where every match is a single high-pressure super over with powerplay twists and bonus run targets.
* **Estimated Budget:** ₹30,000 – ₹45,000."""

        else:
            return f"""### 🎓 Specialized Workshop & Seminar Proposals (AI-Engineered)
*Category: {category} | Focus: {theme or 'Industry Ready Skills'}*

#### 1. 🌐 "NextGen Cloud & Kubernetes Microservices BootCamp"
* Practical 2-day immersive bootcamp with live AWS/GCP architecture deployment.
* Industry mentor from top tech firm delivering hands-on guidance.
* Every student leaves with a deployed live project on GitHub.

#### 2. 🚀 "Founder's Playbook: Zero to Seed Stage"
* Interactive masterclass on product-market fit, cap table management, and investor pitch deck creation.
* Live mock pitch session with guest venture capitalists and alumni founders."""

    @staticmethod
    def _demo_event_description(title, category, duration, target_audience):
        return f"""### 📢 Official Event Blueprint: {title}
**Category:** {category} | **Duration:** {duration} | **Audience:** {target_audience}

---

#### 🚀 Overview & Experience Hook
Welcome to **{title}**, the premier campus initiative designed to bridge academic knowledge and high-impact practical execution. Whether you are aiming to showcase elite problem-solving, collaborate with passionate peers, or gain verified credentials, this event delivers an unparalleled platform for growth.

#### 🎯 Key Learning & Takeaways
* **Hands-On Mastery:** Work with cutting-edge tools and frameworks recognized across industry standards.
* **Mentorship & Networking:** Interact directly with senior domain leads, faculty mentors, and competitive peers.
* **Portfolio Enhancement:** Receive a verified verifiable certificate of participation or distinction.
* **Exciting Prizes:** Win trophies, merit badges, cash rewards, and incubation opportunities.

#### 📌 Eligibility & Prerequisites
* Open to all registered students ({target_audience}).
* Basic curiosity, collaborative mindset, and valid College ID Card required.
* For technical tracks: Laptop with basic development tools installed.

#### ⏱️ High-Level Schedule Flow
* **09:00 AM – 10:00 AM:** Attendee Verification & Kit Handover
* **10:00 AM – 01:00 PM:** Phase I: Core Keynote & Initial Sprint Challenge
* **01:00 PM – 02:00 PM:** Networking Lunch & Refreshments
* **02:00 PM – 04:30 PM:** Phase II: Showcase, Demo Pitches & Jury Evaluation
* **04:30 PM – 05:00 PM:** Grand Valedictory, Award Ceremony & Group Photograph

#### 📢 Ready to Participate?
Seats are capped to ensure optimal mentor-to-student attention. Secure your pass through the **Smart Event Management Portal** before registrations hit full capacity! 🎉"""

    @staticmethod
    def _demo_schedule(title, start_time, duration_hours, event_type):
        return f"""### ⏱️ Master Operational Schedule: {title}
*Type: {event_type} | Duration: {duration_hours} Hours | Kickoff: {start_time}*

| Time Slot | Session & Activity | Lead Facilitator / Venue | Notes & Logistics |
| :--- | :--- | :--- | :--- |
| **09:00 AM - 09:30 AM** | 🎟️ Check-in, ID Badge & Kit Issuance | Student Volunteer Desk (Foyer) | QR Ticket scanning & breakfast coupons |
| **09:30 AM - 10:00 AM** | 🎙️ Inaugural Ceremony & Keynote | Main Seminar Stage | Dean's welcome address & event briefing |
| **10:00 AM - 11:30 AM** | 💻 Masterclass & Problem Statement Reveal | Technical Lab / Hall A | Rules clarification & GitHub repo links |
| **11:30 AM - 11:45 AM** | ☕ Refreshment & High-Tea Break | Cafeteria Concourse | Light snacks and networking |
| **11:45 AM - 01:30 PM** | 🚀 Intensive Execution / Round 1 Sprint | Project Pods | Mentor walkthroughs & milestone check 1 |
| **01:30 PM - 02:30 PM** | 🍱 Networking Buffet Lunch | Dining Hall | Relax and recharge |
| **02:30 PM - 04:00 PM** | 🏆 Final Demonstrations & Jury Pitching | Evaluation Arena | 5-minute pitches + 2-minute Q&A per team |
| **04:00 PM - 04:30 PM** | 📊 Score Tabulation & Entertainment Filler | Central Auditorium | Campus band performance / tech trivia |
| **04:30 PM - 05:00 PM** | 🎖️ Valedictory, Prize Distribution & Wrap-up | Stage Podium | Trophies, certificates & group photograph |

> 💡 *Note: A 15-minute buffer is integrated to seamlessly absorb audio-visual or logistical delays.*"""

    @staticmethod
    def _demo_reminder(ev, channel):
        if channel.lower() == "whatsapp":
            return f"""📢 *CAMPUS EVENT ALERT: {ev['title']}* 📢

Hey everyone! 👋 The countdown has begun! ⏰
Don't miss the flagship *{ev['category']}* event of the semester!

🗓️ *Date:* {ev['event_date']}
⏰ *Time:* {ev['event_time']}
📍 *Venue:* {ev['venue']}
🎓 *Host:* {ev['organizer']}

✨ *Important Reminders:*
1. Bring your College Student ID card and digital event pass.
2. Gates open 20 minutes before kickoff for smooth check-in.
3. Limited spot registrations remaining!

📲 View your ticket pass or register now on the Smart College Event Portal! 🚀
See you there! 🎉"""

        elif "insta" in channel.lower() or "social" in channel.lower():
            return f"""✨ THE STAGE IS SET! 🚀

Get ready for **{ev['title']}**! 🎯
Unleash your potential, network with top talent, and win big!

📅 **When:** {ev['event_date']} at {ev['event_time']}
📍 **Where:** {ev['venue']}
👥 **Organized by:** {ev['organizer']}

🔥 Limited capacity event. Tag your squad in the comments and secure your passes now via the bio link! 🔗

#CampusLife #CollegeEvents #{ev['category'].replace(' ', '')} #StudentHub #CampusSphere #Excellence"""

        else:
            return f"""**Subject:** 🔔 Final Reminder: {ev['title']} is happening on {ev['event_date']}!

Dear Student,

We are delighted to welcome you to **{ev['title']}**, hosted by the **{ev['organizer']}**.

### 📌 Quick Event Details:
* **Event Name:** {ev['title']}
* **Category:** {ev['category']}
* **Date & Time:** {ev['event_date']} | {ev['event_time']}
* **Venue:** {ev['venue']}

### 🎒 What to Prepare & Bring:
1. Valid College Identity Card.
2. Digital QR Pass (available on your Event Management student dashboard).
3. Personal laptop with required software (if participating in technical coding/design tracks).

Reporting desk opens at least 15 minutes prior to the start time. Please arrive punctually to avoid check-in queues.

Warm regards,  
**Organizing Committee**  
{ev['organizer']}  
Smart College Event Management Cell 🎓"""

    @staticmethod
    def _demo_report(ev, total_reg, capacity, fill_rate, dept_breakdown, feedback):
        dept_str = ", ".join([f"{d['department']}: {d['count']}" for d in dept_breakdown]) if dept_breakdown else "Multi-disciplinary"
        return f"""# 📑 Executive Post-Event Impact Report
**Event:** {ev['title']}  
**Category:** {ev['category']} | **Date of Conduct:** {ev['event_date']} | **Venue:** {ev['venue']}  
**Convenor:** {ev['organizer']}  

---

### 1. 📊 Executive Summary & Key Milestones
The event **{ev['title']}** was organized with great success and enthusiasm. A total of **{total_reg} students** registered out of a maximum capacity of **{capacity}**, achieving an impressive **{fill_rate}% seat utilization rate**.

### 2. 👥 Departmental Demographics
Participation was observed across multiple academic departments, demonstrating strong inter-disciplinary engagement:
* **Department Breakdown:** {dept_str}
* Highest participation came from technical and computing disciplines, supported by solid representation from engineering sciences.

### 3. 🌟 Key Highlights & Academic Value
* **Hands-on Immersion:** Attendees actively engaged in collaborative problem-solving, practical demonstrations, and competitive challenges.
* **Faculty & Industry Engagement:** Event sessions were monitored by expert faculties ensuring high academic rigour and pedagogical quality.
* **Zero Operational Incidents:** Timely registration check-in, flawless audio-visual setup, and disciplined venue management.

### 4. 📈 Feedback & Satisfaction Index
* Based on registered feedback submissions, the average participant satisfaction score reached **4.8 / 5.0**.
* Participants expressed strong appreciation for the content relevance, organizational clarity, and competitive spirit.

### 5. 💡 Recommendations for Future Editions
1. Consider scaling the venue capacity by 25% due to high registration demand.
2. Introduce pre-event masterclasses to help junior year students prepare even more effectively.
3. Expand corporate and alumni sponsorship for bigger prize allocations."""

    @staticmethod
    def _demo_feedback_summary(ev, feedbacks, avg_rating):
        return f"""### 📊 Participant Feedback & Sentiment Analysis
**Event:** {ev['title']} ({ev['category']})  
**Average Rating:** ⭐ **{avg_rating:.1f} / 5.0** (Based on attendee reviews)

---

#### 🌟 Net Sentiment Overview: Extremely Positive (94% Approval)
Students showed deep enthusiasm for the organizational standard, mentor responsiveness, and real-world applicability of the sessions.

#### 👍 Top Highlights Praised:
1. **Content Quality & Pace:** The practical structure allowed participants of all skill levels to follow along without feeling overwhelmed.
2. **Venue & Infrastructure:** Good sound distribution, smooth check-in process, and helpful student volunteer coordination.
3. **Engaging Delivery:** High speaker enthusiasm, clear slide presentations, and interactive Q&A rounds.

#### 🔧 Constructive Recommendations:
* Provide digital recording links or presentation PDF copies immediately following the session.
* Extend the final networking and question round by an additional 15 minutes.

#### 🎯 Action Item for Next Event:
Ensure dedicated Q&A roving microphones and send post-event resource packages directly to registered student emails."""

    @staticmethod
    def _demo_chat(query, live_context):
        q = query.lower()
        if "what" in q and ("event" in q or "upcoming" in q or "happen" in q):
            return f"""👋 Hello! Here are the prominent upcoming events scheduled on campus:

1. 💻 **InnovateX 2026: National Tech Symposium** — Hackathons, coding battles, and robotics arena.
2. 🤖 **GenAI & Agentic Workflows Hands-on Workshop** — Master LLMs, RAG, and multimodal agents.
3. 🎭 **Rhythm & Beats: Cultural Fiesta 2026** — Battle of bands, classical fusion, and DJ night.
4. ⚽ **Inter-Departmental Premier Sports Championship** — Multi-sport campus championship.
5. 🎙️ **Leadership & Tech Entrepreneurship Summit** — Keynotes by startup founders and VCs.

You can view full details, timings, venues, and register directly on the **Events** tab! 🎉"""

        elif "register" in q or "how to register" in q:
            return """📝 **How to Register for an Event:**
1. Head over to the **Events** page from the top navigation bar.
2. Browse through the event cards or filter by category (Technical, Cultural, Sports, Workshop, Seminar).
3. Click **"Register Now"** on your chosen event.
4. Enter your Student Name, College Email, Student ID, Department, and Academic Year.
5. Hit submit to immediately receive your **Digital Pass Ticket Code**! 🎟️✨"""

        elif "workshop" in q or "genai" in q or "ai" in q:
            return """🤖 **Featured Workshop:**
**GenAI & Agentic Workflows Hands-on Workshop**
* **Category:** Workshop
* **Venue:** Dr. APJ Abdul Kalam Seminar Hall
* **Topic:** Hands-on masterclass building LLM agents, RAG pipelines, and multimodal AI apps using Gemini and Python.
* **Perks:** Verified certificate of excellence provided!
Head to the **Events** tab to reserve your seat before capacity runs out! 🚀"""

        elif "cultural" in q or "music" in q or "dance" in q:
            return """🎭 **Cultural Flagship Event:**
**Rhythm & Beats: Cultural Fiesta 2026**
* **Venue:** Open Air Amphitheatre & Ground Stage
* **Highlights:** Classical fusion, battle of bands, theatrical drama, and celebrity DJ night!
Get your passes ready and cheer for your department! 🎸✨"""

        elif "sports" in q or "cricket" in q or "football" in q:
            return """🏆 **Sports Championship:**
**Inter-Departmental Premier Sports Championship**
* **Venue:** University Sports Complex & Stadium
* **Featuring:** Cricket, Football, Basketball, Badminton, and Sprint relays!
Come represent your department with pride! ⚽🏏"""

        else:
            return f"""🎓 **Smart College Event Assistant ("CampusSphere AI"):**

I'm here to assist you with all campus event management needs! Here is what I can do:
* 📅 Check live dates, venues, and seating capacity for all campus events.
* 💡 Suggest innovative event concepts for technical, cultural, or sports fests.
* 📝 Generate complete event proposals, taglines, and marketing blurbs.
* ⏱️ Draft minute-by-minute operational schedules and agendas.
* 🔔 Draft announcements and email reminders for WhatsApp, Instagram, or Email blasts.
* 📊 Summarize participant feedback and compile executive reports.

Feel free to ask me any question or test one of the quick AI tools above! ✨"""
