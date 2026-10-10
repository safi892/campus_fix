"""
CampusFix AI — Database Layer
All SQL lives here. Every query is parameterized (`?`). Records are never deleted:
duplicates are linked with `parent_id` and counted with `duplicate_count`.
"""

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger("campusfix.db")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "campusfix.db")


class AlreadyLinkedError(Exception):
    """Raised when a merge targets a report that is no longer standalone."""


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------
def get_db_connection() -> sqlite3.Connection:
    """Open a new connection with dict-like rows. Caller must close it."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_transaction():
    """Commit on success, roll back on error, always close."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Database transaction failed")
        raise
    finally:
        conn.close()


def _fetch_all(query: str, params: tuple = ()) -> list[dict]:
    conn = get_db_connection()
    try:
        return [dict(row) for row in conn.execute(query, params).fetchall()]
    finally:
        conn.close()


def _fetch_one(query: str, params: tuple = ()) -> Optional[dict]:
    conn = get_db_connection()
    try:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
def init_db() -> None:
    """Create tables and indexes if missing, then apply additive migrations. Idempotent."""
    with db_transaction() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference_code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                building TEXT NOT NULL,
                room TEXT,
                category TEXT NOT NULL,
                urgency TEXT NOT NULL DEFAULT 'Normal',
                safety_hazard INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'Submitted',
                parent_id INTEGER DEFAULT NULL,
                duplicate_count INTEGER NOT NULL DEFAULT 1,
                ai_reviewed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES complaints (id)
            )
        """)
        _migrate_schema(conn)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_complaints_ref ON complaints(reference_code)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_complaints_building ON complaints(building)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_complaints_parent ON complaints(parent_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)")
    logger.info("Database ready at %s", DB_PATH)


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the first release. Never drops data."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(complaints)")}
    if "ai_reviewed" not in columns:
        # 1 = staff chose "Keep Separate"; the AI will not suggest this report again.
        conn.execute("ALTER TABLE complaints ADD COLUMN ai_reviewed INTEGER NOT NULL DEFAULT 0")
        logger.info("Migration: added complaints.ai_reviewed")
    if "location" not in columns:
        conn.execute("ALTER TABLE complaints ADD COLUMN location TEXT")
        logger.info("Migration: added complaints.location")
    if "user_type" not in columns:
        conn.execute("ALTER TABLE complaints ADD COLUMN user_type TEXT DEFAULT 'student'")
        logger.info("Migration: added complaints.user_type")
    if "image_filename" not in columns:
        conn.execute("ALTER TABLE complaints ADD COLUMN image_filename TEXT")
        logger.info("Migration: added complaints.image_filename")
    if "duplicate_group" not in columns:
        conn.execute("ALTER TABLE complaints ADD COLUMN duplicate_group TEXT")
        logger.info("Migration: added complaints.duplicate_group")


def reset_database() -> None:
    """Drop and recreate the schema. Development and seeding only."""
    with db_transaction() as conn:
        conn.execute("DROP TABLE IF EXISTS complaints")
    logger.warning("Database reset: complaints table dropped")
    init_db()


# ---------------------------------------------------------------------------
# Student flow
# ---------------------------------------------------------------------------
def insert_complaint(
    reference_code: str,
    title: str,
    description: str,
    building: str,
    room: Optional[str] = None,
    category: str = "Other",
    urgency: str = "Normal",
    safety_hazard: int = 0,
    user_type: str = "student",
    image_filename: Optional[str] = None,
    duplicate_group: Optional[str] = None,
    location: Optional[str] = None,
) -> int:
    """Insert a new standalone complaint and return its id."""
    resolved_loc = location or building
    with db_transaction() as conn:
        cursor = conn.execute("""
            INSERT INTO complaints (
                reference_code, title, description, building, room,
                category, urgency, safety_hazard, status, duplicate_count,
                location, user_type, image_filename, duplicate_group
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', 1, ?, ?, ?, ?)
        """, (
            reference_code, title, description, resolved_loc, room,
            category, urgency, safety_hazard,
            resolved_loc, user_type, image_filename, duplicate_group
        ))
        return cursor.lastrowid


def get_complaint_by_reference(reference_code: str) -> Optional[dict]:
    return _fetch_one("SELECT * FROM complaints WHERE reference_code = ?", (reference_code,))


def get_complaint_by_id(complaint_id: int) -> Optional[dict]:
    return _fetch_one("SELECT * FROM complaints WHERE id = ?", (complaint_id,))


def get_active_complaints_by_building(building: str) -> list[dict]:
    """All non-resolved complaints in a building (used by the typeahead peek)."""
    return _fetch_all("""
        SELECT * FROM complaints
        WHERE building = ? AND status != 'Resolved'
        ORDER BY created_at DESC
    """, (building,))


def get_all_complaints(limit: int = 100) -> list[dict]:
    return _fetch_all("SELECT * FROM complaints ORDER BY created_at DESC LIMIT ?", (limit,))


# ---------------------------------------------------------------------------
# Staff queue & clusters
# ---------------------------------------------------------------------------
def get_staff_queue(
    building_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> list[dict]:
    """
    Canonical jobs (parent_id IS NULL), safety first, then cluster size, then newest.
    Without a status filter, resolved jobs are hidden so the queue shows open work.
    """
    # Only fixed SQL fragments are joined; every user value goes through `params`.
    conditions = ["parent_id IS NULL"]
    params: list = []

    if building_filter:
        conditions.append("building = ?")
        params.append(building_filter)
    if category_filter:
        conditions.append("category = ?")
        params.append(category_filter)
    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)
    else:
        conditions.append("status != 'Resolved'")

    query = (
        "SELECT * FROM complaints WHERE " + " AND ".join(conditions) +
        " ORDER BY safety_hazard DESC, duplicate_count DESC, created_at DESC, id DESC"
    )
    return _fetch_all(query, tuple(params))


def get_cluster_children(parent_id: int) -> list[dict]:
    """Individual student reports linked into a cluster, oldest first."""
    return _fetch_all("""
        SELECT * FROM complaints WHERE parent_id = ?
        ORDER BY created_at ASC, id ASC
    """, (parent_id,))


def get_unclustered_candidates(building: str) -> list[dict]:
    """
    Standalone, active, not-yet-reviewed reports in a building.
    These are the reports the AI may propose merging. Oldest first.
    """
    return _fetch_all("""
        SELECT * FROM complaints
        WHERE building = ?
          AND parent_id IS NULL
          AND duplicate_count = 1
          AND ai_reviewed = 0
          AND status != 'Resolved'
        ORDER BY id ASC
    """, (building,))  # id order matches the "older parent" rule in services/triage.py


def update_complaint_status(complaint_id: int, new_status: str) -> bool:
    """
    Set the status of a complaint AND every report linked to it, so each student's
    tracking page reflects the real repair progress. Returns False if id not found.
    """
    with db_transaction() as conn:
        cursor = conn.execute("""
            UPDATE complaints
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? OR parent_id = ?
        """, (new_status, complaint_id, complaint_id))
        return cursor.rowcount > 0


def link_duplicate(child_id: int, parent_id: int) -> int:
    """
    Link child into parent's cluster and return the parent's new duplicate_count.
    - Never deletes: the child keeps its own row and reference code.
    - A submitted parent moves to 'Under Review' (it has now been triaged).
    - The child inherits the parent's status so its tracker shows real progress.
    - A safety hazard on the child escalates the parent, because staff only see parents.
    Business validation lives in services/triage.py. As a last line of defence, the
    child is only linked if it is still standalone, all inside one transaction, so
    two simultaneous merges can never double-count. Raises AlreadyLinkedError otherwise.
    """
    with db_transaction() as conn:
        # 1. Claim the child atomically (only if still standalone).
        cursor = conn.execute("""
            UPDATE complaints
            SET parent_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND parent_id IS NULL AND duplicate_count = 1
        """, (parent_id, child_id))
        if cursor.rowcount == 0:
            raise AlreadyLinkedError(f"Complaint {child_id} is not a standalone report")

        child_hazard = conn.execute(
            "SELECT safety_hazard FROM complaints WHERE id = ?", (child_id,)
        ).fetchone()["safety_hazard"]

        # 2. Grow the parent cluster and escalate safety if needed.
        conn.execute("""
            UPDATE complaints
            SET duplicate_count = duplicate_count + 1,
                status = CASE WHEN status = 'Submitted' THEN 'Under Review' ELSE status END,
                safety_hazard = MAX(safety_hazard, ?),
                urgency = CASE WHEN ? = 1 THEN 'Critical' ELSE urgency END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (child_hazard, child_hazard, parent_id))

        # 3. Child mirrors the parent's (possibly just-updated) status.
        conn.execute("""
            UPDATE complaints
            SET status = (SELECT status FROM complaints WHERE id = ?)
            WHERE id = ?
        """, (parent_id, child_id))

        row = conn.execute(
            "SELECT duplicate_count FROM complaints WHERE id = ?", (parent_id,)
        ).fetchone()

    logger.info("Linked complaint %d into cluster %d", child_id, parent_id)
    return row["duplicate_count"]


