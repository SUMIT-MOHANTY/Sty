from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import time

from app.api.dependencies import get_db, get_current_user
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import Token, TokenPayload, UserRegister
from app.services.auth_service import authenticate_user, register_new_user

router = APIRouter()

# Simple rate limiter implementation
IP_TO_REQUESTS = {}
REQUEST_WINDOW = 60  # 1 minute
REQUEST_LIMIT = 5  # 5 attempts per minute

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Rate limiting implementation
    client_ip = request.client.host
    current_time = time.time()

    # Clean up old entries
    IP_TO_REQUESTS = {ip: [t for t in timestamps if current_time - t < REQUEST_WINDOW]
                     for ip, timestamps in IP_TO_REQUESTS.items()}

    # Check current IP's request count
    if client_ip in IP_TO_REQUESTS:
        if len(IP_TO_REQUESTS[client_ip]) >= REQUEST_LIMIT:
            response.headers["Retry-After"] = str(REQUEST_WINDOW)
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later."
            )
        IP_TO_REQUESTS[client_ip].append(current_time)
    else:
        IP_TO_REQUESTS[client_ip] = [current_time]

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=Token)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister,
) -> Any:
    """
    Register a new user and return access token
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )

    user = register_new_user(db=db, user_data=user_in)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=Dict[str, Any])
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "firstName": current_user.first_name,
        "lastName": current_user.last_name,
        "role": "admin" if current_user.is_admin else "applicant"
    }
