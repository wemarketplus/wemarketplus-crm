from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import Prospect, AuditLog

prospects_bp = Blueprint("prospects", __name__, url_prefix="/api/prospects")

VALID_STATUSES = ["Inquiry", "Pending Admission", "Lost", "Admitted"]


@prospects_bp.route("/", methods=["GET"])
@jwt_required()
def list_prospects():
    claims = get_jwt()
    company_id = claims.get("company_id")

    prospects = Prospect.query.filter_by(company_id=company_id).order_by(Prospect.id.desc()).all()

    return jsonify([
        {
            "id": p.id,
            "company_id": p.company_id,
            "name": p.name,
            "status": p.status,
            "referral_source_id": p.referral_source_id,
            "assigned_marketer": p.assigned_marketer,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in prospects
    ]), 200


@prospects_bp.route("/", methods=["POST"])
@jwt_required()
def add_prospect():
    claims = get_jwt()
    company_id = claims.get("company_id")
    user_name = claims.get("name")

    data = request.get_json() or {}
    name = data.get("name")
    status = data.get("status")
    referral_source_id = data.get("referral_source_id")
    assigned_marketer = data.get("assigned_marketer")

    if not name or not status:
        return jsonify({"error": "name and status are required"}), 400

    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400

    prospect = Prospect(
        company_id=company_id,
        name=name,
        status=status,
        referral_source_id=referral_source_id,
        assigned_marketer=assigned_marketer
    )
    db.session.add(prospect)
    db.session.flush()

    audit = AuditLog(
        user_id=None,
        action=f"{user_name} added prospect {name} with status {status}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "message": "Prospect added successfully",
        "prospect_id": prospect.id
    }), 201


@prospects_bp.route("/<int:prospect_id>", methods=["PUT"])
@jwt_required()
def update_prospect(prospect_id):
    claims = get_jwt()
    company_id = claims.get("company_id")
    user_name = claims.get("name")

    prospect = Prospect.query.filter_by(id=prospect_id, company_id=company_id).first()
    if not prospect:
        return jsonify({"error": "Prospect not found"}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"]:
        prospect.name = data["name"]

    if "status" in data and data["status"]:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400
        prospect.status = data["status"]

    if "referral_source_id" in data:
        prospect.referral_source_id = data["referral_source_id"]

    if "assigned_marketer" in data:
        prospect.assigned_marketer = data["assigned_marketer"]

    audit = AuditLog(
        user_id=None,
        action=f"{user_name} updated prospect {prospect.id}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Prospect updated successfully"}), 200


@prospects_bp.route("/<int:prospect_id>", methods=["DELETE"])
@jwt_required()
def delete_prospect(prospect_id):
    claims = get_jwt()
    company_id = claims.get("company_id")
    user_name = claims.get("name")

    prospect = Prospect.query.filter_by(id=prospect_id, company_id=company_id).first()
    if not prospect:
        return jsonify({"error": "Prospect not found"}), 404

    prospect_name = prospect.name
    db.session.delete(prospect)

    audit = AuditLog(
        user_id=None,
        action=f"{user_name} deleted prospect {prospect_name}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Prospect deleted successfully"}), 200
