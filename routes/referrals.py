from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import ReferralSource, AuditLog

referrals_bp = Blueprint("referrals", __name__, url_prefix="/api/referrals")


@referrals_bp.route("/", methods=["GET"])
@jwt_required()
def list_referrals():
    claims = get_jwt()
    company_id = claims.get("company_id")

    referrals = ReferralSource.query.filter_by(company_id=company_id).order_by(ReferralSource.id.desc()).all()

    return jsonify([
        {
            "id": r.id,
            "company_id": r.company_id,
            "name": r.name,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in referrals
    ]), 200


@referrals_bp.route("/", methods=["POST"])
@jwt_required()
def add_referral():
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    company_id = claims.get("company_id")
    user_name = claims.get("name")

    data = request.get_json() or {}
    name = data.get("name")
    status = data.get("status")

    if not name or not status:
        return jsonify({"error": "name and status are required"}), 400

    if status not in ["Green", "Red"]:
        return jsonify({"error": "status must be Green or Red"}), 400

    referral = ReferralSource(
        company_id=company_id,
        name=name,
        status=status
    )
    db.session.add(referral)
    db.session.flush()

    audit = AuditLog(
        user_id=None,
        action=f"{user_name} added referral source {name}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "message": "Referral source added successfully",
        "referral_id": referral.id
    }), 201


@referrals_bp.route("/<int:referral_id>", methods=["DELETE"])
@jwt_required()
def delete_referral(referral_id):
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    company_id = claims.get("company_id")
    user_name = claims.get("name")

    referral = ReferralSource.query.filter_by(id=referral_id, company_id=company_id).first()
    if not referral:
        return jsonify({"error": "Referral source not found"}), 404

    referral_name = referral.name
    db.session.delete(referral)

    audit = AuditLog(
        user_id=None,
        action=f"{user_name} deleted referral source {referral_name}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Referral source deleted successfully"}), 200
