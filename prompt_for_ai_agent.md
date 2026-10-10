# TASK: Implement Milestone 3 for CampusFix AI (Staff Dashboard, AI Duplicate Review & Hotspot Analytics)

You are continuing development on **CampusFix AI**, an intelligent university maintenance dispatch and deduplication system. 

Before writing any code, inspect the codebase and read the architectural rules in `.ai/context.md`, `.ai/rules.md`, `.ai/routes.md`, `.ai/database.md`, and `.ai/design.md`.

---

## 1. What is Already Built & Working (DO NOT BREAK THIS)
* **Milestone 1 & 2 are complete and tested** (`test_routes.py` has 16/16 passing unit tests).
* **Database Layer (`db.py`)**: SQLite `complaints` table with `parent_id` and `duplicate_count` soft clustering.
* **Student Flow (`routes/submit.py`, `routes/track.py`)**: `/submit` complaint form and `/track/<reference_code>` status receipt.
* **Offline ML Engine (`ml.py`)**: `SentenceTransformer` loading locally from `models/all-MiniLM-L6-v2/` on CPU/MPS with TF-IDF fallback and regex safety scanner.
* **Demo Seed Dataset (`seed.py`)**: Populates 5 realistic clusters (16 complaints) with pre-arranged duplicates and an emergency safety hazard.

---

## 2. Your Goal in Milestone 3 (The Winning Hackathon Presentation Layer)
Build the staff maintenance management experience:
1. **Staff Maintenance Dashboard (`/staff`)** with filtering and 1-click status updates.
2. **AI Duplicate Review Deck (Human-in-the-Loop)** with side-by-side comparison and `[Accept Merge]` / `[Keep Separate]` actions.
3. **Campus Hotspot Analytics (`/analytics`)** showing consolidation efficiency and building maintenance load.
4. **Automated Test Suite (`test_staff_routes.py`)**.

---

## 3. Detailed Implementation Requirements

### A. Database Helper Extensions (`db.py`)
Add the following functions to `db.py` (use parameterized queries `?` ONLY):
1. `get_staff_queue(building_filter=None, category_filter=None, status_filter=None) -> list[dict]`:
   - Fetches canonical parent complaints (`parent_id IS NULL`).
   - Order by: `safety_hazard DESC, duplicate_count DESC, created_at DESC`.
   - Supports optional filtering by `building`, `category`, and `status`.
2. `get_cluster_children(parent_id: int) -> list[dict]`:
   - Fetches all child reports linked to a parent complaint (`parent_id = ?`).
3. `get_unclustered_candidates(building: str) -> list[dict]`:
   - Fetches active complaints in the same building that have `duplicate_count == 1` and `parent_id IS NULL` (potential duplicates waiting for review).
4. `get_hotspot_analytics() -> dict`:
   - Aggregates:
     - `total_reports`: Total rows in `complaints`.
     - `consolidated_jobs`: Count of parent complaints (`parent_id IS NULL`).
     - `workload_reduction_pct`: Calculated percentage: `round((1 - consolidated_jobs / total_reports) * 100, 1)`.
     - `safety_hazards_count`: Count where `safety_hazard == 1`.
     - `building_stats`: Group by building, count total reports and resolved count.
     - `category_stats`: Group by category, count total reports.

### B. Staff Blueprint & Endpoints (`routes/staff.py`)
Create a new blueprint `staff_bp = Blueprint("staff", __name__)` and register it in `app.py`:

1. **GET `/staff`**:
   - Query parameters for filters: `building`, `category`, `status`.
   - Loads the prioritized queue from `get_staff_queue()`.
   - Finds AI duplicate suggestions: for each complaint, compare against other complaints in the same building using `find_candidate_duplicates()` from `ml.py`.
   - Renders `templates/staff.html`.
2. **POST `/api/status/update`** (JSON):
   - Request body: `{ "id": 1, "status": "In Progress" }` (Valid: `Submitted | Under Review | In Progress | Resolved`).
   - Updates status in database.
   - Response: `{ "success": true, "id": 1, "status": "In Progress" }`.
3. **POST `/api/cluster/merge`** (JSON):
   - Request body: `{ "parent_id": 1, "child_id": 3 }`.
   - Calls `link_duplicate(child_id, parent_id)` in `db.py` (increments parent count, sets child parent_id, NEVER deletes).
   - Response: `{ "success": true, "parent_id": 1, "child_id": 3, "new_count": 6 }`.
4. **POST `/api/cluster/dismiss`** (JSON):
   - Request body: `{ "complaint_id": 3 }`.
   - Marks the complaint as explicitly reviewed so it won't be re-suggested.
   - Response: `{ "success": true }`.
5. **GET `/analytics`**:
   - Calls `get_hotspot_analytics()` from `db.py`.
   - Renders `templates/analytics.html`.

### C. Staff UI & Visual Craft (`templates/staff.html`)
Design matching `.ai/design.md`:
* **Top Header & Filter Bar**: Filter by Building, Category, or Status; quick counters for `Urgent Safety Hazards`, `Total Reports`, `Consolidated Jobs`.
* **AI Duplicate Review Deck (Top Section)**:
  - If AI detects duplicate candidates ($\ge 0.65$ similarity), show an alert card with side-by-side comparison:
    - *Candidate Report* vs *Canonical Parent Report* with similarity badge (e.g. `88% Match [High Confidence]`).
    - Buttons: `[✓ Accept Merge]` (fires `POST /api/cluster/merge` and updates UI dynamically) and `[✕ Keep Separate]`.
* **Ticket Queue (Cards or Table)**:
  - Each item shows: Urgency badge (`Critical` with `safety-pulse`), Volume badge (`🔥 5 Reports`), Title, Building, Room, Category, Submitted timestamp.
  - Expandable accordion: Clicking a cluster reveals all individual student reports grouped inside it.
  - Status dropdown: Staff can change status to `Under Review`, `In Progress`, or `Resolved`.

### D. Analytics UI (`templates/analytics.html`)
* **Impact Metric Banner**: *"16 student reports consolidated into 5 actionable repair jobs (68% workload reduction)"*.
* **Campus Building Load**: Progress bars showing reports per building (Engineering Complex, Library, etc.).
* **Category Breakdown**: Percentage bar/distribution for HVAC, Plumbing, Safety, Electrical.
* **Resolution Gauge**: Completed vs pending repairs.

### E. Navbar Integration
* Update `templates/base.html` navigation bar to include links to:
  * `Report Issue` (`{{ url_for('submit.submit_form') }}`)
  * `Staff Dashboard` (`{{ url_for('staff.staff_dashboard') }}`)
  * `Hotspots & Analytics` (`{{ url_for('staff.analytics_view') }}`)

---

## 4. Strict Constraints & Guardrails
* **NO Authentication**: Do not build login forms, JWT, or password tables. The staff view is directly accessible at `/staff` for the hackathon demo.
* **NEVER DELETE Records**: All merges must preserve child records and their reference codes.
* **Parameterized SQL Only**: All new queries in `db.py` must use `?`.
* **Preserve Test Suite**: Ensure `python3 -m unittest test_routes -v` still passes.
* **Create `test_staff_routes.py`**: Write and run unit tests covering `/staff`, `/api/status/update`, `/api/cluster/merge`, and `/analytics`.

---

## 5. Verification Command
When completed, verify by running:
```bash
python3 seed.py
python3 -m unittest test_routes test_staff_routes -v
```
All tests must pass.
