"""
CampusFix AI — Milestone 2 route tests.
Runs against a throwaway SQLite file so demo data is never touched.

Run:  python3 -m unittest test_routes -v
"""

import contextlib
import io
import os
import tempfile
import unittest

import db
import seed
from app import app

VALID_FORM = {
    "title": "Projector bulb burnt out",
    "description": "The projector in this room has a dead bulb and cannot be used.",
    "building": "Engineering Complex",
    "room": "Room 101",
    "category": "Electrical",
}


class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls._original_path = db.DB_PATH
        db.DB_PATH = os.path.join(cls._tmp.name, "test.db")
        with contextlib.redirect_stdout(io.StringIO()):
            seed.seed_demo_data()
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        db.DB_PATH = cls._original_path
        cls._tmp.cleanup()

    # --- basic pages -------------------------------------------------
    def test_health(self):
        self.assertEqual(self.client.get("/health").status_code, 200)

    def test_submit_form_renders(self):
        response = self.client.get("/submit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Report a Campus Issue", response.data)

    # --- tracking ----------------------------------------------------
    def test_track_existing(self):
        response = self.client.get("/track/CFX-2026-1001")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CFX-2026-1001", response.data)
        self.assertIn(b"Linked with <strong>4 other reports</strong>", response.data)

    def test_track_child_shows_parent_cluster(self):
        response = self.client.get("/track/CFX-2026-1003")
        self.assertIn(b"Linked with <strong>4 other reports</strong>", response.data)

    def test_track_missing_returns_404(self):
        self.assertEqual(self.client.get("/track/CFX-0000-0000").status_code, 404)

    def test_track_safety_hazard_badge(self):
        response = self.client.get("/track/CFX-2026-3001")
        self.assertIn(b"safety-pulse", response.data)

    # --- submission --------------------------------------------------
    def test_submit_valid_redirects_to_track(self):
        response = self.client.post("/submit", data=VALID_FORM)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/track/CFX-2026-", response.location)
        self.assertEqual(self.client.get(response.location).status_code, 200)

    def test_submit_hazard_is_critical(self):
        form = {**VALID_FORM, "title": "Sparks from wall socket",
                "description": "Sparks fly every time I plug anything into it."}
        response = self.client.post("/submit", data=form)
        page = self.client.get(response.location).data
        self.assertIn(b"Critical Priority", page)
        self.assertIn(b"Safety Hazard", page)

    def test_submit_fire_title_is_critical(self):
        form = {**VALID_FORM, "title": "fire here",
                "description": "Small fire reported in the lab."}
        response = self.client.post("/submit", data=form)
        page = self.client.get(response.location).data
        self.assertIn(b"Critical Priority", page)
        self.assertIn(b"Safety Hazard", page)

    def test_submit_invalid_category_rejected(self):
        response = self.client.post("/submit", data={**VALID_FORM, "category": "Hacking"})
        self.assertEqual(response.status_code, 400)

    def test_submit_invalid_building_rejected(self):
        response = self.client.post("/submit", data={**VALID_FORM, "building": "Moon Base"})
        self.assertEqual(response.status_code, 400)

    def test_submit_short_title_rejected(self):
        response = self.client.post("/submit", data={**VALID_FORM, "title": "abc"})
        self.assertEqual(response.status_code, 400)

    def test_xss_is_escaped(self):
        payload = "<script>alert(1)</script> broken light"
        response = self.client.post("/submit", data={**VALID_FORM, "title": payload})
        page = self.client.get(response.location).data
        self.assertNotIn(b"<script>alert(1)</script>", page)
        self.assertIn(b"&lt;script&gt;", page)

    def test_sql_injection_string_is_harmless(self):
        response = self.client.get("/track/x'%20OR%20'1'='1")
        self.assertEqual(response.status_code, 404)

    # --- duplicate peek API -----------------------------------------
    def test_duplicate_api_finds_cluster(self):
        response = self.client.get(
            "/api/check-duplicates",
            query_string={"building": "Engineering Complex",
                          "query": "air conditioning blowing hot air room 204"},
        )
        self.assertEqual(response.status_code, 200)
        matches = response.get_json()["similar_complaints"]
        self.assertTrue(matches)
        self.assertEqual(matches[0]["reference_code"], "CFX-2026-1001")

    def test_duplicate_api_rejects_bad_building(self):
        response = self.client.get(
            "/api/check-duplicates", query_string={"building": "X", "query": "something long enough"}
        )
        self.assertEqual(response.status_code, 400)

    # --- data safety -------------------------------------------------
    def test_seed_counts_and_no_deletion(self):
        complaints = db.get_all_complaints(limit=1000)
        self.assertGreaterEqual(len(complaints), 16)
        parent = db.get_complaint_by_reference("CFX-2026-1001")
        self.assertEqual(parent["duplicate_count"], 5)

    # --- dataset categories & fields from CSV ------------------------
    def test_submit_csv_dataset_fields(self):
        form_data = {
            "title": "Water cooler outside Lab2 broken",
            "description": "The water cooler outside Lab2 is not giving any cold water since morning.",
            "location": "Lab2",
            "room": "Beside entrance",
            "category": "Plumbing and water",
            "user_type": "teacher",
        }
        response = self.client.post("/submit", data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # Follow to tracking receipt
        page = self.client.get(response.location).data
        self.assertIn(b"Plumbing and water", page)
        self.assertIn(b"Lab2", page)
        self.assertIn(b"Teacher", page)

    def test_submit_it_category_in_lecture_theater(self):
        form_data = {
            "title": "Projector displays blue screen in LT3",
            "description": "Projector in LT3 is not displaying lecture slides properly.",
            "location": "LT3",
            "category": "IT",
            "user_type": "student",
        }
        response = self.client.post("/submit", data=form_data)
        self.assertEqual(response.status_code, 302)
        page = self.client.get(response.location).data
        self.assertIn(b"IT", page)
        self.assertIn(b"LT3", page)


if __name__ == "__main__":
    unittest.main()
