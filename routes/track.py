"""
CampusFix AI — Tracking Routes
Handles student complaint status tracking and progress display.
"""

from datetime import datetime

from flask import Blueprint, render_template, abort

from db import get_complaint_by_reference, get_complaint_by_id

track_bp = Blueprint("track", __name__)

# Maps DB status -> stepper position (1-4)
STATUS_STEPS = {
    "Submitted": 1,
    "Under Review": 2,
    "In Progress": 3,
    "Resolved": 4,
}

URGENCY_BADGE_CLASS = {
    "Critical": "danger",
    "High": "warning",
    "Normal": "primary",
    "Low": "secondary",
}

DATE_DISPLAY_FORMAT = "%B %d, %Y at %I:%M %p"


def _format_timestamp(value: str) -> str:
    """Convert a SQLite timestamp string into a human-friendly date."""
    return datetime.fromisoformat(value).strftime(DATE_DISPLAY_FORMAT)


def _linked_report_count(complaint: dict) -> int:
    """
    Number of OTHER reports linked with this complaint.
    A child report looks at its parent's cluster; a parent uses its own counter.
    """
    if complaint["parent_id"]:
        parent = get_complaint_by_id(complaint["parent_id"])
        cluster_size = parent["duplicate_count"] if parent else 1
    else:
        cluster_size = complaint["duplicate_count"]
    return max(cluster_size - 1, 0)


@track_bp.route("/track/<reference_code>")
def track_complaint(reference_code: str):
    """Display the tracking receipt for a complaint."""
    complaint = get_complaint_by_reference(reference_code)
    if complaint is None:
        abort(404)

    linked_count = _linked_report_count(complaint)

    return render_template(
        "track.html",
        complaint=complaint,
        current_step=STATUS_STEPS.get(complaint["status"], 1),
        linked_count=linked_count,
        urgency_class=URGENCY_BADGE_CLASS.get(complaint["urgency"], "primary"),
        created_formatted=_format_timestamp(complaint["created_at"]),
        updated_formatted=_format_timestamp(complaint["updated_at"]),
    )
