from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_login import login_required, current_user

from .database import db
from .models import Subject, Progress, User, UserSettings
from .utils import (
    compute_hours_per_day,
    compute_subject_progress,
    compute_overall_stats,
    compute_priority_score,
)


def _build_progress_map(subjects: List[Subject], user_id: int) -> Dict[int, dict]:
    """
    Build a mapping subject_id -> aggregated progress info for a given user.
    """
    progress_entries = Progress.query.filter_by(user_id=user_id).all()
    by_subject: Dict[int, List[Progress]] = {s.id: [] for s in subjects}
    for entry in progress_entries:
        if entry.subject_id in by_subject:
            by_subject[entry.subject_id].append(entry)

    progress_map: Dict[int, dict] = {}
    for subj in subjects:
        records = by_subject.get(subj.id, [])
        progress_map[subj.id] = compute_subject_progress(subj, records)
    return progress_map


def _get_or_create_settings(user_id: int) -> UserSettings:
    """
    Fetch or create default settings for the given user.
    """
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if settings is None:
        settings = UserSettings(
            user_id=user_id,
            max_daily_hours=8.0,
            show_dashboard_tour=True,
        )
        db.session.add(settings)
        db.session.commit()
    return settings


def register_progress_routes(app: Flask) -> None:
    """
    Register progress, schedule, and statistics routes.
    """

    @app.post("/api/progress")
    @login_required
    def update_progress():
        data = request.get_json(silent=True) or {}
        subject_id = data.get("subject_id")
        hours_studied = data.get("hours_studied", 0)
        topics_completed = data.get("topics_completed") or []
        date_str = data.get("date")

        # Basic validation.
        try:
            subject_id_int = int(subject_id)
        except (TypeError, ValueError):
            return jsonify({"error": "subject_id must be an integer"}), 400

        try:
            hours_value = float(hours_studied)
        except (TypeError, ValueError):
            return jsonify({"error": "hours_studied must be a number"}), 400

        if hours_value < 0:
            return jsonify({"error": "hours_studied cannot be negative"}), 400

        if not isinstance(topics_completed, list):
            return jsonify({"error": "topics_completed must be a list"}), 400

        subject = Subject.query.filter_by(
            id=subject_id_int, user_id=current_user.id
        ).first()
        if not subject:
            return jsonify({"error": "Subject not found"}), 404

        if date_str:
            try:
                entry_date = datetime.fromisoformat(date_str).date()
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        else:
            entry_date = date.today()

        progress = Progress.query.filter_by(
            user_id=current_user.id, subject_id=subject.id, date=entry_date
        ).first()

        if not progress:
            progress = Progress(
                user_id=current_user.id,
                subject_id=subject.id,
                date=entry_date,
                hours_studied=0.0,
                topics_completed="[]",
            )
            db.session.add(progress)

        # Add to existing hours, keeping a running total for the day.
        progress.hours_studied += hours_value

        # Merge topic completions.
        try:
            existing_topics = json.loads(progress.topics_completed or "[]")
        except Exception:
            existing_topics = []
        existing_set = {str(t) for t in existing_topics}
        for t in topics_completed:
            existing_set.add(str(t))
        progress.topics_completed = json.dumps(sorted(existing_set))

        db.session.commit()

        return jsonify({"message": "Progress updated"}), 200

    @app.get("/api/progress")
    @login_required
    def get_progress():
        subjects = Subject.query.filter_by(user_id=current_user.id).all()
        progress_map = _build_progress_map(subjects, current_user.id)
        return jsonify({"progress_by_subject": progress_map})

    @app.get("/api/daily-schedule")
    @login_required
    def daily_schedule():
        subjects = Subject.query.filter_by(user_id=current_user.id).all()
        progress_map = _build_progress_map(subjects, current_user.id)
        today = date.today()
        schedule = []
        total_daily_hours = 0.0

        settings = _get_or_create_settings(current_user.id)

        for subj in subjects:
            hours_per_day = compute_hours_per_day(
                subj.exam_date, today, subj.total_hours_needed
            )
            progress_info = progress_map.get(subj.id, {})
            priority = compute_priority_score(subj, today, progress_info)
            total_daily_hours += hours_per_day

            schedule.append(
                {
                    "subject_id": subj.id,
                    "name": subj.name,
                    "exam_date": subj.exam_date.isoformat(),
                    "hours_per_day": hours_per_day,
                    "priority": priority,
                }
            )

        # Sort by priority (highest first).
        schedule.sort(key=lambda x: x["priority"], reverse=True)

        # Check for overload (default threshold: 8 hours/day).
        try:
            max_daily_hours = float(
                request.args.get("max_daily_hours", settings.max_daily_hours)
            )
        except (TypeError, ValueError):
            max_daily_hours = settings.max_daily_hours
        is_overloaded = total_daily_hours > max_daily_hours

        return jsonify(
            {
                "schedule": schedule,
                "total_daily_hours": round(total_daily_hours, 2),
                "is_overloaded": is_overloaded,
            }
        )

    @app.get("/api/week-view")
    @login_required
    def week_view():
        start_date_str = request.args.get("start")
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
            except ValueError:
                return jsonify({"error": "Invalid start date format"}), 400
        else:
            start_date = date.today()

        subjects = Subject.query.filter_by(user_id=current_user.id).all()
        progress_map = _build_progress_map(subjects, current_user.id)
        week_data = []

        for day_offset in range(7):
            current_day = date.fromordinal(start_date.toordinal() + day_offset)
            day_schedule = []

            for subj in subjects:
                progress_info = progress_map.get(subj.id, {})
                hours_studied = float(progress_info.get("total_hours_studied", 0.0))
                hours_needed = subj.total_hours_needed
                hours_remaining = max(hours_needed - hours_studied, 0.0)

                days_until_exam = (subj.exam_date - current_day).days
                if days_until_exam > 0:
                    hours_per_day = hours_remaining / float(days_until_exam)
                else:
                    hours_per_day = hours_remaining if days_until_exam == 0 else 0.0

                day_schedule.append(
                    {
                        "subject_id": subj.id,
                        "name": subj.name,
                        "hours_per_day": round(hours_per_day, 2),
                    }
                )

            week_data.append(
                {
                    "date": current_day.isoformat(),
                    "subjects": day_schedule,
                    "total_hours": round(
                        sum(s["hours_per_day"] for s in day_schedule), 2
                    ),
                }
            )

        return jsonify({"week": week_data})

    @app.get("/api/stats")
    @login_required
    def stats():
        subjects = Subject.query.filter_by(user_id=current_user.id).all()
        progress_map = _build_progress_map(subjects, current_user.id)
        stats_payload = compute_overall_stats(subjects, progress_map)
        return jsonify({"stats": stats_payload})

    @app.get("/api/history")
    @login_required
    def history():
        """
        Return recent study history for analytics: daily totals and per-subject totals.
        """
        today = date.today()
        start_date = today - timedelta(days=29)

        entries = Progress.query.filter(
            Progress.user_id == current_user.id,
            Progress.date >= start_date,
        ).all()

        daily_totals: Dict[date, float] = {}
        hours_by_subject: Dict[int, float] = {}

        for entry in entries:
            daily_totals[entry.date] = daily_totals.get(entry.date, 0.0) + float(
                entry.hours_studied
            )
            hours_by_subject[entry.subject_id] = hours_by_subject.get(
                entry.subject_id, 0.0
            ) + float(entry.hours_studied)

        # Map subject IDs to names for the current user only.
        subjects = Subject.query.filter_by(user_id=current_user.id).all()
        subject_names = {s.id: s.name for s in subjects}

        daily_list = [
            {"date": d.isoformat(), "hours": round(hours, 2)}
            for d, hours in sorted(daily_totals.items())
        ]
        by_subject_list = [
            {
                "subject_id": sid,
                "name": subject_names.get(sid, "Unknown subject"),
                "total_hours": round(hours, 2),
            }
            for sid, hours in sorted(
                hours_by_subject.items(), key=lambda item: item[1], reverse=True
            )
        ]

        return jsonify({"daily_totals": daily_list, "by_subject": by_subject_list})

    @app.get("/api/settings")
    @login_required
    def get_settings():
        settings = _get_or_create_settings(current_user.id)
        return jsonify(
            {
                "settings": {
                    "max_daily_hours": settings.max_daily_hours,
                    "show_dashboard_tour": settings.show_dashboard_tour,
                }
            }
        )

    @app.put("/api/settings")
    @login_required
    def update_settings():
        data = request.get_json(silent=True) or {}
        settings = _get_or_create_settings(current_user.id)

        if "max_daily_hours" in data:
            try:
                value = float(data["max_daily_hours"])
                if value <= 0:
                    return jsonify({"error": "max_daily_hours must be positive"}), 400
                settings.max_daily_hours = value
            except (TypeError, ValueError):
                return jsonify({"error": "max_daily_hours must be a number"}), 400

        if "show_dashboard_tour" in data:
            settings.show_dashboard_tour = bool(data["show_dashboard_tour"])

        db.session.commit()

        return jsonify(
            {
                "settings": {
                    "max_daily_hours": settings.max_daily_hours,
                    "show_dashboard_tour": settings.show_dashboard_tour,
                }
            }
        )

