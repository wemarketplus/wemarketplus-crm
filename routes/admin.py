from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import User, Company, AuditLog
from utils.security import hash_password

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    company_id = claims.get("company_id")
    users = User.query.filter_by(company_id=company_id).all()

    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]), 200


@admin_bp.route("/users", methods=["POST"])
@jwt_required()
def add_user():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    company_id = claims.get("company_id")
    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with that email already exists"}), 400

    company = Company.query.get(company_id)
    current_count = User.query.filter_by(company_id=company_id).count()

    if current_count >= company.user_limit:
        return jsonify({"error": "User limit reached for this subscription"}), 400

    user = User(
        company_id=company_id,
        name=name,
        email=email,
        password=hash_password(password),
        role=role
    )
    db.session.add(user)

    audit = AuditLog(
        user_id=None,
        action=f"Admin added user {email}"
    )
    db.session.add(audit)

    db.session.commit()

    return jsonify({
        "message": "User added successfully",
        "user_id": user.id
    }), 201


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    company_id = claims.get("company_id")
    user = User.query.filter_by(id=user_id, company_id=company_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)

    audit = AuditLog(
        user_id=None,
        action=f"Admin deleted user {user.email}"
    )
    db.session.add(audit)

    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200
