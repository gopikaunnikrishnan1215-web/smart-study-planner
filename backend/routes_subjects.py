from __future__ import annotations

import json
from datetime import date, datetime
from typing import List

from flask import Flask, jsonify, request
from flask_login import login_required, current_user

from .database import db
from .models import Subject, Progress
from .utils import compute_hours_per_day, compute_subject_progress


def _subject_to_dict(subject: Subject, include_progress: bool = False) -> dict:
    topics: List[str]
    try:
        topics = json.loads(subject.topics or "[]")
    except Exception:
        topics = []

    subj_dict = {
        "id": subject.id,
        "name": subject.name,
        "exam_date": subject.exam_date.isoformat(),
        "total_hours_needed": subject.total_hours_needed,
        "topics": topics,
    }

    if include_progress:
        progress_records = Progress.query.filter_by(
            user_id=subject.user_id, subject_id=subject.id
        ).all()
        stats = compute_subject_progress(subject, progress_records)
        subj_dict["progress"] = stats

    # Always provide today's suggested hours-per-day for convenience.
    subj_dict["hours_per_day"] = compute_hours_per_day(
        subject.exam_date, date.today(), subject.total_hours_needed
    )

    return subj_dict


def register_subject_routes(app: Flask) -> None:
    """
    Register subject management routes on the app.
    """

    @app.get("/api/subjects")
    @login_required
    def list_subjects():
        subjects = Subject.query.filter_by(user_id=current_user.id).all()
        return jsonify(
            {"subjects": [_subject_to_dict(subj, include_progress=True) for subj in subjects]}
        )

    @app.post("/api/subjects")
    @login_required
    def create_subject():
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        exam_date_str = data.get("exam_date") or ""
        total_hours_needed = data.get("total_hours_needed")
        topics = data.get("topics") or []

        if not name or not exam_date_str or total_hours_needed is None:
            return (
                jsonify(
                    {
                        "error": "name, exam_date, and total_hours_needed are required",
                    }
                ),
                400,
            )

        try:
            exam_date = datetime.fromisoformat(exam_date_str).date()
        except ValueError:
            return jsonify({"error": "Invalid exam_date format"}), 400

        try:
            total_hours = float(total_hours_needed)
        except (TypeError, ValueError):
            return jsonify({"error": "total_hours_needed must be a number"}), 400

        if total_hours <= 0:
            return jsonify({"error": "total_hours_needed must be positive"}), 400

        if not isinstance(topics, list):
            return jsonify({"error": "topics must be a list"}), 400

        subject = Subject(
            user_id=current_user.id,
            name=name,
            exam_date=exam_date,
            total_hours_needed=total_hours,
            topics=json.dumps([str(t).strip() for t in topics if str(t).strip()]),
        )
        db.session.add(subject)
        db.session.commit()

        return jsonify({"subject": _subject_to_dict(subject)}), 201

