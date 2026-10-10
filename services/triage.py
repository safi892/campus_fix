"""
CampusFix AI — Staff triage service.

Two responsibilities:
1. Build AI duplicate suggestions for the review deck (the AI only *proposes*).
2. Apply staff decisions (merge / keep separate) after validating them.

Routes call these functions; these functions call db.py and ml.py.
"""

import logging

import db
from forms import ALLOWED_BUILDINGS
from ml import find_candidate_duplicates

logger = logging.getLogger("campusfix.services.triage")

SIMILARITY_THRESHOLD = 0.65  # below this, reports are treated as independent


class TriageError(Exception):
    """A staff action that cannot be applied. `status_code` maps to the HTTP response."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# ---------------------------------------------------------------------------
# AI suggestions
# ---------------------------------------------------------------------------
def build_duplicate_suggestions(building: str | None = None) -> list[dict]:
    """
    Return merge proposals, highest similarity first:
        {"candidate": {...}, "parent": {...}, "similarity": 0.88,
         "similarity_pct": 88, "confidence": "High"}

    Never raises: if the ML layer fails, the dashboard still loads without suggestions.
    """
    buildings = [building] if building else sorted(ALLOWED_BUILDINGS)
    suggestions: list[dict] = []
    try:
        for name in buildings:
            suggestions.extend(_suggestions_for_building(name))
    except Exception:
        logger.exception("Duplicate suggestion engine failed; showing none")
        return []

    suggestions.sort(key=lambda s: s["similarity"], reverse=True)
    return suggestions


def _suggestions_for_building(building: str) -> list[dict]:
    """
    Compare each standalone report with the open jobs in the same building.

    A job can absorb a candidate if it is already a cluster, or it is an older
    standalone report. The "older" rule stops us proposing A->B and B->A.
    Candidates are processed oldest first, and once a report is proposed as a
    child it is no longer offered as a parent, so accepted merges never conflict.
    """
    candidates = db.get_unclustered_candidates(building)
    if not candidates:
        return []

    open_jobs = db.get_staff_queue(building_filter=building)
    proposed_children: set[int] = set()
    results = []

    for candidate in candidates:
        targets = [
            job for job in open_jobs
            if job["id"] != candidate["id"]
            and job["id"] not in proposed_children
            and (job["duplicate_count"] > 1 or job["id"] < candidate["id"])
        ]
        matches = find_candidate_duplicates(
            candidate["title"], candidate["description"], targets, threshold=SIMILARITY_THRESHOLD
        )
        if not matches:
            continue

        best = matches[0]
        proposed_children.add(candidate["id"])
        results.append({
            "candidate": candidate,
            "parent": best["complaint"],
            "similarity": best["similarity"],
            "similarity_pct": round(best["similarity"] * 100),
            "confidence": best["confidence"],
        })

    return results


# ---------------------------------------------------------------------------
# Staff decisions
# ---------------------------------------------------------------------------
def merge_into_cluster(parent_id: int, child_id: int) -> int:
    """Validate and link child into parent's cluster. Returns the new cluster size."""
    if parent_id == child_id:
        raise TriageError("A report cannot be merged into itself.")

    parent = db.get_complaint_by_id(parent_id)
    child = db.get_complaint_by_id(child_id)
    if parent is None or child is None:
        raise TriageError("Report not found.", status_code=404)

    if parent["parent_id"] is not None:
        raise TriageError("Target report is itself a duplicate; merge into its parent instead.", 409)
    if child["parent_id"] is not None:
        raise TriageError("This report is already linked to a cluster.", 409)
    if child["duplicate_count"] > 1:
        raise TriageError("This report already has its own cluster and cannot be merged.", 409)
    if parent["building"] != child["building"]:
        raise TriageError("Only reports in the same building can be merged.")

    return db.link_duplicate(child_id, parent_id)


def keep_separate(complaint_id: int) -> None:
    """Record that staff reviewed this report and it is distinct."""
    if not db.mark_ai_reviewed(complaint_id):
        raise TriageError("Report not found.", status_code=404)


def attach_cluster_children(queue: list[dict]) -> list[dict]:
    """Add a `children` list to each job that has linked reports (for the accordion)."""
    for job in queue:
        job["children"] = db.get_cluster_children(job["id"]) if job["duplicate_count"] > 1 else []
    return queue
