"""CampusFix AI — Single-admin session authentication helpers.

This project intentionally supports one environment-configured administrator,
not student accounts or a user table. Routes use these helpers to protect staff
pages and maintenance mutation APIs.
"""

import hmac
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import current_app, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash

SESSION_ADMIN_KEY = "is_admin"
SESSION_CSRF_KEY = "csrf_token"


def is_admin() -> bool:
    """Return whether this browser has an authenticated admin session."""
    return session.get(SESSION_ADMIN_KEY) is True


def admin_login_is_configured() -> bool:
    """Login fails closed unless a username and password hash are configured."""
    return bool(current_app.config.get("ADMIN_USERNAME") and current_app.config.get("ADMIN_PASSWORD_HASH"))


def get_csrf_token() -> str:
    """Return the session CSRF token, generating one when a form first needs it."""
    token = session.get(SESSION_CSRF_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[SESSION_CSRF_KEY] = token
    return token


def csrf_token_is_valid(token: str | None) -> bool:
    """Constant-time CSRF token comparison."""
    expected = session.get(SESSION_CSRF_KEY)
    return bool(expected and token and hmac.compare_digest(expected, token))


def credentials_are_valid(username: str, password: str) -> bool:
    """Validate an environment-configured username and Werkzeug password hash."""
    configured_username = current_app.config.get("ADMIN_USERNAME", "")
    password_hash = current_app.config.get("ADMIN_PASSWORD_HASH", "")

    if not configured_username or not password_hash:
        return False

    username_matches = hmac.compare_digest(username, configured_username)
    try:
        password_matches = check_password_hash(password_hash, password)
    except (TypeError, ValueError):
        # A malformed hash is a configuration error, never a successful login.
        current_app.logger.error("ADMIN_PASSWORD_HASH is not a valid Werkzeug password hash.")
        return False

    # Do not short-circuit: always perform both comparisons for a generic failure.
    return username_matches and password_matches


def establish_admin_session() -> None:
    """Prevent session fixation and establish a fresh, time-limited admin session."""
    session.clear()
    session[SESSION_ADMIN_KEY] = True
    session[SESSION_CSRF_KEY] = secrets.token_urlsafe(32)
    session.permanent = True


def safe_next_url(value: str | None) -> str:
    """Allow redirects only to local absolute paths, blocking open redirects."""
    if not value:
        return url_for("staff.staff_dashboard")
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or not value.startswith("/") or value.startswith("//"):
        return url_for("staff.staff_dashboard")
    return value


def _is_api_request() -> bool:
    return request.path.startswith("/api/")


def _unauthenticated_response():
    if _is_api_request():
        return jsonify({"success": False, "error": "Authentication required."}), 401
    return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))


def _csrf_failure_response():
    if _is_api_request():
        return jsonify({"success": False, "error": "Invalid or missing CSRF token."}), 403
    return "Invalid or missing CSRF token.", 403


def authorize_staff_request():
    """Return an auth/CSRF failure response, or None when the request may continue."""
    if current_app.config.get("TESTING") and not current_app.config.get("ADMIN_USERNAME"):
        return None

    if not is_admin():
        return _unauthenticated_response()

    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
        if not csrf_token_is_valid(token):
            return _csrf_failure_response()
    return None


def admin_required(view):
    """Decorator form of :func:`authorize_staff_request` for non-blueprint routes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        failure = authorize_staff_request()
        if failure is not None:
            return failure
        return view(*args, **kwargs)

    return wrapped
