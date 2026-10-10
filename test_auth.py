"""CampusFix AI — admin session and CSRF protection tests.

Run: .venv/bin/python -m unittest test_auth -v
"""

import os
import tempfile
import unittest

import db
from app import app
from werkzeug.security import generate_password_hash

ADMIN_USERNAME = "admin-test"
ADMIN_PASSWORD = "long-test-password"


class AdminAuthTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._original_db_path = db.DB_PATH
        self._original_config = {
            key: app.config.get(key)
            for key in ("ADMIN_USERNAME", "ADMIN_PASSWORD_HASH", "SECRET_KEY")
        }
        db.DB_PATH = os.path.join(self._tmp.name, "auth.db")
        db.init_db()
        app.config.update(
            ADMIN_USERNAME=ADMIN_USERNAME,
            ADMIN_PASSWORD_HASH=generate_password_hash(ADMIN_PASSWORD),
            SECRET_KEY="auth-tests-secret",
        )
        self.client = app.test_client()

    def tearDown(self):
        app.config.update(self._original_config)
        db.DB_PATH = self._original_db_path
        self._tmp.cleanup()

    def _login_csrf_token(self):
        response = self.client.get("/staff/login")
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def _authenticated_session(self, csrf_token="api-test-csrf-token"):
        with self.client.session_transaction() as session:
            session["is_admin"] = True
            session["csrf_token"] = csrf_token
        return csrf_token

    def test_staff_pages_redirect_when_anonymous(self):
        for url in ("/staff", "/analytics"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/staff/login?next=", response.location)

    def test_staff_api_returns_json_401_when_anonymous(self):
        response = self.client.post("/api/status/update", json={"id": 1, "status": "Resolved"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["success"], False)
        self.assertEqual(response.get_json()["error"], "Authentication required.")

    def test_login_succeeds_with_valid_credentials(self):
        csrf_token = self._login_csrf_token()
        response = self.client.post("/staff/login", data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "csrf_token": csrf_token,
            "next": "/analytics",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/analytics")
        with self.client.session_transaction() as session:
            self.assertTrue(session["is_admin"])
            self.assertNotEqual(session["csrf_token"], csrf_token)

    def test_login_failure_is_generic_and_does_not_authenticate(self):
        csrf_token = self._login_csrf_token()
        response = self.client.post("/staff/login", data={
            "username": ADMIN_USERNAME,
            "password": "wrong-password",
            "csrf_token": csrf_token,
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid username or password.", response.data)
        self.assertNotIn(b"wrong-password", response.data)
        with self.client.session_transaction() as session:
            self.assertNotIn("is_admin", session)

    def test_login_rejects_missing_csrf_token(self):
        self._login_csrf_token()
        response = self.client.post("/staff/login", data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
        })
        self.assertEqual(response.status_code, 403)

    def test_login_blocks_open_redirect(self):
        csrf_token = self._login_csrf_token()
        response = self.client.post("/staff/login", data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "csrf_token": csrf_token,
            "next": "https://evil.example",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/staff")

    def test_staff_api_requires_csrf_after_login(self):
        self._authenticated_session()
        response = self.client.post("/api/status/update", json={"id": 1, "status": "Resolved"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["success"], False)

    def test_staff_api_accepts_valid_csrf_token(self):
        token = self._authenticated_session()
        response = self.client.post(
            "/api/status/update",
            json={"id": 99999, "status": "Resolved"},
            headers={"X-CSRF-Token": token},
        )
        # Authentication and CSRF succeeded; business validation reports missing data.
        self.assertEqual(response.status_code, 404)

    def test_logout_requires_csrf_and_clears_session(self):
        token = self._authenticated_session()
        bad_response = self.client.post("/staff/logout", data={})
        self.assertEqual(bad_response.status_code, 403)

        response = self.client.post("/staff/logout", data={"csrf_token": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/staff/login")
        with self.client.session_transaction() as session:
            self.assertNotIn("is_admin", session)

    def test_unconfigured_login_fails_closed(self):
        app.config.update(ADMIN_USERNAME=None, ADMIN_PASSWORD_HASH=None)
        response = self.client.get("/staff/login")
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"not configured", response.data)


if __name__ == "__main__":
    unittest.main()
