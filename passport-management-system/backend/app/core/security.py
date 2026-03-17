from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password

    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password to compare against

    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a password hash using bcrypt

    Args:
        password: The plaintext password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        subject: The subject of the token (usually user_id)
        role: The user's role (for RBAC)
        expires_delta: Optional custom expiration time

    Returns:
        str: The encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "type": "access_token",
        "iat": datetime.utcnow()  # issued at time for token rotation policies
    }

    # Create a signed JWT using the secret key
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

def create_email_verification_token(email: str) -> str:
    """
    Create a JWT token for email verification

    Args:
        email: The email to verify

    Returns:
        str: The encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

def create_password_reset_token(email: str) -> str:
    """
    Create a JWT token for password reset

    Args:
        email: The email for password reset

    Returns:
        str: The encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(hours=1)  # Shorter expiry for security
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt
