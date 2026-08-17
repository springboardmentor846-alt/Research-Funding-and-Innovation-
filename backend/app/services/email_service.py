import smtplib
from email.message import EmailMessage
from app.config import settings

def send_password_reset_email(email: str, reset_link: str) -> None:
    message = EmailMessage()
    message["Subject"] = "Reset your InnovFund password"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = email
    message.set_content(f"""Hello,

We received a request to reset your InnovFund password.

Use the link below to create a new password:

{reset_link}

This link expires in {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
InnovFund
Research Funding & Innovation Platform
""")
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)
