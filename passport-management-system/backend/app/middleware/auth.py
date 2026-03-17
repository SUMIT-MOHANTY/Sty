from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
import time
from typing import Optional, Callable

from app.core.config import settings

class AuthMiddleware:
    def __init__(self, app, exclude_paths=None):
        self.app = app
        self.exclude_paths = exclude_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/reset-password",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def __call__(self, request: Request, call_next):
        # Skip auth for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Check for token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.replace("Bearer ", "")
        try:
            # Validate token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            # Check if token is expired
            exp = payload.get("exp")
            if not exp or time.time() > exp:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token expired"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Add user info to request state for handlers
            request.state.user = {
                "id": payload.get("id"),
                "username": payload.get("sub"),
                "role": payload.get("role", "user"),
                "permissions": payload.get("permissions", []),
            }

        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)

def auth_middleware_factory(exclude_paths=None):
    def create_middleware(app):
        return AuthMiddleware(app, exclude_paths)
    return create_middleware
