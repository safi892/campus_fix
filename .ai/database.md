# CampusFix AI — Database & Schema Specification

> **AI INSTRUCTION**: Use SQLite with standard `sqlite3` library. Keep database logic in `db.py`. Do NOT use heavy ORMs (SQLAlchemy) to prevent overhead. Parameterize all queries (`?`).

---

## 1. Database Location & Init
* **Database File**: `instance/campusfix.db`
* **Auto-creation**: `get_db()` helper checks and initializes DB if not present.

---

## 2. DDL Table Definition

```sql
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_code TEXT UNIQUE NOT NULL,      -- e.g. "CFX-2026-8192"
    title TEXT NOT NULL,                     -- e.g. "Water leaking from ceiling"
    description TEXT NOT NULL,               -- Full explanation
    building TEXT NOT NULL,                  -- e.g. "Library", "Engineering Hall"
    room TEXT,                               -- e.g. "Room 204", "2nd Floor Restroom"
    category TEXT NOT NULL,                  -- "HVAC", "Electrical", "Plumbing", "Furniture", "Cleanliness", "Safety"
    urgency TEXT NOT NULL DEFAULT 'Normal',  -- "Critical", "High", "Normal", "Low"
    safety_hazard INTEGER NOT NULL DEFAULT 0,-- 1 if dangerous keywords detected, 0 otherwise
    status TEXT NOT NULL DEFAULT 'Submitted',-- "Submitted", "Under Review", "In Progress", "Resolved"
    parent_id INTEGER DEFAULT NULL,          -- If clustered: points to canonical complaints(id)
    duplicate_count INTEGER NOT NULL DEFAULT 1, -- Number of reports in this cluster
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES complaints (id)
);

CREATE INDEX IF NOT EXISTS idx_complaints_ref ON complaints(reference_code);
CREATE INDEX IF NOT EXISTS idx_complaints_building ON complaints(building);
CREATE INDEX IF NOT EXISTS idx_complaints_parent ON complaints(parent_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
```

---

## 3. Canonical SQL Queries

### A. Insert Student Submission
```python
cursor.execute("""
    INSERT INTO complaints (
        reference_code, title, description, building, room,
        category, urgency, safety_hazard, status, duplicate_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', 1)
""", (ref_code, title, desc, building, room, category, urgency, safety_hazard))
```

### B. Lookup Student Tracking Record
```python
cursor.execute("""
    SELECT * FROM complaints WHERE reference_code = ?
""", (ref_code,))
```

### C. Retrieve Staff Priority Queue (Canonical Parent Issues Only)
```python
# Only fetch top-level complaints (parent_id IS NULL)
# Sorted first by Safety Hazards, then by Duplicate Count descending, then recency
cursor.execute("""
    SELECT * FROM complaints 
    WHERE parent_id IS NULL AND status != 'Resolved'
    ORDER BY safety_hazard DESC, duplicate_count DESC, created_at DESC
""")
```

### D. Soft-Deduplication Merge (NEVER DELETE)
When staff confirms Complaint B (`child_id`) is a duplicate of Complaint A (`parent_id`):
```python
# 1. Link child to parent
cursor.execute("""
    UPDATE complaints 
    SET parent_id = ?, status = 'Under Review', updated_at = CURRENT_TIMESTAMP 
    WHERE id = ?
""", (parent_id, child_id))

# 2. Increment parent cluster counter
cursor.execute("""
    UPDATE complaints 
    SET duplicate_count = duplicate_count + 1, updated_at = CURRENT_TIMESTAMP 
    WHERE id = ?
""", (parent_id,))
```

### E. Campus Hotspot Aggregation Query
```python
cursor.execute("""
    SELECT building, COUNT(*) as total_reports, SUM(duplicate_count) as total_volume
    FROM complaints
    GROUP BY building
    ORDER BY total_volume DESC
""")
```
