# Intentionally insecure demo backend for analyzer testing only

import os
import sqlite3
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# ISSUE: hardcoded secrets / credentials
app.config["SECRET_KEY"] = "super-secret-fullstack-dev-key"
DB_PATH = "users.db"
DB_USER = "admin"
DB_PASSWORD = "password123"

# ISSUE: overly permissive CORS
CORS(app, resources={r"/*": {"origins": "*"}})

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            role TEXT,
            bio TEXT
        )
    """)

    # ISSUE: plaintext passwords
    cur.execute("DELETE FROM users")
    cur.execute("INSERT INTO users (email, password, role, bio) VALUES ('admin@example.com', 'admin123', 'admin', 'admin bio')")
    cur.execute("INSERT INTO users (email, password, role, bio) VALUES ('user@example.com', 'user123', 'user', 'normal user')")
    conn.commit()
    conn.close()

init_db()

@app.route("/login", methods=["GET"])
def login():
    email = request.args.get("email")
    password = request.args.get("password")
    token = request.args.get("token")
    api_key = request.args.get("apiKey")

    # ISSUE: sensitive data in logs
    app.logger.warning(f"Login request email={email} password={password} token={token} api_key={api_key}")

    # ISSUE: no real authentication or validation
    return jsonify({
        "status": "ok",
        "email": email,
        "token": token,
        "role": "admin"
    })

@app.route("/admin/users", methods=["GET"])
def admin_users():
    token = request.args.get("token")

    # ISSUE: no real authz/authn
    app.logger.info(f"Admin users accessed with token={token}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, email, password, role, bio FROM users")
    rows = cur.fetchall()
    conn.close()

    # ISSUE: returns sensitive data including plaintext passwords
    return jsonify([
        {"id": r[0], "email": r[1], "password": r[2], "role": r[3], "bio": r[4]}
        for r in rows
    ])

@app.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ISSUE: IDOR + SQL injection risk through interpolation
    sql = f"SELECT id, email, role, bio FROM users WHERE id = {user_id}"
    app.logger.info(f"Executing SQL: {sql}")
    cur.execute(sql)
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Not found"}), 404

    return jsonify({"id": row[0], "email": row[1], "role": row[2], "bio": row[3]})

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ISSUE: SQL injection via string interpolation
    sql = f"SELECT id, email, role FROM users WHERE email LIKE '%{q}%'"
    app.logger.info(f"Executing SQL: {sql}")
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "email": r[1], "role": r[2]}
        for r in rows
    ])

@app.route("/upload", methods=["POST"])
def upload():
    uploaded = request.files["file"]

    # ISSUE: unsafe file path handling / path traversal risk
    save_path = os.path.join("uploads", uploaded.filename)
    uploaded.save(save_path)

    return jsonify({"saved_to": save_path})

@app.route("/process", methods=["POST"])
def process():
    try:
        payload = request.get_json()

        # ISSUE: no input validation
        user_id = payload["user_id"]
        action = payload["action"]

        # ISSUE: logs potentially sensitive payload
        app.logger.error(f"Processing payload: {payload}")

        if action == "delete_all":
            return jsonify({"status": "dangerous action accepted", "user_id": user_id})

        return jsonify({"status": "processed", "user_id": user_id, "action": action})

    except Exception as exc:
        # ISSUE: returns internal errors and stack traces
        return jsonify({
            "error": str(exc),
            "trace": traceback.format_exc()
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "up"})

if __name__ == "__main__":
    # ISSUE: debug enabled in server startup
    app.run(host="0.0.0.0", port=5000, debug=True)
