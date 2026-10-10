"""
CampusFix AI — Staff Routes
Maintenance dashboard, human-in-the-loop duplicate review, and hotspot analytics.

No authentication by design (hackathon demo). JSON endpoints only accept
`Content-Type: application/json`, which a cross-site HTML form cannot send.
"""

import logging

from flask import Blueprint, jsonify, render_template, request

import db
from forms import ALLOWED_BUILDINGS, ALLOWED_CATEGORIES, ALLOWED_STATUSES, STATUS_FLOW
from services import triage

logger = logging.getLogger("campusfix.routes.staff")

staff_bp = Blueprint("staff", __name__)


# ---------------------------------------------------------------------------
# Small request/response helpers
# ---------------------------------------------------------------------------
def _allowed_or_none(value: str | None, allowed: set[str]) -> str | None:
    """Return the filter value if it is on the allowlist, otherwise no filter."""
    value = (value or "").strip()
    return value if value in allowed else None


def _json_body() -> dict:
    body = request.get_json(silent=True)  # None unless Content-Type is JSON
    if not isinstance(body, dict):
        raise triage.TriageError("Request body must be a JSON object.")
    return body


def _required_id(body: dict, key: str) -> int:
    value = body.get(key)
    # bool is a subclass of int in Python, so exclude it explicitly.
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise triage.TriageError(f"'{key}' must be a positive integer.")
    return value


def _error(message: str, status_code: int):
    return jsonify({"success": False, "error": message}), status_code


@staff_bp.errorhandler(triage.TriageError)
def _handle_triage_error(error: triage.TriageError):
    """Expected, user-facing failures (bad input, not found, conflict)."""
    return _error(error.message, error.status_code)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
@staff_bp.route("/staff")
def staff_dashboard():
    filters = {
        "building": _allowed_or_none(request.args.get("building"), ALLOWED_BUILDINGS),
        "category": _allowed_or_none(request.args.get("category"), ALLOWED_CATEGORIES),
        "status": _allowed_or_none(request.args.get("status"), ALLOWED_STATUSES),
    }

    queue = db.get_staff_queue(
        building_filter=filters["building"],
        category_filter=filters["category"],
        status_filter=filters["status"],
    )
    triage.attach_cluster_children(queue)

    return render_template(
        "staff.html",
        queue=queue,
        suggestions=triage.build_duplicate_suggestions(filters["building"]),
        stats=db.get_hotspot_analytics(),
        filters=filters,
        buildings=sorted(ALLOWED_BUILDINGS),
        categories=sorted(ALLOWED_CATEGORIES),
        statuses=STATUS_FLOW,
    )


@staff_bp.route("/analytics")
def analytics_view():
    stats = db.get_hotspot_analytics()
    total = stats["total_reports"]

    # Pre-compute bar widths here so the template stays free of arithmetic.
    for row in stats["building_stats"] + stats["category_stats"]:
        row["share_pct"] = round(row["total_reports"] / total * 100) if total else 0
    for row in stats["building_stats"]:
        reports = row["total_reports"]
        row["resolved_pct"] = round(row["resolved_reports"] / reports * 100) if reports else 0

    jobs = stats["consolidated_jobs"]
    stats["resolved_jobs_pct"] = round(stats["resolved_jobs"] / jobs * 100) if jobs else 0

    return render_template("analytics.html", stats=stats)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------
@staff_bp.route("/api/status/update", methods=["POST"])
def update_status():
    body = _json_body()
    complaint_id = _required_id(body, "id")
    status = body.get("status")
    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        raise triage.TriageError(f"'status' must be one of: {', '.join(STATUS_FLOW)}.")

    triage.update_job_status(complaint_id, status)

    logger.info("Status of job %d set to %s", complaint_id, status)
    return jsonify({"success": True, "id": complaint_id, "status": status})


@staff_bp.route("/api/cluster/merge", methods=["POST"])
def merge_cluster():
    body = _json_body()
    parent_id = _required_id(body, "parent_id")
    child_id = _required_id(body, "child_id")

    new_count = triage.merge_into_cluster(parent_id, child_id)
    return jsonify({
        "success": True,
        "parent_id": parent_id,
        "child_id": child_id,
        "new_count": new_count,
        "message": f"Report #{child_id} linked to cluster #{parent_id}.",
    })


@staff_bp.route("/api/cluster/dismiss", methods=["POST"])
def dismiss_suggestion():
    body = _json_body()
    triage.keep_separate(_required_id(body, "complaint_id"))
    return jsonify({"success": True})
