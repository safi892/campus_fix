"""CampusFix AI - University Maintenance & Issue Tracking Application.

Layers:
    routes/    HTTP only: parse input, call a service or db, render/return JSON
    services/  business rules (AI suggestions, merge validation)
    db.py      all SQL (parameterized)
    ml.py      safety scan + similarity engine with fallbacks
    auth.py    one environment-configured admin session for staff endpoints
"""

import logging
import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

from db import init_db
from formatting import friendly_date

logging.basicConfig(level=logging.INFO)

# .env is optional and ignored by Git. Real deployments should provide process env vars.
load_dotenv()


def _session_secret() -> str:
    """Use an explicit secret when configured; generate a non-forgeable dev fallback."""
    configured_secret = os.environ.get("SECRET_KEY")
    if configured_secret:
        return configured_secret

    # A fresh fallback is safe against forging but signs users out after each restart.
    # Production deployments must set SECRET_KEY explicitly.
    if os.environ.get("CAMPUSFIX_ENV") == "production":
        raise RuntimeError("SECRET_KEY must be configured in production.")
    logging.getLogger("campusfix.app").warning(
        "SECRET_KEY is not configured; using an ephemeral development secret."
    )
    return secrets.token_urlsafe(48)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=_session_secret(),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 MB max request size
        ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME"),
        ADMIN_PASSWORD_HASH=os.environ.get("ADMIN_PASSWORD_HASH"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )

    init_db()
    app.jinja_env.filters["friendly_date"] = friendly_date

    from routes.auth import auth_bp
    from routes.staff import staff_bp
    from routes.submit import submit_bp
    from routes.track import track_bp

    app.register_blueprint(submit_bp)
    app.register_blueprint(track_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(staff_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "app": "CampusFix AI",
            "version": "0.3.0",
            "milestone": 3,
            "message": "CampusFix AI core service is running smoothly.",
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    # Port 5001 avoids the macOS AirPlay conflict on 5000.
    app.run(host="127.0.0.1", port=5001, debug=True)