def mark_ai_reviewed(complaint_id: int) -> bool:
    """Record a 'Keep Separate' decision. Returns False if id not found."""
    with db_transaction() as conn:
        cursor = conn.execute("""
            UPDATE complaints
            SET ai_reviewed = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (complaint_id,))
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
def get_hotspot_analytics() -> dict:
    """Campus-wide consolidation, safety, and building/category load figures."""
    totals = _fetch_one("""
        SELECT
            COUNT(*) AS total_reports,
            SUM(CASE WHEN parent_id IS NULL THEN 1 ELSE 0 END) AS consolidated_jobs,
            SUM(safety_hazard) AS safety_hazards_count,
            SUM(CASE WHEN parent_id IS NULL AND status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_jobs,
            SUM(CASE WHEN parent_id IS NULL AND status != 'Resolved' AND safety_hazard = 1
                     THEN 1 ELSE 0 END) AS active_hazard_jobs
        FROM complaints
    """) or {}

    # SUM() returns NULL on an empty table, so normalise to 0.
    total_reports = totals.get("total_reports") or 0
    consolidated_jobs = totals.get("consolidated_jobs") or 0
    resolved_jobs = totals.get("resolved_jobs") or 0

    workload_reduction_pct = (
        round((1 - consolidated_jobs / total_reports) * 100, 1) if total_reports else 0.0
    )

    building_stats = _fetch_all("""
        SELECT building,
               COUNT(*) AS total_reports,
               SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_reports
        FROM complaints
        GROUP BY building
        ORDER BY total_reports DESC, building ASC
    """)

    category_stats = _fetch_all("""
        SELECT category, COUNT(*) AS total_reports
        FROM complaints
        GROUP BY category
        ORDER BY total_reports DESC, category ASC
    """)

    return {
        "total_reports": total_reports,
        "consolidated_jobs": consolidated_jobs,
        "workload_reduction_pct": workload_reduction_pct,
        "safety_hazards_count": totals.get("safety_hazards_count") or 0,
        "active_hazard_jobs": totals.get("active_hazard_jobs") or 0,
        "resolved_jobs": resolved_jobs,
        "pending_jobs": consolidated_jobs - resolved_jobs,
        "building_stats": building_stats,
        "category_stats": category_stats,
    }
