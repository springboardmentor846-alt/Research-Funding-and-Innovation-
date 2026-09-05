"""
Email sending service.

If SMTP credentials are not configured in the environment, emails are not
sent over the network — instead the content is logged to the console.
This keeps the app fully functional (no crashes, no blocked requests)
in local/dev environments where SMTP has not been set up yet.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("email_service")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL") or SMTP_USERNAME

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def _smtp_configured() -> bool:
    return all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL])


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an email if SMTP is configured. Otherwise logs it to the console
    so the flow (e.g. password reset) can still be tested/used locally.
    Never raises — a failed/missing email configuration should never crash
    the request that triggered it.
    """
    if not _smtp_configured():
        logger.info(
            "SMTP not configured — logging email instead of sending.\n"
            "To: %s\nSubject: %s\nBody:\n%s",
            to_email, subject, body,
        )
        print(f"[email_service] SMTP not configured. Would send to {to_email}:\n{subject}\n{body}")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT), timeout=15) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, [to_email], msg.as_string())
        return True
    except Exception as exc:  # noqa: BLE001 - never let email failure break the request
        logger.warning("Failed to send email to %s: %s", to_email, exc)
        return False


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    subject = "Reset your password"
    body = (
        "We received a request to reset your password.\n\n"
        f"Click the link below to set a new password (valid for a limited time):\n{reset_link}\n\n"
        "If you did not request this, you can safely ignore this email."
    )
    return send_email(to_email, subject, body)