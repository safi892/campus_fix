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
    DATASET_CATEGORIES,
    DATASET_LOCATIONS,
    FLOORS,
    URGENCY_LEVELS,
    USER_TYPES,
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
    """Render the submission form with dataset options and optional error state."""
    html = render_template(
        "submit.html",
        error=error,
        form_data=form_data,
        locations=DATASET_LOCATIONS,
        buildings=DATASET_LOCATIONS,  # backward compatibility alias
        categories=DATASET_CATEGORIES,
        user_types=USER_TYPES,
        floors=FLOORS,
        urgency_levels=URGENCY_LEVELS,
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
                user_type=clean_data.get("user_type", "student"),
                image_filename=clean_data.get("image_filename"),
                location=clean_data.get("location"),
                floor=clean_data.get("floor"),
                equipment_id=clean_data.get("equipment_id"),
                contact_info=clean_data.get("contact_info"),
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
    # Handle optional image file upload or passed filename
    uploaded_image_filename = None
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            if filename:
                upload_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "static", "uploads"
                )
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                uploaded_image_filename = filename

    form_data = {
        "title": request.form.get("title", ""),
        "description": request.form.get("description", ""),
        "category": request.form.get("category", ""),
        "location": request.form.get("location", "") or request.form.get("building", ""),
        "building": request.form.get("location", "") or request.form.get("building", ""),
        "room": request.form.get("room", ""),
        "user_type": request.form.get("user_type", "student"),
        "image_filename": uploaded_image_filename or request.form.get("image_filename", ""),
        "floor": request.form.get("floor", ""),
        "equipment_id": request.form.get("equipment_id", ""),
        "contact_info": request.form.get("contact_info", ""),
        "urgency": request.form.get("urgency", "Normal"),
    }

    is_valid, error_message = validate_complaint_submission(form_data)
    if not is_valid:
        return _render_form(error_message, form_data, status=400)

    clean_data = sanitize_complaint_data(form_data)

    # Deterministic keyword scan: physical safety never depends on ML.
    is_hazard = scan_safety_hazard(f"{clean_data['title']} {clean_data['description']}")
    if is_hazard or clean_data.get("urgency") == "Critical":
        urgency = "Critical"
        safety_flag = 1
    else:
        urgency = clean_data.get("urgency") or "Normal"
        safety_flag = 0

    try:
        reference_code = _save_complaint(clean_data, urgency, safety_flag)
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
    Typeahead peek: top similar active complaints in the same location.
    Query params: location (or building), query.
    """
    location = (request.args.get("location") or request.args.get("building") or "").strip()
    query_text = request.args.get("query", "").strip()

    if location not in ALLOWED_BUILDINGS:
        return jsonify({"error": "Invalid location"}), 400

    if len(query_text) < MIN_PEEK_QUERY_LENGTH:
        return jsonify({"similar_complaints": []})

    try:
        existing = get_active_complaints_by_building(location)
        # Only canonical (parent) reports are shown to reporters.
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
