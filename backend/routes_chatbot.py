from __future__ import annotations

from flask import Flask, jsonify, request
from flask_login import login_required, current_user

from .utils import get_chatbot_response


def register_chatbot_routes(app: Flask) -> None:
    """
    Register chatbot-related API routes.
    """

    @app.post("/api/chatbot")
    @login_required
    def chatbot():
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Get chatbot response
        bot_reply = get_chatbot_response(user_message, current_user.id)

        return jsonify({"reply": bot_reply}), 200
