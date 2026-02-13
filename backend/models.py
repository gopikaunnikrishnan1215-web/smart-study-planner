from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from flask_login import UserMixin

from .database import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    subjects = db.relationship("Subject", back_populates="user", cascade="all, delete")
    progress_entries = db.relationship(
        "Progress", back_populates="user", cascade="all, delete"
    )
    settings = db.relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.username}>"


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    total_hours_needed = db.Column(db.Float, nullable=False)
    # Stored as JSON-encoded list of strings for simplicity.
    topics = db.Column(db.Text, nullable=False, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="subjects")
    progress_entries = db.relationship(
        "Progress", back_populates="subject", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Subject {self.name} (user={self.user_id})>"


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    hours_studied = db.Column(db.Float, nullable=False, default=0.0)
    # JSON-encoded list of topic strings that have been completed on or before this date.
    topics_completed = db.Column(db.Text, nullable=False, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="progress_entries")
    subject = db.relationship("Subject", back_populates="progress_entries")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Progress user={self.user_id} subject={self.subject_id} date={self.date}>"


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    max_daily_hours = db.Column(db.Float, nullable=False, default=8.0)
    show_dashboard_tour = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="settings")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<UserSettings user={self.user_id} max_daily_hours={self.max_daily_hours}>"

