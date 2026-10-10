"""
CampusFix AI — Milestone 3 staff feature tests.
Each test gets a fresh, freshly seeded SQLite file because these tests mutate data.

Run:  python3 -m unittest test_staff_routes -v
"""

import contextlib
import io
import os
import tempfile
import unittest

import db
import seed
from app import app
from services import triage

ENG = "Engineering Complex"
AC_PARENT_REF = "CFX-2026-1001"
AC_CHILD_REF = "CFX-2026-1002"


class StaffTestCase(unittest.TestCase):
    """Fresh seeded database per test, with small helpers."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._original_path = db.DB_PATH
        db.DB_PATH = os.path.join(self._tmp.name, "test.db")
        with contextlib.redirect_stdout(io.StringIO()):
            seed.seed_demo_data()
        self.client = app.test_client()

    def tearDown(self):
        db.DB_PATH = self._original_path
        self._tmp.cleanup()

    # --- helpers -----------------------------------------------------
    def _post_json(self, url, payload):
        return self.client.post(url, json=payload)

    def _id(self, reference_code):
        return db.get_complaint_by_reference(reference_code)["id"]

    def _insert(self, ref, title, description, building=ENG, room="Room 204",
                category="HVAC", urgency="Normal", safety_hazard=0):
        return db.insert_complaint(ref, title, description, building, room,
                                   category, urgency, safety_hazard)

    def _insert_ac_duplicate(self, ref="CFX-2026-9001"):
        """A standalone report that the AI should pair with the AC cluster."""
        return self._insert(
            ref,
            "Air conditioning blowing hot air in room 204",
            "The AC in Engineering Room 204 is broken and blowing warm air, the room is boiling hot.",
        )

    def _row_count(self):
        return len(db.get_all_complaints(limit=10_000))


# ---------------------------------------------------------------------------
# /staff dashboard
# ---------------------------------------------------------------------------
class StaffDashboardTests(StaffTestCase):
    def test_dashboard_renders(self):
        """Dashboard loads with its main sections."""
        response = self.client.get("/staff")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Maintenance Triage Board", response.data)
        self.assertIn(b"AI Duplicate Review", response.data)

    def test_queue_orders_safety_first(self):
        """The safety-hazard job is listed before the largest cluster."""
        page = self.client.get("/staff").data
        self.assertIn(b"CFX-2026-3001", page)
        self.assertIn(b"CFX-2026-1001", page)
        self.assertLess(page.index(b"CFX-2026-3001"), page.index(b"CFX-2026-1001"))

    def test_queue_db_order(self):
        """get_staff_queue returns only parents, hazards first, then by cluster size."""
        refs = [job["reference_code"] for job in db.get_staff_queue()]
        self.assertEqual(refs, ["CFX-2026-3001", "CFX-2026-1001", "CFX-2026-2001",
                                "CFX-2026-5001", "CFX-2026-4001"])

    def test_building_filter_narrows(self):
        """Building filter shows only that building's jobs."""
        page = self.client.get("/staff", query_string={"building": "Central Library"}).data
        self.assertIn(b"CFX-2026-2001", page)
        self.assertNotIn(b"CFX-2026-1001", page)
        self.assertNotIn(b"CFX-2026-3001", page)

    def test_invalid_filter_ignored(self):
        """Values outside the allowlist are ignored, not errors."""
        response = self.client.get("/staff", query_string={
            "building": "Moon Base", "category": "Hacking", "status": "'; DROP TABLE complaints;--"})
        self.assertEqual(response.status_code, 200)
        for ref in (b"CFX-2026-1001", b"CFX-2026-2001", b"CFX-2026-3001",
                    b"CFX-2026-4001", b"CFX-2026-5001"):
            self.assertIn(ref, response.data)

    def test_resolved_filter_shows_no_seeded_jobs(self):
        """No seeded job is resolved, so the Resolved filter is empty."""
        page = self.client.get("/staff", query_string={"status": "Resolved"}).data
        self.assertIn(b"No jobs match these filters.", page)
        self.assertNotIn(b"CFX-2026-1001", page)

    def test_resolved_jobs_hidden_by_default(self):
        """A resolved job leaves the default queue but appears under the Resolved filter."""
        self._post_json("/api/status/update", {"id": self._id(AC_PARENT_REF), "status": "Resolved"})
        self.assertNotIn(b"CFX-2026-1001", self.client.get("/staff").data)
        page = self.client.get("/staff", query_string={"status": "Resolved"}).data
        self.assertIn(b"CFX-2026-1001", page)

    def test_no_suggestions_after_plain_seed(self):
        """All seeded children are linked, so the AI has nothing to propose."""
        self.assertEqual(triage.build_duplicate_suggestions(), [])
        self.assertNotIn(b"js-suggestion", self.client.get("/staff").data)

    def test_suggestion_pairs_near_duplicate_with_ac_cluster(self):
        """A new AC report in the same building is proposed for the AC cluster."""
        candidate_id = self._insert_ac_duplicate()
        suggestions = triage.build_duplicate_suggestions(ENG)
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["candidate"]["id"], candidate_id)
        self.assertEqual(suggestions[0]["parent"]["reference_code"], AC_PARENT_REF)
        self.assertGreaterEqual(suggestions[0]["similarity"], triage.SIMILARITY_THRESHOLD)

    def test_suggestion_card_rendered(self):
        """The review deck shows the suggestion with both actions."""
        candidate_id = self._insert_ac_duplicate()
        page = self.client.get("/staff").data
        self.assertIn(b"js-suggestion", page)
        self.assertIn(b"Accept Merge", page)
        self.assertIn(b"Keep Separate", page)
        self.assertIn(f'data-child-id="{candidate_id}"'.encode(), page)
        self.assertIn(f'data-parent-id="{self._id(AC_PARENT_REF)}"'.encode(), page)

    def test_children_accordion_lists_child_refs(self):
        """Linked student reports are listed under their parent job."""
        page = self.client.get("/staff").data
        for ref in (b"CFX-2026-1002", b"CFX-2026-1003", b"CFX-2026-1004", b"CFX-2026-1005"):
            self.assertIn(ref, page)
        self.assertIn(b"Show 4 linked student reports", page)

    def test_xss_title_escaped(self):
        """User-supplied titles are HTML-escaped on the staff board."""
        self._insert("CFX-2026-9666", "<script>alert(1)</script> AC broken",
                     "The AC in room 204 is broken and blowing hot air.")
        page = self.client.get("/staff").data
        self.assertNotIn(b"<script>alert(1)</script>", page)
        self.assertIn(b"&lt;script&gt;alert(1)&lt;/script&gt;", page)


