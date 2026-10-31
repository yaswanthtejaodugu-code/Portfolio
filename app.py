import os
import re
import smtplib
import ssl
from email.message import EmailMessage

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Create Flask application
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("portfolio.html")


@app.route("/send-message", methods=["POST"])
def send_message():
    # Reload .env on request to pick up any changes without restarting the server
    load_dotenv(override=True)

    # Get form data sent by JavaScript
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    sender_email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    # Validate required fields
    if not name or not sender_email or not message:
        return jsonify({
            "error": "Please fill in all fields."
        }), 400

    # Limit input lengths to prevent abuse
    if len(name) > 100 or len(sender_email) > 254 or len(message) > 5000:
        return jsonify({
            "error": "Your message exceeds the allowed length."
        }), 400

    # Validate sender email address format
    email_pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"
    if not re.fullmatch(email_pattern, sender_email):
        return jsonify({
            "error": "Please enter a valid email address."
        }), 400

    # Read email configuration from environment variables (.env)
    # Supports MAIL_USERNAME/MAIL_APP_PASSWORD/MAIL_RECIPIENT and SENDER_EMAIL/EMAIL_PASSWORD/RECEIVER_EMAIL
    mail_username = (os.environ.get("MAIL_USERNAME") or "").strip()
    mail_password = (os.environ.get("MAIL_APP_PASSWORD") or "").strip()
    recipient_email = (os.environ.get("MAIL_RECIPIENT") or mail_username).strip()

    # Clean Google App Password (remove spaces if copied from Google display)
    mail_password_clean = mail_password.replace(" ", "")

    smtp_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    try:
        smtp_port = int(os.environ.get("MAIL_PORT", 587))
    except ValueError:
        smtp_port = 587

    # Check configuration
    if not mail_username or not mail_password_clean or not recipient_email:
        app.logger.error("Email environment variables are missing.")
        return jsonify({
            "error": "Email service is not configured. Please check your .env settings."
        }), 500

    # Detect unconfigured placeholder credentials in .env
    placeholder_indicators = [
        "your_gmail_account",
        "your_gmail_app_password",
        "your_16_character_app_password",
    ]
    if any(p in mail_username.lower() for p in placeholder_indicators) or any(p in mail_password_clean.lower() for p in placeholder_indicators):
        app.logger.error("Email credentials in .env are still set to default placeholders.")
        return jsonify({
            "error": "Email settings contain placeholder values. Please update your .env file with your actual Gmail account and App Password."
        }), 500

    # Create email
    email_message = EmailMessage()
    email_message["Subject"] = f"New Portfolio Message from {name}"
    # email_message["From"] = mail_username
    email_message["To"] = recipient_email
    email_message["Reply-To"] = sender_email

    email_body = f"""You received a message from your portfolio contact form.

From: {name}
Email: {sender_email}

Message:
----------------------------------------
{message}
----------------------------------------
"""
    email_message.set_content(email_body)

    # Send email using SMTP (default Gmail with STARTTLS)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(mail_username, mail_password_clean)
            server.send_message(email_message)

        app.logger.info("Portfolio contact email sent successfully.")
        return jsonify({
            "message": "Message sent successfully! Thank you for contacting me."
        }), 200

    except smtplib.SMTPAuthenticationError:
        app.logger.exception("SMTP Authentication failed.")
        return jsonify({
            "error": "Email authentication failed. Please verify your Gmail address and 16-character Google App Password in .env."
        }), 500

    except (smtplib.SMTPException, OSError):
        app.logger.exception("Failed to send portfolio contact email.")
        return jsonify({
            "error": "Failed to send email due to a network or server issue. Please try again later."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
