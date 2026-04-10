from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- MOCK DATABASE ---
agencies = {
    "demoagency": {
        "plan": "pro",
        "status": "active",
        "user_limit": 10,
        "users": [
            {"email": "admin@demo.com", "password": "demo123", "role": "admin"},
            {"email": "nurse@demo.com", "password": "demo123", "role": "nurse"}
        ]
    }
}

# --- LOGIN ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    for agency_name, agency in agencies.items():
        if agency["status"] != "active":
            return jsonify({"error": "Subscription inactive"}), 403

        for user in agency["users"]:
            if user["email"] == data["email"] and user["password"] == data["password"]:
                return jsonify({
                    "success": True,
                    "user": user,
                    "agency": agency_name
                })

    return jsonify({"success": False}), 401


# --- DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    return jsonify({
        "patients": 32,
        "visits_today": 14,
        "mileage": 128,
        "alerts": ["Missing signatures", "Late notes"]
    })


# --- ADD USER (ADMIN CONTROL) ---
@app.route("/add-user", methods=["POST"])
def add_user():
    data = request.json
    agency = agencies["demoagency"]

    if len(agency["users"]) >= agency["user_limit"]:
        return jsonify({"error": "User limit reached"}), 403

    agency["users"].append(data)
    return jsonify({"success": True})


# --- KILL SWITCH ---
@app.route("/set-status", methods=["POST"])
def set_status():
    data = request.json
    agencies["demoagency"]["status"] = data["status"]
    return jsonify({"success": True})


@app.route("/")
def home():
    return "HospiceLink Max CRM LIVE"


if __name__ == "__main__":
    app.run()
