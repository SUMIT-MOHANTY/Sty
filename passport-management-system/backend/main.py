import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.api import auth
from app.core.config import settings
from app.middleware.auth import auth_middleware_factory

app = FastAPI(
    title="Passport Management System API",
    description="API for managing passport applications and appointments",
    version="1.0.0",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)

# Setup authentication middleware
exclude_paths = [
    f"{settings.API_V1_STR}/auth/login",
    f"{settings.API_V1_STR}/auth/register",
    f"{settings.API_V1_STR}/auth/reset-password",
    f"{settings.API_V1_STR}/auth/verify-email",
    "/docs",
    "/redoc",
    "/openapi.json",
]

# Commented out for development - uncomment in production
# app.add_middleware(auth_middleware_factory(exclude_paths))

@app.get("/")
async def root():
    return {"message": "Welcome to Passport Management System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )
