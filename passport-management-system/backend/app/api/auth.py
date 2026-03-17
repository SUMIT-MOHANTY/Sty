from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
    TokenData
)
from app.core.database import get_db
from app.models.user import User
from app.core.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

@router.post("/register", response_model=Token)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check if user exists
    db_user_by_email = db.query(User).filter(User.email == user_data.email).first()
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user_by_username = db.query(User).filter(User.username == user_data.username).first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role="user",  # Default role is "user"
        is_active=True,
        is_verified=False  # Email verification required
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    send_verification_email(new_user.email, new_user.id)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": new_user.username,
            "id": new_user.id,
            "role": new_user.role,
            "permissions": ["read:profile", "write:applications", "read:applications"]
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "username": new_user.username,
        "role": new_user.role
    }

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    permissions = ["read:profile", "write:applications", "read:applications"]

    if user.role == "admin":
        permissions.extend([
            "read:all_applications",
            "write:all_applications",
            "read:all_appointments",
            "write:all_appointments",
            "read:all_users",
            "write:all_users"
        ])

    access_token = create_access_token(
        data={
            "sub": user.username,
            "id": user.id,
            "role": user.role,
            "permissions": permissions
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.post("/reset-password")
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist",
        )

    # In a real application, generate a reset token and send email
    # For this example, we'll just return a success message
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.get("/verify-email/{verification_token}")
def verify_email(verification_token: str, db: Session = Depends(get_db)) -> Any:
    # In a real application, verify the token and update user's verification status
    return {"message": "Email verified successfully"}

@router.get("/me", response_model=dict)
def get_current_user_info(current_user: TokenData = Depends(get_current_user)) -> Any:
    return {
        "id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role
    }
