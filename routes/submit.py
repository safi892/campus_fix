"""
CampusFix AI — Submission Routes
Handles the student complaint form and the typeahead duplicate-peek API.
"""

import logging
import random
import sqlite3

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from db import get_active_complaints_by_building, insert_complaint
from forms import (
    ALLOWED_BUILDINGS,
    ALLOWED_CATEGORIES,
    sanitize_complaint_data,
    validate_complaint_submission,
)
from ml import find_candidate_duplicates, scan_safety_hazard

logger = logging.getLogger("campusfix.routes.submit")

submit_bp = Blueprint("submit", __name__)

MIN_PEEK_QUERY_LENGTH = 10
MAX_PEEK_RESULTS = 2
MAX_REFERENCE_ATTEMPTS = 5


def _render_form(error: str = "", form_data: dict | None = None, status: int = 200):
    """Render the submission form with dropdown options and optional error state."""
    html = render_template(
        "submit.html",
        error=error,
        form_data=form_data,
        buildings=sorted(ALLOWED_BUILDINGS),
        categories=sorted(ALLOWED_CATEGORIES),
    )
    return html, status


def _generate_reference_code() -> str:
    """Create a human-friendly tracking code, e.g. CFX-2026-9041."""
    return f"CFX-2026-{random.randint(1000, 9999)}"


def _save_complaint(clean_data: dict, urgency: str, safety_flag: int) -> str:
    """
    Insert the complaint and return its reference code.
    Retries with a fresh code if the random code collides (UNIQUE constraint).
    """
    for _ in range(MAX_REFERENCE_ATTEMPTS):
        reference_code = _generate_reference_code()
        try:
            insert_complaint(
                reference_code=reference_code,
                title=clean_data["title"],
                description=clean_data["description"],
                building=clean_data["building"],
                room=clean_data["room"],
                category=clean_data["category"],
                urgency=urgency,
                safety_hazard=safety_flag,
            )
            return reference_code
        except sqlite3.IntegrityError:
            logger.warning("Reference code collision on %s, retrying", reference_code)
    raise RuntimeError("Could not allocate a unique reference code")


@submit_bp.route("/submit", methods=["GET"])
def submit_form():
    """Render the empty complaint form."""
    return _render_form()


@submit_bp.route("/submit", methods=["POST"])
def submit_complaint():
    """Validate, safety-scan, store, then redirect to the tracking receipt."""
    form_data = {
        field: request.form.get(field, "")
        for field in ("title", "description", "category", "building", "room")
    }

    is_valid, error_message = validate_complaint_submission(form_data)
    if not is_valid:
        return _render_form(error_message, form_data, status=400)

    clean_data = sanitize_complaint_data(form_data)

    # Deterministic keyword scan: physical safety never depends on ML.
    is_hazard = scan_safety_hazard(f"{clean_data['title']} {clean_data['description']}")
    urgency = "Critical" if is_hazard else "Normal"

    try:
        reference_code = _save_complaint(clean_data, urgency, int(is_hazard))
    except Exception:
        logger.exception("Complaint submission failed")
        return _render_form(
            "Unable to submit your report. Please try again.", form_data, status=500
        )

    logger.info("New complaint %s (safety_hazard=%s)", reference_code, is_hazard)
    return redirect(url_for("track.track_complaint", reference_code=reference_code))


@submit_bp.route("/api/check-duplicates", methods=["GET"])
def check_duplicates_api():
    """
    Typeahead peek: top similar active complaints in the same building.
    Query params: building, query.
    """
    building = request.args.get("building", "").strip()
    query_text = request.args.get("query", "").strip()

    if building not in ALLOWED_BUILDINGS:
        return jsonify({"error": "Invalid building"}), 400

    if len(query_text) < MIN_PEEK_QUERY_LENGTH:
        return jsonify({"similar_complaints": []})

    try:
        existing = get_active_complaints_by_building(building)
        # Only canonical (parent) reports are shown to students.
        existing = [c for c in existing if c["parent_id"] is None]
        matches = find_candidate_duplicates(query_text, "", existing)
    except Exception:
        logger.exception("Duplicate check failed")
        return jsonify({"error": "Unable to check duplicates"}), 500

    similar = [
        {
            "reference_code": m["complaint"]["reference_code"],
            "title": m["complaint"]["title"],
            "similarity": m["similarity"],
            "duplicate_count": m["complaint"]["duplicate_count"],
        }
        for m in matches[:MAX_PEEK_RESULTS]
    ]
    return jsonify({"similar_complaints": similar})
