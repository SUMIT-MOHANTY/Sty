from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SystemSettings(BaseModel):
    """System settings schema"""
    application_fee: float = Field(..., description="Passport application fee")
    appointment_slots_per_day: int = Field(..., description="Number of appointment slots per day")
    maintenance_mode: bool = Field(False, description="System maintenance mode")
    notification_email: str = Field(..., description="Email address for system notifications")
    document_retention_days: int = Field(30, description="Number of days to retain documents")
    allowed_document_types: list = Field(default=["pdf", "jpg", "png"], description="Allowed document file types")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Custom system settings")

    class Config:
        orm_mode = True
