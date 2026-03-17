import os
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, BaseModel
from jose import jwt
from datetime import datetime, timedelta

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Define email connection config
email_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Create FastMail instance
try:
    fm = FastMail(email_config)
except Exception as e:
    logger.error(f"Failed to initialize FastMail: {e}")
    fm = None

class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]

def generate_verification_token(user_id: int) -> str:
    """Generate email verification token"""
    expire = datetime.utcnow() + timedelta(hours=24)
    token_data = {
        "exp": expire.timestamp(),
        "user_id": user_id,
        "purpose": "email_verification"
    }
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return token

async def send_email_async(
    subject: str,
    email_to: List[EmailStr],
    body: Dict[str, Any],
    template_name: str = "email_template.html"
) -> None:
    if not fm:
        logger.error("FastMail not initialized. Cannot send email.")
        return

    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        template_body=body,
        subtype=MessageType.html
    )

    try:
        await fm.send_message(message, template_name=template_name)
        logger.info(f"Email sent to {', '.join(email_to)}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def send_verification_email(email: str, user_id: int) -> None:
    """Send verification email to user"""
    token = generate_verification_token(user_id)
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email/{token}"

    # In a real app, this would be async
    # For this example, we'll just log it
    logger.info(f"Verification URL for {email}: {verification_url}")

    # In production, you would use:
    # asyncio.create_task(send_email_async(
    #     subject="Verify your email",
    #     email_to=[email],
    #     body={
    #         "title": "Email Verification",
    #         "name": email.split('@')[0],
    #         "verification_url": verification_url
    #     }
    # ))
