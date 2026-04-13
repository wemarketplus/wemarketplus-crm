from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db
from models import User, Company
from utils.security import hash_password, verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register-admin", methods=["POST"])
def register_admin():
    data = request.get_json() or {}

    company_name = data.get("company_name")
    admin_name = data.get("admin_name")
    email = data.get("email")
    password = data.get("password")
    subscription_plan = data.get("subscription_plan", "pro")
    user_limit = data.get("user_limit", 5)

    if not company_name or not admin_name or not email or not password:
        return jsonify({"error": "company_name, admin_name, email, and password are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with that email already exists"}), 400

    company = Company(
        name=company_name,
        subscription_plan=subscription_plan,
        user_limit=user_limit
    )
    db.session.add(company)
    db.session.flush()

    admin_user = User(
        company_id=company.id,
        name=admin_name,
        email=email,
        password=hash_password(password),
        role="admin"
    )
    db.session.add(admin_user)
    db.session.commit()

    return jsonify({
        "message": "Admin registered successfully",
        "company_id": company.id,
        "user_id": admin_user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password, user.password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={
        "role": user.role,
        "company_id": user.company_id,
        "name": user.name
    })

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id
        }
    }), 200
