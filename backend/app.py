from __future__ import annotations

import os
from datetime import timedelta

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, current_user

from .database import db, init_db
from .models import User  # models will be implemented in a separate module


login_manager = LoginManager()


def create_app(config_name: str = "development") -> Flask:
    """
    Application factory for the Study Planner backend.

    This sets up configuration, database bindings, authentication, CORS,
    and registers all API routes.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists (for SQLite database file, etc.).
    os.makedirs(app.instance_path, exist_ok=True)

    # Basic configuration – can be refactored into a separate config module later.
    app.config.update(
        SECRET_KEY=os.environ.get("STUDY_PLANNER_SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(
            app.instance_path, "study_planner.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REMEMBER_COOKIE_DURATION=timedelta(days=7),
    )

    # Initialize extensions.
    CORS(app, supports_credentials=True)
    init_db(app)

    login_manager.init_app(app)
    login_manager.login_view = "unauthorized"

    # Register route groups.
    _register_auth_routes(app)
    _register_subject_routes(app)
    _register_progress_and_stats_routes(app)
    _register_chatbot_routes(app)
    _register_frontend_routes(app)

    # Custom unauthorized handler for API endpoints.
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Authentication required"}), 401

    return app


@login_manager.user_loader
def load_user(user_id: str):
    from .models import User  # local import to avoid circular dependency

    return User.query.get(int(user_id))


def _register_auth_routes(app: Flask) -> None:
    """
    Placeholder for authentication routes.

    The concrete implementations will be added after models are defined.
    """
    from .routes_auth import register_auth_routes  # type: ignore[import-not-found]

    register_auth_routes(app)


def _register_subject_routes(app: Flask) -> None:
    from .routes_subjects import register_subject_routes  # type: ignore[import-not-found]

    register_subject_routes(app)


def _register_progress_and_stats_routes(app: Flask) -> None:
    from .routes_progress import register_progress_routes  # type: ignore[import-not-found]

    register_progress_routes(app)


def _register_chatbot_routes(app: Flask) -> None:
    from .routes_chatbot import register_chatbot_routes  # type: ignore[import-not-found]

    register_chatbot_routes(app)


def _register_frontend_routes(app: Flask) -> None:
    """
    Serve the static frontend pages from the `frontend/pages` directory.
    """

    base_frontend_dir = os.path.join(app.root_path, "..", "frontend")

    @app.route("/")
    def index():
        pages_dir = os.path.join(base_frontend_dir, "pages")
        return send_from_directory(pages_dir, "index.html")

    @app.route("/home")
    def home():
        pages_dir = os.path.join(base_frontend_dir, "pages")
        return send_from_directory(pages_dir, "home.html")

    @app.route("/dashboard")
    def dashboard_page():
        # The dashboard itself will enforce auth via API calls (401 -> redirect on frontend).
        pages_dir = os.path.join(base_frontend_dir, "pages")
        return send_from_directory(pages_dir, "dashboard.html")

    # Static asset routes for CSS, JS, and image assets served from the frontend folder.
    @app.route("/static/css/<path:filename>")
    def frontend_css(filename: str):
        css_dir = os.path.join(base_frontend_dir, "css")
        return send_from_directory(css_dir, filename)

    @app.route("/static/js/<path:filename>")
    def frontend_js(filename: str):
        js_dir = os.path.join(base_frontend_dir, "js")
        return send_from_directory(js_dir, filename)

    @app.route("/static/assets/<path:filename>")
    def frontend_assets(filename: str):
        assets_dir = os.path.join(base_frontend_dir, "assets")
        return send_from_directory(assets_dir, filename)

