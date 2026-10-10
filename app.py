"""
CampusFix AI - University Maintenance & Issue Tracking Application.

Layers:
    routes/    HTTP only: parse input, call a service or db, render/return JSON
    services/  business rules (AI suggestions, merge validation)
    db.py      all SQL (parameterized)
    ml.py      safety scan + similarity engine with fallbacks
"""

import logging
import os

from flask import Flask, jsonify, render_template

from db import init_db
from formatting import friendly_date

logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campusfix-hackathon-dev-secret-key")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max request size

    init_db()

    app.jinja_env.filters["friendly_date"] = friendly_date

    from routes.staff import staff_bp
    from routes.submit import submit_bp
    from routes.track import track_bp

    app.register_blueprint(submit_bp)
    app.register_blueprint(track_bp)
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
