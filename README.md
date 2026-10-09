# 🎓 CampusSphere AI — Smart College Event Management Agent

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-Analytics-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-3.8%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

A colourful, production-ready **Smart College Event Management Agent** platform for managing campus events, student registrations, real-time analytics, and autonomous AI-assisted event workflows.

---

## 🎨 1. Key Highlights & Features

### 💜 Modern UI / UX Design
* **Vibrant Aesthetic:** Purple (`#6C5CE7`), Pink (`#FD79A8`), and Electric Blue (`#0984E3`) gradients.
* **Glassmorphic Elements:** Frosted-glass navigation, rounded cards (`border-radius: 20px`), micro-interactions, and soft elevation shadows.
* **Dual Theme:** Instant Dark Mode 🌙 and Light Mode ☀️ with persistent `localStorage` synchronization.
* **Dynamic Media:** High-definition posters curated for Technical Symposiums, Hackathons, Cultural Fests, Sports Meets, Workshops, and Leadership Seminars.
* **Fully Responsive:** Optimized across desktop, tablet, and mobile displays.

### 🏠 2. Dynamic Dashboard
* **Real-time Stat Cards:** Total Events, Verified Student Passes, Upcoming Events, and Concluded Events.
* **Interactive Chart.js Visualizations:**
  * 🍩 *Category Distribution Donut Chart* (Technical, Cultural, Sports, Workshop, Seminar).
  * 📊 *Department Participation Bar Chart* (CSE, AI & DS, ECE, IT, MECH, CIVIL, MBA).
* **Featured Events Carousel / Grid:** Quick register shortcuts, seat occupancy bars.
* **Live Activity & Bulletin Streams:** Verified student pass generations and urgent campus announcements.

### 📅 3. Full Event Management (CRUD)
* **Create Events:** Event Title, Category, Description, Date, Time, Venue, Seating Capacity, Organizer, and Poster URL.
* **Edit & Update:** Change schedules, venue, or mark status as Upcoming or Completed.
* **Delete with Safety Guard:** Confirmation modal with cascade deletion.
* **Live Filtering & Search:** Instant search by keywords and filter pills by category and status.

### 👥 4. Student Registration & Digital Pass Generator
* **Registration Form:** Collects Student Name, College Email, Roll/Student ID, Department, Contact Phone, and Year of Study.
* **Zero Duplicate Policy:** Automatic dual constraint checking: prevents duplicate registrations with the same Email or Student ID for the same event.
* **Digital Ticket Pass:** Generates a custom ticket code (e.g., `PASS-TECH-9821`), with print/save support and clipboard copying.

### 🤖 5. Autonomous AI Event Management Agent
Powered by **Google Gemini 3.8 Flash** with an **Intelligent Offline Demo Engine**:
1. 💡 **Suggest Event Ideas:** Generates 3 creative proposals with punchlines, rounds, appeal, and budget ranges.
2. 📝 **Generate Marketing Descriptions:** Formats full event proposals with learning outcomes, prerequisites, and calls-to-action.
3. 🗓️ **Minute-by-Minute Schedules:** Generates detailed operational schedules with inaugurations, keynote sessions, breaks, and valedictories.
4. 🔔 **Reminder & Broadcast Generator:** Drafts targeted copy for Email Blasts, WhatsApp Groups, and Instagram posts.
5. 📑 **Executive Impact Reports:** Generates post-event audits for College Principals and Deans with seat utilization metrics and department breakdowns.
6. 📊 **Feedback & Sentiment Analysis:** Synthesizes attendee star ratings and comments into strengths and recommendations.
7. 💬 **Context-Grounded Interactive Chat:** AI assistant directly answers student queries using live data from the SQLite database.

### 📈 6. Reports & Data Exports
* **Live Capacity Tracking:** Calculates real-time seat fill rate percentages.
* **One-Click CSV Exports:**
  * `export/events.csv`: Summary of events, capacity, registrations, and fill rates.
  * `export/participants.csv`: Detailed roster of attendees with ticket pass codes.

---

## 📂 Project Structure

```
college-event-agent/
│
├── app.py                     # Flask web server, page routes & REST API endpoints
├── database.py                # SQLite connection, schema, seed data, and helper queries
├── ai_agent.py                # Gemini 3.8 Flash integration & offline demo fallback engine
├── database.db                # SQLite database (auto-created on startup)
├── requirements.txt           # Python package dependencies
├── .env.example               # Environment variables template
├── .env                       # Local environment configuration
├── .gitignore                 # Git ignore rules
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern CSS with purple/blue/pink gradients & dark mode
│   └── js/
│       ├── main.js            # Theme toggle, global toasts, notification helpers
│       ├── dashboard.js       # Chart.js initialization & dynamic chart updates
│       ├── events.js          # Event filtering, search, modal creation, edit, & delete
│       ├── registration.js    # Student registration & digital ticket modal
│       ├── reports.js         # Report analytics charts
│       └── ai_assistant.js    # AI chat & 6 specialized generator tools
│
└── templates/
    ├── base.html              # Core layout (navbar, theme toggle, modals, footer)
    ├── index.html             # Dashboard with stats, charts, & featured events
    ├── events.html            # Event catalog with filters, search, and CRUD modals
    ├── event_detail.html      # Event details, participant list, and feedback
    ├── register.html          # Student pass registration page & digital ticket
    ├── participants.html      # Participant directory & search
    ├── reports.html           # Executive analytics & CSV export center
    └── ai_agent.html          # AI Event Management Agent Hub & 6 Power Tools
```

