from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, migrate, jwt
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.referrals import referrals_bp
from routes.prospects import prospects_bp
from routes.notes import notes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(referrals_bp)
    app.register_blueprint(prospects_bp)
    app.register_blueprint(notes_bp)

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
