from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from datetime import datetime

from app.core.config import settings
from app.core.database import get_db
from app.schemas.user import TokenData
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate the access token and get the current user

    Args:
        db: Database session
        token: JWT token

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Check token type
        token_type = payload.get("type")
        if token_type != "access_token":
            raise credentials_exception

        # Create token data object
        token_data = TokenData(user_id=user_id, role=payload.get("role"))
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Update last_login if needed
    # Uncomment to update on every authenticated request (can be resource intensive)
    # user.last_login = datetime.utcnow()
    # db.commit()

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User: The authenticated active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get the current verified user

    Args:
        current_user: Authenticated active user

    Returns:
        User: The authenticated verified user

    Raises:
        HTTPException: If user's email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get the current admin user

    Args:
        current_user: Authenticated active user

    Returns:
        User: The authenticated admin user

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Role-based access control (RBAC) middleware
def role_required(required_roles: List[str]):
    """
    Role-based access control dependency

    Args:
        required_roles: List of roles allowed to access the endpoint

    Returns:
        Callable: Dependency function for role checking
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not authorized"
            )
        return current_user
    return role_checker
