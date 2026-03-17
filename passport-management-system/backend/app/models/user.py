from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import Optional, List
from datetime import datetime

from app.core.database import Base

class User(Base):
    """User model for storing user account information"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum("regular", "admin", name="user_roles"), nullable=False, default="regular")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    # Security best practices: Never store plaintext password, always store hashed version
    # No password attribute to prevent accidental storage/exposure

    def __repr__(self) -> str:
        return f"<User {self.email}>"
