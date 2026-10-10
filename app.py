"""
CampusFix AI - University Maintenance & Issue Tracking Application
Milestone 1: Application entry point with landing page and health check.
"""

from flask import Flask, render_template, jsonify

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "campusfix-hackathon-dev-secret-key"

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
            "version": "0.1.0",
            "milestone": 1,
            "message": "CampusFix AI core service is running smoothly."
        }), 200

    return app

app = create_app()

if __name__ == "__main__":
    # Development server running on port 5001 to avoid macOS AirPlay port 5000 conflict
    app.run(host="127.0.0.1", port=5001, debug=True)
