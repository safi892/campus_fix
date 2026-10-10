# CampusFix AI

**Intelligent University Campus Maintenance & Issue Tracking Application**

CampusFix AI helps university maintenance departments manage student reports effectively. When multiple students report the same problem (such as a broken AC in a lecture hall), CampusFix AI clusters duplicate reports, escalates urgent safety hazards, and keeps staff in full control.

---

## Prerequisites

- **Python 3.11** (Recommended for compatibility with future ML dependencies)
- **macOS / Linux / Windows WSL**
- **Git**

---

## Quick Setup & Run

### 1. Open Terminal and Navigate to the Project
```bash
cd /Volumes/Data/hackthon
```

### 2. Activate the Virtual Environment
```bash
source /Volumes/Data/hackthon/.venv/bin/activate
```
*(If on Windows command prompt: `.venv\Scripts\activate`)*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
python app.py
```
By default, the application runs on **http://127.0.0.1:5001** (Port 5001 is used to avoid macOS AirPlay Receiver conflicts on port 5000).

---

## Verification & Testing

Once the server is running:

1. **Landing Page**: Open your browser and visit:
   ```
   http://127.0.0.1:5001/
   ```
   You should see the responsive CampusFix AI landing page with navigation, features, and system status.

2. **Health Check Route**: Open your browser or run:
   ```bash
   curl http://127.0.0.1:5001/health
   ```
   Expected response:
   ```json
   {
     "app": "CampusFix AI",
     "message": "CampusFix AI core service is running smoothly.",
     "milestone": 1,
     "status": "healthy",
     "version": "0.1.0"
   }
   ```

---

## Project Structure (Milestone 1)

```
hackthon/
├── .gitignore             # Ignored files (virtualenv, cache, sqlite dbs)
├── requirements.txt       # Python package dependencies
├── README.md              # Setup and verification instructions
├── app.py                 # Flask application entry point & routes
├── static/
│   └── css/
│       └── style.css      # Custom styling and design tokens
└── templates/
    ├── base.html          # Shared layout with Bootstrap 5 navbar & footer
    └── index.html         # Responsive landing page
```

---

## Hackathon Working Rules & Roadmap

- **Rule 1:** Graceful degradation — If ML libraries fail to load, core ticket reporting and search continue working.
- **Rule 2:** Zero record deletion — Duplicate clusters never delete original student submissions.
- **Rule 3:** Human-in-the-loop — Staff confirm or reject AI similarity groupings.
- **Milestone 1 (Complete):** Core Flask setup, responsive landing page, health check.
- **Milestone 2 (Next):** Student complaint submission form, input validation, and SQLite database storage.
- **Milestone 3 (Planned):** Sentence-transformer embeddings (`all-MiniLM-L6-v2`), duplicate clustering, and staff dashboard.
