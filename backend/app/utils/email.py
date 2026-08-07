"""
Email sending utility — wraps SMTP or logs when disabled.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _send_email(
    to_email: str,
    subject: str,
    html_body: str,
) -> None:
    """Send an HTML email via SMTP. Only fires when EMAILS_ENABLED=true."""
    if not settings.EMAILS_ENABLED:
        logger.debug(
            f"[Email disabled] Would send '{subject}' to {to_email}:\n{html_body}"
        )
        return

    import aiosmtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
    logger.info(f"Email '{subject}' sent to {to_email}")


async def send_verification_email(email: str, token: str) -> None:
    """Send account email verification link."""
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#6366f1;">Verify Your Email</h2>
      <p>Welcome to the <strong>Research Funding & Innovation Intelligence Platform</strong>!</p>
      <p>Click the button below to verify your email address:</p>
      <a href="{verify_url}"
         style="display:inline-block;padding:12px 24px;background:#6366f1;
                color:#fff;border-radius:8px;text-decoration:none;font-weight:bold;">
        Verify Email
      </a>
      <p style="color:#888;font-size:0.85em;margin-top:24px;">
        This link expires in 24 hours. If you did not sign up, ignore this email.
      </p>
    </body></html>
    """
    await _send_email(email, "Verify your RFIP account", html)


async def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset link."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#6366f1;">Reset Your Password</h2>
      <p>We received a request to reset your <strong>RFIP Platform</strong> password.</p>
      <a href="{reset_url}"
         style="display:inline-block;padding:12px 24px;background:#6366f1;
                color:#fff;border-radius:8px;text-decoration:none;font-weight:bold;">
        Reset Password
      </a>
      <p style="color:#888;font-size:0.85em;margin-top:24px;">
        This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hour(s).
        If you did not request a reset, ignore this email.
      </p>
    </body></html>
    """
    await _send_email(email, "Reset your RFIP password", html)
