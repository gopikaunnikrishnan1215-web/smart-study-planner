from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance, initialized with the app in create_app.
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """
    Bind the SQLAlchemy instance to the Flask app and create all tables.

    This should be called from within the application factory after the app
    configuration has been set up.
    """
    db.init_app(app)

    with app.app_context():
        db.create_all()

