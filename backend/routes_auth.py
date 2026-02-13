from __future__ import annotations

from flask import Flask, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from .database import db
from .models import User


def register_auth_routes(app: Flask) -> None:
    """
    Register authentication-related API routes on the given Flask app.
    """

    @app.post("/api/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not username or not email or not password:
            return (
                jsonify({"error": "username, email and password are required"}),
                400,
            )

        # Enforce uniqueness.
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"error": "Username or email already in use"}), 400

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Registration successful"}), 201

    @app.post("/api/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid username or password"}), 401

        login_user(user)
        return jsonify(
            {"message": "Login successful", "user": {"id": user.id, "username": user.username}}
        )

    @app.post("/api/logout")
    @login_required
    def logout():
        logout_user()
        return jsonify({"message": "Logged out"}), 200

