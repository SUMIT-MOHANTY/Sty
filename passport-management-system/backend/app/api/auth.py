from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    create_email_verification_token,
    create_password_reset_token
)
from app.core.email import (
    send_verification_email,
    send_password_reset_email
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    UserPasswordUpdate
)
from app.middleware.auth import get_current_user, get_current_active_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    user_in: UserCreate
) -> Any:
    """
    Register a new user.
    """
    # Check if user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user with hashed password
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role="regular",  # Default role
        is_active=True,
        is_verified=False  # Requires email verification
    )

    # Save user to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate verification token
    verification_token = create_email_verification_token(email=user_in.email)

    # Send verification email asynchronously
    background_tasks.add_task(
        send_verification_email,
        email_to=user_in.email,
        token=verification_token,
        username=f"{user_in.first_name} {user_in.last_name}"
    )

    return db_user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Update last login time
    user.last_login = db.func.now()
    db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    db: Session = Depends(get_db),
    token: str = Body(..., embed=True)
) -> Any:
    """
    Verify user email with token received by email.
    """
    # Decode token
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check token type
        token_type = payload.get("type")
        if token_type != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Find user with email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Mark as verified
    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}

@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
def request_password_reset(
    email: EmailStr = Body(..., embed=True),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request a password reset token sent to user's email.
    """
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Return 200 even if user doesn't exist to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}

    # Generate password reset token
    reset_token = create_password_reset_token(email=email)

    # Send password reset email asynchronously
    background_tasks.add_task(
        send_password_reset_email,
        email_to=email,
        token=reset_token,
        username=f"{user.first_name} {user.last_name}"
    )

    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset user password with token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check token type
        token_type = payload.get("type")
        if token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Find user with email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    *,
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password.
    """
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_update.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
