"""
CampusFix AI — Database Layer
Provides clean abstraction over SQLite with connection pooling and schema management.
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("campusfix.db")

# Database file location
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "campusfix.db")


def get_db_connection() -> sqlite3.Connection:
    """
    Creates a database connection with Row factory for dict-like access.
    Each connection is independent and must be closed by the caller.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_transaction():
    """
    Context manager for database transactions.
    Automatically commits on success or rolls back on exception.
    
    Usage:
        with db_transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ...")
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Database transaction failed: %s", e)
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialize database schema if not exists.
    Safe to call multiple times (idempotent).
    """
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        # Main complaints table
        cursor.execute("""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES complaints (id)
            )
        """)
        
        # Performance indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_ref 
            ON complaints(reference_code)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_building 
            ON complaints(building)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_parent 
            ON complaints(parent_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_status 
            ON complaints(status)
        """)
        
        logger.info("Database schema initialized successfully at: %s", DB_PATH)


def insert_complaint(
    reference_code: str,
    title: str,
    description: str,
    building: str,
    room: Optional[str],
    category: str,
    urgency: str = "Normal",
    safety_hazard: int = 0
) -> int:
    """
    Insert a new complaint and return its ID.
    Uses parameterized queries to prevent SQL injection.
    """
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints (
                reference_code, title, description, building, room,
                category, urgency, safety_hazard, status, duplicate_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', 1)
        """, (reference_code, title, description, building, room, category, urgency, safety_hazard))
        
        return cursor.lastrowid


def get_complaint_by_reference(reference_code: str) -> Optional[dict]:
    """
    Retrieve a single complaint by its reference code.
    Returns a dict-like Row object or None if not found.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM complaints WHERE reference_code = ?
        """, (reference_code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_complaint_by_id(complaint_id: int) -> Optional[dict]:
    """Retrieve a single complaint by primary key, or None if not found."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT * FROM complaints WHERE id = ?", (complaint_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_active_complaints_by_building(building: str) -> list[dict]:
    """
    Get all active (non-resolved) complaints in a specific building.
    Used for duplicate detection.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM complaints 
            WHERE building = ? AND status != 'Resolved'
            ORDER BY created_at DESC
        """, (building,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_complaints(limit: int = 100) -> list[dict]:
    """
    Retrieve recent complaints (for admin/staff views).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM complaints 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def update_complaint_status(complaint_id: int, new_status: str) -> None:
    """
    Update complaint status and refresh updated_at timestamp.
    """
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE complaints 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (new_status, complaint_id))


def link_duplicate(child_id: int, parent_id: int) -> None:
    """
    Mark child_id as a duplicate of parent_id.
    Increments parent's duplicate_count and updates child's parent_id.
    NEVER deletes the child record.
    """
    with db_transaction() as conn:
        cursor = conn.cursor()
        
        # Link child to parent
        cursor.execute("""
            UPDATE complaints 
            SET parent_id = ?, status = 'Under Review', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (parent_id, child_id))
        
        # Increment parent's duplicate counter
        cursor.execute("""
            UPDATE complaints 
            SET duplicate_count = duplicate_count + 1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (parent_id,))
        
        logger.info("Linked complaint %d as duplicate of %d", child_id, parent_id)


def reset_database() -> None:
    """
    Drop all tables and reinitialize schema.
    USE WITH CAUTION: Only for development and seeding.
    """
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS complaints")
        logger.warning("Database reset: All tables dropped")
    
    init_db()
