from datetime import datetime
from extensions import db


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    admin_email = db.Column(db.String(255), unique=True, nullable=False)
    crm_type = db.Column(db.String(50), nullable=False)  # pro, gold, max
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship("User", backref="tenant", lazy=True, cascade="all, delete-orphan")
    subscriptions = db.relationship("Subscription", backref="tenant", lazy=True, cascade="all, delete-orphan")
    referral_sources = db.relationship("ReferralSource", backref="tenant", lazy=True, cascade="all, delete-orphan")
    prospects = db.relationship("Prospect", backref="tenant", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Note", backref="tenant", lazy=True, cascade="all, delete-orphan")
    family_communications = db.relationship("FamilyCommunication", backref="tenant", lazy=True, cascade="all, delete-orphan")
    evv_logs = db.relationship("EVVLog", backref="tenant", lazy=True, cascade="all, delete-orphan")
    mileage_logs = db.relationship("MileageLog", backref="tenant", lazy=True, cascade="all, delete-orphan")
    staff_tracking_logs = db.relationship("StaffTracking", backref="tenant", lazy=True, cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", backref="tenant", lazy=True, cascade="all, delete-orphan")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False)  # admin, marketer, nurse, caregiver
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    crm_type = db.Column(db.String(50), nullable=False)  # pro, gold, max
    seat_limit = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), nullable=False, default="active")  # active, past_due, suspended, cancelled
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ReferralSource(db.Model):
    __tablename__ = "referral_sources"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    business_name = db.Column(db.String(255), nullable=False)
    ref_status = db.Column(db.String(50), nullable=False, default="Green")  # Green, Red
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Prospect(db.Model):
    __tablename__ = "prospects"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Inquiry")  # Inquiry, Pending Admission, Lost, Admitted
    referral_source_id = db.Column(db.Integer, db.ForeignKey("referral_sources.id"), nullable=True)
    assigned_marketer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey("prospects.id"), nullable=True)
    author_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    author_name = db.Column(db.String(255), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    next_step = db.Column(db.String(255), nullable=False)
    note_date = db.Column(db.Date, nullable=False)
    note_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class FamilyCommunication(db.Model):
    __tablename__ = "family_communications"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey("prospects.id"), nullable=True)
    communicator_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    communicator_name = db.Column(db.String(255), nullable=False)
    communication_text = db.Column(db.Text, nullable=False)
    communication_date = db.Column(db.Date, nullable=False)
    communication_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class EVVLog(db.Model):
    __tablename__ = "evv_logs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    staff_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    patient_name = db.Column(db.String(255), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    verification_status = db.Column(db.String(100), nullable=False, default="Pending")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class MileageLog(db.Model):
    __tablename__ = "mileage_logs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    staff_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    trip_date = db.Column(db.Date, nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    miles = db.Column(db.Float, nullable=False, default=0.0)
    purpose = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class StaffTracking(db.Model):
    __tablename__ = "staff_tracking"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    staff_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    activity_type = db.Column(db.String(255), nullable=False)
    target_name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(100), nullable=False, default="Open")
    entry_date = db.Column(db.Date, nullable=False)
    entry_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.String(100), nullable=True)
    details_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
