import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailVerificationService:
    """
    Service for handling email verification processes.

    This service generates verification tokens, stores them,
    and sends verification emails to users.
    """
    # In production, this would be stored in the database
    # For simplicity, using an in-memory dictionary for this example
    verification_tokens: Dict[str, Dict] = {}

    @classmethod
    def generate_token(cls, user_id: str, email: str) -> str:
        """
        Generate a unique verification token for a user.

        Args:
            user_id: The ID of the user
            email: The email address of the user

        Returns:
            str: The generated token
        """
        # Generate a secure random token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(64))

        # Store token with expiration time (24 hours)
        cls.verification_tokens[token] = {
            "user_id": user_id,
            "email": email,
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }

        return token

    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict]:
        """
        Verify if a token is valid and not expired.

        Args:
            token: The token to verify

        Returns:
            Optional[Dict]: User information if token is valid, None otherwise
        """
        if token not in cls.verification_tokens:
            return None

        token_data = cls.verification_tokens[token]

        # Check if token is expired
        if token_data["expires_at"] < datetime.utcnow():
            del cls.verification_tokens[token]
            return None

        # Token is valid - remove from storage to prevent reuse
        user_data = cls.verification_tokens[token]
        del cls.verification_tokens[token]

        return user_data

    @staticmethod
    def send_verification_email(email: str, token: str, base_url: str = "http://localhost:8000") -> bool:
        """
        Send verification email to the user.

        Args:
            email: The recipient email address
            token: The verification token
            base_url: The base URL of the application

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        verification_link = f"{base_url}/api/auth/verify-email?token={token}"

        # In a real implementation, this would use an SMTP server or email service
        # For now, just log the email that would be sent
        print(f"Sending verification email to: {email}")
        print(f"Verification link: {verification_link}")

        # Simulate successful sending
        return True
