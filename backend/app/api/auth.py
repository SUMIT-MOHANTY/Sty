from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict, Any

from app.models.user import User
from app.utils.database import get_db
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    verify_user
)
from app.utils.schemas import UserCreate, Token, UserResponse
from app.utils.config import settings

router = APIRouter()

@router.post("/register", response_model=Dict[str, str])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = create_user(db, user_data)
    return {"message": "Registration successful! Please check your email to verify your account."}

@router.get("/verify/{token}", response_model=Dict[str, str])
def verify_email(token: str, db: Session = Depends(get_db)):
    verify_user(db, token)
    return {"message": "Email verified successfully! You can now log in."}

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
