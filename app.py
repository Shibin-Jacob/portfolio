from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    # Prepare record
    entry = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Save to messages.json (simple local storage)
    file_path = "messages.json"
    existing = []

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []

    existing.append(entry)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return jsonify({"success": True, "message": "Message received. I’ll get back to you soon."})


# if __name__ == "__main__":
#     # Debug=True for development, remove/change in production
#     app.run(debug=True)
# For Vercel Serverless compatibility
def handler(event, context):
    return app(event, context)
