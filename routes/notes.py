from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import Note, AuditLog

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")

VALID_NEXT_STEPS = [
    "Immediate Family Outreach (Call/Text)",
    "Schedule On-Site Visit",
    "Conduct Bedside Presentation",
    "Request Clinical Records (H&P)",
    "RN Assessment Requested",
    "RN Assessment Scheduled",
    "Obtain Physician Order for Eval",
    "Insurance Verification in Progress",
    "CM Follow-Up (Status Update)",
    "Overcoming Family Hesitation",
    "Other",
]


@notes_bp.route("/", methods=["GET"])
@jwt_required()
def list_notes():
    claims = get_jwt()
    company_id = claims.get("company_id")

    prospect_id = request.args.get("prospect_id", type=int)

    query = Note.query

    if prospect_id:
        query = query.filter_by(prospect_id=prospect_id)

    notes = query.order_by(Note.id.desc()).all()

    return jsonify([
        {
            "id": n.id,
            "prospect_id": n.prospect_id,
            "user_name": n.user_name,
            "note": n.note,
            "next_step": n.next_step,
            "note_date": n.note_date.isoformat() if n.note_date else None,
            "note_time": n.note_time.isoformat() if n.note_time else None,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }
        for n in notes
    ]), 200


@notes_bp.route("/", methods=["POST"])
@jwt_required()
def add_note():
    claims = get_jwt()
    user_name_from_token = claims.get("name")

    data = request.get_json() or {}

    prospect_id = data.get("prospect_id")
    user_name = data.get("user_name") or user_name_from_token
    note = data.get("note")
    next_step = data.get("next_step")
    note_date = data.get("note_date")
    note_time = data.get("note_time")

    if not user_name or not note or not next_step or not note_date or not note_time:
        return jsonify({"error": "user_name, note, next_step, note_date, and note_time are required"}), 400

    if next_step not in VALID_NEXT_STEPS:
        return jsonify({"error": "Invalid next_step value"}), 400

    try:
        parsed_date = datetime.strptime(note_date, "%Y-%m-%d").date()
        parsed_time = datetime.strptime(note_time, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    new_note = Note(
        prospect_id=prospect_id,
        user_name=user_name,
        note=note,
        next_step=next_step,
        note_date=parsed_date,
        note_time=parsed_time
    )
    db.session.add(new_note)
    db.session.flush()

    audit = AuditLog(
        user_id=None,
        action=f"{user_name_from_token} added note for prospect {prospect_id}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "message": "Note added successfully",
        "note_id": new_note.id
    }), 201
