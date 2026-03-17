from pydantic import BaseModel, Field
from typing import Optional

class ApplicationStatusUpdate(BaseModel):
    """Application status update schema"""
    status: str = Field(..., description="Application status")
    admin_notes: Optional[str] = Field(None, description="Admin notes on application")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if applicable")
