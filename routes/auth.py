"""CampusFix AI — Single environment-configured admin login routes."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from auth import (
    admin_login_is_configured,
    credentials_are_valid,
    csrf_token_is_valid,
    establish_admin_session,
    get_csrf_token,
    is_admin,
    safe_next_url,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/staff/login", methods=["GET", "POST"])
def login():
    """Render and process the single-admin login form."""
    next_url = safe_next_url(request.values.get("next"))

    if is_admin():
        return redirect(next_url)

    if not admin_login_is_configured():
        current_app.logger.error("Admin login is unavailable: missing ADMIN_USERNAME or ADMIN_PASSWORD_HASH.")
        return render_template(
            "login.html",
            csrf_token=get_csrf_token(),
            next_url=next_url,
            configuration_error=True,
        ), 503

    if request.method == "POST":
        if not csrf_token_is_valid(request.form.get("csrf_token")):
            return render_template(
                "login.html",
                csrf_token=get_csrf_token(),
                next_url=next_url,
                error="Your session expired. Please try again.",
            ), 403

        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if credentials_are_valid(username, password):
            establish_admin_session()
            return redirect(next_url)

        # Intentionally generic: never disclose whether username or password failed.
        return render_template(
            "login.html",
            csrf_token=get_csrf_token(),
            next_url=next_url,
            error="Invalid username or password.",
        ), 401

    return render_template("login.html", csrf_token=get_csrf_token(), next_url=next_url)


@auth_bp.route("/staff/logout", methods=["POST"])
def logout():
    """End the admin session. A CSRF-protected POST prevents logout CSRF."""
    if not csrf_token_is_valid(request.form.get("csrf_token")):
        return "Invalid or missing CSRF token.", 403

    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
