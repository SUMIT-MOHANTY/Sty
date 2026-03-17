import smtplib
from email.message import EmailMessage
from app.utils.config import settings

def send_email(recipient_email: str, subject: str, content: str):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.MAIL_FROM
    message["To"] = recipient_email
    message.set_content(content)

    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_TLS:
                server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_verification_email(recipient_email: str, token: str):
    subject = "Verify your email for the Passport Portal"
    verification_link = f"http://localhost:3000/verify-email?token={token}"

    content = f"""
    Hello,

    Thank you for registering with the Passport Portal!

    Please click the link below to verify your email address:
    {verification_link}

    This link is valid for 24 hours.

    If you did not register for an account, please ignore this email.

    Best regards,
    Passport Portal Team
    """

    return send_email(recipient_email, subject, content)
