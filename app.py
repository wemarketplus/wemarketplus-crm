from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, migrate, jwt
from models import (
    Tenant,
    User,
    Subscription,
    ReferralSource,
    Prospect,
    Note,
    FamilyCommunication,
    EVVLog,
    MileageLog,
    StaffTracking,
    AuditLog,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @app.route("/")
    def home():
        return jsonify({
            "message": "We Market Plus CRM backend is running",
            "status": "ok"
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    @app.route("/api/test")
    def api_test():
        return jsonify({
            "message": "CRM API test route working"
        })

    return app


app = create_app()
