from datetime import datetime
from extensions import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    subscription_plan = db.Column(db.Text, nullable=True)
    user_limit = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, unique=True, nullable=True)
    password = db.Column(db.Text, nullable=True)
    role = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Prospect(db.Model):
    __tablename__ = "prospects"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)
    referral_source_id = db.Column(db.Integer, nullable=True)
    assigned_marketer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ReferralSource(db.Model):
    __tablename__ = "referral_sources"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    prospect_id = db.Column(db.Integer, nullable=True)
    user_name = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)
    next_step = db.Column(db.Text, nullable=True)
    note_date = db.Column(db.Date, nullable=True)
    note_time = db.Column(db.Time, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
