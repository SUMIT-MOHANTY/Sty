from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import bcrypt
import uuid

from ...models.auth import (
    UserRegistration,
    UserResponse,
    EmailVerificationRequest,
    EmailVerificationResponse
)
from ...services.email_service import EmailVerificationService
from ...core.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    """
    Register a new user with the system.

    This endpoint:
    1. Validates user input
    2. Checks for existing users with the same email
    3. Creates a new user with hashed password
    4. Generates and stores a verification token
    5. Sends a verification email

    Args:
        user_data: The user registration data
        db: Database session

    Returns:
        UserResponse: The created user's ID, email, and a message

    Raises:
        HTTPException: If a user with the email already exists
    """
    # Check if email already exists
    # In a real implementation, this would use SQLAlchemy models
    # For now, simulating this check
    existing_user = db.execute("SELECT * FROM users WHERE email = :email",
                               {"email": user_data.email}).fetchone()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    password_bytes = user_data.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # Create user ID
    user_id = str(uuid.uuid4())

    # In a real implementation, this would use SQLAlchemy models to insert into database
    # Simulating user creation
    db.execute(
        """
        INSERT INTO users (id, email, password_hash, first_name, last_name, is_verified, role)
        VALUES (:id, :email, :password_hash, :first_name, :last_name, :is_verified, :role)
        """,
        {
            "id": user_id,
            "email": user_data.email,
            "password_hash": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "is_verified": False,
            "role": "regular"
        }
    )
    db.commit()

    # Generate verification token
    token = EmailVerificationService.generate_token(user_id, user_data.email)

    # Send verification email
    EmailVerificationService.send_verification_email(
        email=user_data.email,
        token=token
    )

    return UserResponse(
        user_id=user_id,
        email=user_data.email,
        message="Verification email sent"
    )

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(verification_data: EmailVerificationRequest, db: Session = Depends(get_db)):
    """
    Verify a user's email address using the verification token.

    Args:
        verification_data: Contains the verification token
        db: Database session

    Returns:
        EmailVerificationResponse: Success message

    Raises:
        HTTPException: If the token is invalid or expired
    """
    token_data = EmailVerificationService.verify_token(verification_data.token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Update user verification status
    # In a real implementation, this would use SQLAlchemy models
    db.execute(
        "UPDATE users SET is_verified = TRUE WHERE id = :user_id",
        {"user_id": token_data["user_id"]}
    )
    db.commit()

    return EmailVerificationResponse(message="Email verified successfully")
