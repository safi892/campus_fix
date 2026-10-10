# TASK: Implement Milestone 2 for CampusFix AI (Database, Complaint Flow & Seed Data)

You are continuing development on **CampusFix AI**, an intelligent university maintenance complaint and deduplication system. 

Before writing any code, inspect the codebase and read the architectural rules in `.ai/context.md`, `.ai/rules.md`, `.ai/database.md`, and `.ai/security.md`.

---

## 1. What is Already Built & Working (DO NOT BREAK THIS)
* Python 3.11 virtual environment in `.venv/`.
* Flask app entry point in `app.py` with `/` (landing page) and `/health` (health check).
* Bootstrap 5 shared layout in `templates/base.html` and styles in `static/css/style.css`.
* Offline semantic ML engine in `ml.py` using `models/all-MiniLM-L6-v2/` on CPU (with Scikit-Learn TF-IDF fallback and regex safety scanner). Verified working.

---

## 2. Your Goal in Milestone 2
Build the complete student complaint submission, SQLite database storage, issue tracking receipt, and realistic demo seed script.

---

## 3. Detailed Implementation Requirements

### A. SQLite Database Helper (`db.py`)
1. Create `db.py` to manage SQLite connections with `sqlite3.Row` factory. Store database file in `instance/campusfix.db`.
2. Initialize table `complaints` matching `.ai/database.md`:
   - `id` INTEGER PRIMARY KEY AUTOINCREMENT
   - `reference_code` TEXT UNIQUE NOT NULL (e.g. `CFX-2026-9041`)
   - `title` TEXT NOT NULL
   - `description` TEXT NOT NULL
   - `building` TEXT NOT NULL
   - `room` TEXT
   - `category` TEXT NOT NULL ('HVAC', 'Electrical', 'Plumbing', 'Furniture', 'Cleanliness', 'Safety')
   - `urgency` TEXT NOT NULL DEFAULT 'Normal' ('Critical', 'High', 'Normal', 'Low')
   - `safety_hazard` INTEGER NOT NULL DEFAULT 0 (1 if emergency keywords found, 0 otherwise)
   - `status` TEXT NOT NULL DEFAULT 'Submitted' ('Submitted', 'Under Review', 'In Progress', 'Resolved')
   - `parent_id` INTEGER DEFAULT NULL (foreign key to complaints.id)
   - `duplicate_count` INTEGER NOT NULL DEFAULT 1
   - `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   - `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
3. Use ONLY parameterized SQL queries (`?`). Never format strings into SQL.

### B. Student Complaint Submission (`/submit`)
1. **GET `/submit`**: Render `templates/submit.html` (inheriting from `base.html`).
   - Fields: Campus Building (dropdown), Room/Area (text), Category (cards or dropdown), Title (text), Description (textarea).
   - Clean, accessible design matching `.ai/design.md`.
2. **Typeahead Duplicate Peek API (`GET /api/check-duplicates`)**:
   - Query params: `building`, `query`.
   - Uses `find_candidate_duplicates` from `ml.py` against active complaints in the same building.
   - Returns top 2 similar complaints so the frontend can gently notify the student: *"Notice: X students already reported a similar issue in this building"*.
3. **POST `/submit`**:
   - Validate inputs per `.ai/security.md` (enforce length limits, valid categories, valid buildings).
   - Run `scan_safety_hazard()` from `ml.py`. If emergency keywords (`spark`, `exposed wire`, `gas leak`, `flooding`, `smoke`, etc.) are detected, set `safety_hazard = 1` and `urgency = 'Critical'`.
   - Generate human-friendly reference code: `f"CFX-2026-{random.randint(1000, 9999)}"`.
   - Insert into SQLite and redirect to `/track/<reference_code>`.

### C. Student Tracking View (`/track/<reference_code>`)
1. **GET `/track/<reference_code>`**: Render `templates/track.html`.
2. Display:
   - Reference code with 1-click copy button.
   - Visual 4-step progress stepper: `Submitted` -> `Triaged` -> `In Progress` -> `Resolved`.
   - Urgency & Safety badges (glowing red badge if `safety_hazard == 1`).
   - Volume Signal: If `parent_id` or `duplicate_count > 1`, show: *"Linked with N other reports in this building. Priority elevated."*
   - Clear details: Building, Room, Category, Date submitted.

### D. Demo Seed Script (`seed.py`)
1. Create `seed.py` to populate `instance/campusfix.db` with the 5 realistic demo clusters specified in `.ai/seed_data.md`:
   - Cluster 1: AC Failure in Engineering Complex Room 204 (5 student reports, 1 parent + 4 duplicates).
   - Cluster 2: Water leak in Central Library 2nd floor restroom (4 reports, 1 parent + 3 duplicates).
   - Cluster 3: Sparks from outlet in Science Lab B Room 110 (2 reports, Critical Safety Hazard).
   - Cluster 4: Broken study chairs in Student Center (2 reports).
   - Cluster 5: Wi-Fi offline in Residential Hall West (3 reports).
2. Running `python3 seed.py` should reset/initialize and populate the DB cleanly.

---

## 4. Strict Constraints & Guardrails
* **NO Authentication**: Do not build login, JWT, user accounts, or passwords.
* **NO Data Deletion**: When handling duplicates, never run `DELETE`. Use `parent_id` and `duplicate_count`.
* **Zero XSS**: Do not use `| safe` in Jinja on user fields.
* **Python 3.11 Runtime**: Always use `.venv` with `python3` (avoid global python3.14).
* **Verify Before Done**: Test `/submit`, `/track/<ref>`, `seed.py`, and the DB with automated test commands.

---

## 5. Output Expected
1. Explain the changes made.
2. Provide exact terminal commands to run `python3 seed.py` and test the new routes.
