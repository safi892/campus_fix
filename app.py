"""
CampusFix AI - University Maintenance & Issue Tracking Application
Milestone 2: Complete complaint submission and tracking system.
"""

import os
from flask import Flask, render_template, jsonify

from db import init_db

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campusfix-hackathon-dev-secret-key")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max request size
    
    # Initialize database on first request
    with app.app_context():
        init_db()
    
    # Register blueprints
    from routes.submit import submit_bp
    from routes.track import track_bp
    
    app.register_blueprint(submit_bp)
    app.register_blueprint(track_bp)

    @app.route("/")
    def index():
        """Render the landing page."""
        return render_template("index.html")

    @app.route("/health")
    def health_check():
        """
        Health check endpoint.
        Returns system status and basic application metadata.
        """
        return jsonify({
            "status": "healthy",
            "app": "CampusFix AI",
            "version": "0.2.0",
            "milestone": 2,
            "message": "CampusFix AI core service is running smoothly."
        }), 200

    return app

app = create_app()

if __name__ == "__main__":
    # Development server running on port 5001 to avoid macOS AirPlay port 5000 conflict
    app.run(host="127.0.0.1", port=5001, debug=True)
