from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..core.security import SECRET_KEY, ALGORITHM, oauth2_scheme
from ..models.user import User
from ..core.database import get_db

logger = logging.getLogger("middleware.auth")

async def authenticate_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """
    Authenticate a user based on JWT token.

    Args:
        token: JWT token from request
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            logger.warning("Token missing user_id")
            raise credentials_exception

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.warning(f"User {user_id} not found in database")
            raise credentials_exception

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user {user_id} attempted authentication")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        return user
    except ExpiredSignatureError:
        logger.warning("Expired token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise credentials_exception