# ---------------------------------------------------------------------------
# POST /api/status/update
# ---------------------------------------------------------------------------
class StatusUpdateTests(StaffTestCase):
    URL = "/api/status/update"

    def test_success_shape(self):
        parent_id = self._id(AC_PARENT_REF)
        response = self._post_json(self.URL, {"id": parent_id, "status": "In Progress"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(),
                         {"success": True, "id": parent_id, "status": "In Progress"})
        self.assertEqual(db.get_complaint_by_id(parent_id)["status"], "In Progress")

    def test_cascades_to_children(self):
        """Every linked student report follows the job status, including its tracker."""
        self._post_json(self.URL, {"id": self._id(AC_PARENT_REF), "status": "In Progress"})
        for child in db.get_cluster_children(self._id(AC_PARENT_REF)):
            self.assertEqual(child["status"], "In Progress")
        page = self.client.get(f"/track/{AC_CHILD_REF}").data
        self.assertIn(b"status-progress", page)

    def test_does_not_touch_other_clusters(self):
        self._post_json(self.URL, {"id": self._id(AC_PARENT_REF), "status": "Resolved"})
        self.assertEqual(db.get_complaint_by_reference("CFX-2026-2002")["status"], "Under Review")

    def test_invalid_status_400(self):
        response = self._post_json(self.URL, {"id": self._id(AC_PARENT_REF), "status": "Done"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])
        self.assertIn("error", response.get_json())

    def test_unknown_id_404(self):
        response = self._post_json(self.URL, {"id": 99999, "status": "Resolved"})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.get_json()["success"])

    def test_bool_id_400(self):
        response = self._post_json(self.URL, {"id": True, "status": "Resolved"})
        self.assertEqual(response.status_code, 400)

    def test_string_and_negative_ids_400(self):
        for bad in ("1", 0, -3, 1.5, None):
            with self.subTest(id=bad):
                response = self._post_json(self.URL, {"id": bad, "status": "Resolved"})
                self.assertEqual(response.status_code, 400)

    def test_form_encoded_body_400(self):
        """Only JSON is accepted (blocks cross-site HTML form posts)."""
        response = self.client.post(self.URL, data={"id": "1", "status": "Resolved"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_non_object_json_400(self):
        response = self._post_json(self.URL, [1, "Resolved"])
        self.assertEqual(response.status_code, 400)

    def test_non_string_status_400(self):
        """Unhashable values must be rejected, not crash with a 500."""
        for bad in (["Resolved"], {"s": 1}, 5, None):
            with self.subTest(status=bad):
                response = self._post_json(self.URL, {"id": self._id(AC_PARENT_REF), "status": bad})
                self.assertEqual(response.status_code, 400)

    def test_child_status_update_rejected_409(self):
        """A cluster keeps one status: children can't be updated on their own."""
        response = self._post_json(self.URL, {"id": self._id(AC_CHILD_REF), "status": "Resolved"})
        self.assertEqual(response.status_code, 409)
        self.assertNotEqual(db.get_complaint_by_reference(AC_CHILD_REF)["status"], "Resolved")


# ---------------------------------------------------------------------------
# POST /api/cluster/merge
# ---------------------------------------------------------------------------
class ClusterMergeTests(StaffTestCase):
    URL = "/api/cluster/merge"

    def test_merge_success(self):
        """Merging the candidate grows the cluster without deleting any row."""
        parent_id = self._id(AC_PARENT_REF)
        child_id = self._insert_ac_duplicate()
        rows_before = self._row_count()

        response = self._post_json(self.URL, {"parent_id": parent_id, "child_id": child_id})
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["success"])
        self.assertEqual(body["parent_id"], parent_id)
        self.assertEqual(body["child_id"], child_id)
        self.assertEqual(body["new_count"], 6)
        self.assertIn("message", body)

        child = db.get_complaint_by_id(child_id)
        self.assertIsNotNone(child)
        self.assertEqual(child["parent_id"], parent_id)
        self.assertEqual(child["reference_code"], "CFX-2026-9001")
        self.assertEqual(child["status"], db.get_complaint_by_id(parent_id)["status"])
        self.assertEqual(self._row_count(), rows_before)
        self.assertEqual(db.get_complaint_by_id(parent_id)["duplicate_count"], 6)

    def test_merged_report_leaves_suggestions_and_tracks_cluster(self):
        parent_id = self._id(AC_PARENT_REF)
        child_id = self._insert_ac_duplicate()
        self._post_json(self.URL, {"parent_id": parent_id, "child_id": child_id})
        self.assertEqual(triage.build_duplicate_suggestions(ENG), [])
        page = self.client.get("/track/CFX-2026-9001").data
        self.assertIn(b"Linked with <strong>5 other reports</strong>", page)

    def test_self_merge_400(self):
        parent_id = self._id(AC_PARENT_REF)
        response = self._post_json(self.URL, {"parent_id": parent_id, "child_id": parent_id})
        self.assertEqual(response.status_code, 400)

    def test_missing_ids_404(self):
        parent_id = self._id(AC_PARENT_REF)
        for payload in ({"parent_id": 99999, "child_id": parent_id},
                        {"parent_id": parent_id, "child_id": 99999}):
            with self.subTest(payload=payload):
                self.assertEqual(self._post_json(self.URL, payload).status_code, 404)

    def test_already_linked_child_409(self):
        response = self._post_json(self.URL, {"parent_id": self._id(AC_PARENT_REF),
                                              "child_id": self._id(AC_CHILD_REF)})
        self.assertEqual(response.status_code, 409)

    def test_parent_is_child_409(self):
        response = self._post_json(self.URL, {"parent_id": self._id(AC_CHILD_REF),
                                              "child_id": self._insert_ac_duplicate()})
        self.assertEqual(response.status_code, 409)

    def test_child_with_own_cluster_409(self):
        response = self._post_json(self.URL, {"parent_id": self._id("CFX-2026-2001"),
                                              "child_id": self._id("CFX-2026-5001")})
        self.assertEqual(response.status_code, 409)

    def test_cross_building_400(self):
        child_id = self._insert_ac_duplicate()
        response = self._post_json(self.URL, {"parent_id": self._id("CFX-2026-2001"),
                                              "child_id": child_id})
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(db.get_complaint_by_id(child_id)["parent_id"])

    def test_resolved_parent_rejected_409(self):
        parent_id = self._id(AC_PARENT_REF)
        self._post_json("/api/status/update", {"id": parent_id, "status": "Resolved"})
        response = self._post_json(self.URL, {"parent_id": parent_id,
                                              "child_id": self._insert_ac_duplicate()})
        self.assertEqual(response.status_code, 409)

    def test_db_link_is_atomic_against_double_merge(self):
        """Linking the same child twice at the DB layer fails instead of double-counting."""
        parent_id = self._id(AC_PARENT_REF)
        child_id = self._insert_ac_duplicate()
        self.assertEqual(db.link_duplicate(child_id, parent_id), 6)
        with self.assertRaises(db.AlreadyLinkedError):
            db.link_duplicate(child_id, parent_id)
        self.assertEqual(db.get_complaint_by_id(parent_id)["duplicate_count"], 6)

    def test_missing_field_400(self):
        response = self._post_json(self.URL, {"parent_id": self._id(AC_PARENT_REF)})
        self.assertEqual(response.status_code, 400)

    def test_safety_hazard_escalates_parent(self):
        """A hazard merged into a non-hazard job makes the job Critical."""
        parent_id = self._id(AC_PARENT_REF)
        self.assertEqual(db.get_complaint_by_id(parent_id)["safety_hazard"], 0)
        hazard_id = self._insert("CFX-2026-9002", "Sparks from AC vent in room 204",
                                 "Sparks are coming out of the AC vent in Engineering Room 204.",
                                 urgency="Critical", safety_hazard=1)
        response = self._post_json(self.URL, {"parent_id": parent_id, "child_id": hazard_id})
        self.assertEqual(response.status_code, 200)
        parent = db.get_complaint_by_id(parent_id)
        self.assertEqual(parent["safety_hazard"], 1)
        self.assertEqual(parent["urgency"], "Critical")


# ---------------------------------------------------------------------------
# POST /api/cluster/dismiss
# ---------------------------------------------------------------------------
class ClusterDismissTests(StaffTestCase):
    URL = "/api/cluster/dismiss"

    def test_dismiss_success_and_hidden_from_suggestions(self):
        candidate_id = self._insert_ac_duplicate()
        self.assertTrue(triage.build_duplicate_suggestions(ENG))

        response = self._post_json(self.URL, {"complaint_id": candidate_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True})

        candidates = [s["candidate"]["id"] for s in triage.build_duplicate_suggestions()]
        self.assertNotIn(candidate_id, candidates)
        self.assertEqual(db.get_complaint_by_id(candidate_id)["ai_reviewed"], 1)
        self.assertIsNone(db.get_complaint_by_id(candidate_id)["parent_id"])

    def test_dismiss_unknown_id_404(self):
        response = self._post_json(self.URL, {"complaint_id": 99999})
        self.assertEqual(response.status_code, 404)

    def test_dismiss_bad_id_400(self):
        self.assertEqual(self._post_json(self.URL, {"complaint_id": "abc"}).status_code, 400)


# ---------------------------------------------------------------------------
# /analytics
# ---------------------------------------------------------------------------
class AnalyticsTests(StaffTestCase):
    def test_analytics_renders_banner(self):
        response = self.client.get("/analytics")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"16 student reports", response.data)
        self.assertIn(b"5 actionable repair jobs", response.data)
        self.assertIn(b"68.8% workload reduction", response.data)

    def test_hotspot_numbers(self):
        stats = db.get_hotspot_analytics()
        self.assertEqual(stats["total_reports"], 16)
        self.assertEqual(stats["consolidated_jobs"], 5)
        self.assertEqual(stats["workload_reduction_pct"], 68.8)
        self.assertEqual(stats["safety_hazards_count"], 2)
        self.assertEqual(stats["active_hazard_jobs"], 1)
        self.assertEqual(stats["resolved_jobs"], 0)
        self.assertEqual(stats["pending_jobs"], 5)
        self.assertEqual(len(stats["building_stats"]), 5)
        self.assertEqual(stats["building_stats"][0]["building"], ENG)
        self.assertEqual(stats["building_stats"][0]["total_reports"], 5)

    def test_resolving_updates_analytics(self):
        self._post_json("/api/status/update", {"id": self._id(AC_PARENT_REF), "status": "Resolved"})
        stats = db.get_hotspot_analytics()
        self.assertEqual(stats["resolved_jobs"], 1)
        self.assertEqual(stats["pending_jobs"], 4)
        eng = next(r for r in stats["building_stats"] if r["building"] == ENG)
        self.assertEqual(eng["resolved_reports"], 5)

    def test_empty_database(self):
        """No reports: zeros everywhere, no ZeroDivisionError, pages still render."""
        db.reset_database()
        stats = db.get_hotspot_analytics()
        for key in ("total_reports", "consolidated_jobs", "workload_reduction_pct",
                    "safety_hazards_count", "active_hazard_jobs", "resolved_jobs", "pending_jobs"):
            self.assertEqual(stats[key], 0, key)
        self.assertEqual(stats["building_stats"], [])
        self.assertEqual(stats["category_stats"], [])
        self.assertEqual(self.client.get("/analytics").status_code, 200)
        self.assertEqual(self.client.get("/staff").status_code, 200)


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
class NavigationTests(StaffTestCase):
    def test_home_links_to_staff_pages(self):
        page = self.client.get("/").data
        self.assertIn(b'href="/staff"', page)
        self.assertIn(b'href="/analytics"', page)


if __name__ == "__main__":
    unittest.main()
