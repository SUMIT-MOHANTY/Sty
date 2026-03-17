import os
from pydantic import BaseSettings, EmailStr
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Passport Management System"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str

    # JWT Authentication settings
    SECRET_KEY: str  # Secure random key for signing JWT tokens
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: EmailStr

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