---

## ⚡ Quick Start & Terminal Commands

### 1. Open Terminal in VS Code
Open the project directory in VS Code or your terminal:
```bash
cd C:\Users\nprhp\.gemini\antigravity\scratch\college-event-agent
```

### 2. Verify / Install Dependencies
The required packages (`Flask`, `google-genai`, `requests`, `python-dotenv`) are listed in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
```

### 3. Configure the AI API Key (Optional)
The system contains an intelligent offline fallback engine, meaning **it works out of the box even without an API key**!

To enable live Google Gemini AI generation:
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Open `.env` and set:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   FLASK_SECRET_KEY=smart_college_secret_key
   PORT=5000
   ```

### 4. Run the Application
Execute the following command in your terminal:
```bash
python app.py
```

### 5. Access the Web Application
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🎓 College Presentation & Demonstration Guide

Follow this step-by-step walkthrough during your evaluation:

### 🌟 Step 1: The Modern Dashboard
* Show the vibrant **Purple, Pink, and Blue gradient theme**.
* Click the **Moon / Sun icon** in the top navigation bar to toggle **Dark Mode** and **Light Mode** seamlessly.
* Point out the **4 Stat Cards** (Total Events, Registered Students, Upcoming, Completed).
* Review the **Category Donut Chart** and **Department Participation Bar Chart**.

### 📅 Step 2: Event Management & CRUD
* Navigate to the **Events** tab.
* Test the **Category Filter Pills** (Technical, Cultural, Sports, Workshop, Seminar).
* Use the **Search bar** to search for "Hackathon" or "AI".
* Click **"+ Host New Event"** to show the live creation modal with automated royalty-free poster preview.
* Demonstrate the **Edit Event** and **Delete Event** options under the actions dropdown.

### 🎟️ Step 3: Registration & Duplicate Prevention
* Open the **Register** tab or click **"Register"** on any event.
* Fill in student details: Name, Email, Student ID, and Department.
* Submit the form: Watch the **Digital Ticket Pass** modal pop up with ticket code (e.g. `PASS-TECH-XXXXX`).
* Click **"Copy Pass Code"** to test the clipboard copy toast.
* **Test Duplicate Prevention:** Try submitting the same email or Student ID for the same event again. The system catches the collision and displays a clear warning message!

### 🤖 Step 4: The AI Event Management Agent Hub
* Navigate to the **AI Assistant** tab.
* **Demonstrate Live Conversational Chat:**
  * Click one of the quick starter pills or type: *"What events are scheduled for next week?"*
  * Notice how the AI references real events stored in your SQLite database!
* **Demonstrate the 6 AI Generators in the Power Tools Studio:**
  1. *Suggest Event Ideas:* Generate 3 proposals for a Technical or Cultural fest.
  2. *Generate Description:* Create a proposal for a new hackathon.
  3. *Minute-by-Minute Schedule:* Build a schedule table for a 6-hour workshop.
  4. *Reminder Notice:* Generate a WhatsApp broadcast copy for an upcoming event.
  5. *Executive Impact Report:* Produce an executive audit for the College Principal.
  6. *Feedback Summary:* Synthesize attendee ratings and feedback.

### 📊 Step 5: Reports & CSV Export
* Open the **Reports** tab.
* Review the **Fill Rate progress bars** and KPI cards.
* Click **"Export All Participants CSV"** or **"Export Events Summary CSV"** to demonstrate downloadable spreadsheets for administrative record-keeping.

---

## 🔒 Security & Best Practices
* **No hardcoded secrets:** API keys and secret keys are managed through `.env`.
* **Database Safety:** Uses SQLite parameterized SQL queries (`?`) to prevent SQL injection vulnerabilities.
* **Duplicate Prevention:** SQLite unique constraints on `(event_id, student_email)` and `(event_id, student_id)`.
* **Zero Failure Grace:** If Gemini API is unreachable or rate-limited, the system automatically falls back to the rich demo generator without breaking the user experience.

---

## 🏆 Summary Checklist
* [x] Purple, blue, pink gradient theme with dark mode
* [x] Responsive layout with Bootstrap 5
* [x] Dashboard with Chart.js charts and stat cards
* [x] Event Management (Create, Edit, Delete, Filter, Search)
* [x] Student Registration with ticket passes & duplicate checks
* [x] Participant Directory & search
* [x] 6-Tool AI Event Management Agent with Gemini & Fallback
* [x] Context-aware AI queries grounded in SQLite database
* [x] CSV Exports for participants and events
* [x] Comprehensive documentation and presentation guide
