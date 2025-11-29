from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import smtplib
import ssl
from email.message import EmailMessage

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


def send_contact_email(name: str, email: str, message: str):
    """
    Send contact form data to your email using SMTP.
    Configuration is taken from environment variables:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, TO_EMAIL (optional)
    """

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    to_email = os.environ.get("TO_EMAIL") or smtp_user

    # If SMTP is not configured, just log and skip
    if not (smtp_host and smtp_user and smtp_pass and to_email):
        print("[WARN] SMTP not fully configured, email not sent.")
        print("Expected env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, TO_EMAIL")
        return False, "SMTP not configured"

    msg = EmailMessage()
    msg["Subject"] = f"New portfolio contact from {name}"
    msg["From"] = smtp_user
    msg["To"] = to_email

    body = (
        f"New message from your portfolio site:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Time (UTC): {datetime.utcnow().isoformat()}Z\n\n"
        f"Message:\n{message}\n"
    )
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            # If you're using port 587 (TLS)
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print("[INFO] Contact email sent successfully.")
        return True, "Email sent"
    except Exception as e:
        print("[ERROR] Failed to send email:", repr(e))
        return False, str(e)


@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    entry = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Log to Vercel logs
    print("New contact message:", entry, flush=True)

    # Try to send email
    ok, info = send_contact_email(name, email, message)

    # For the user, we don't expose internal SMTP errors in detail
    if ok:
        return jsonify(
            {
                "success": True,
                "message": "Message received. I’ll get back to you soon.",
            }
        )
    else:
        # You can choose: still return success (so user isn't scared) or show error.
        return jsonify(
            {
                "success": True,
                "message": "Message received. (Email notification is temporarily unavailable.)",
            }
        )

# Local dev only
if __name__ == "__main__":
    app.run(debug=True)
