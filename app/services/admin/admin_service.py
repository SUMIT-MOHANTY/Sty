from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ...db.repositories.application_repository import ApplicationRepository
from ...db.repositories.user_repository import UserRepository
from ...schemas.application import ApplicationStatusUpdate
from ...schemas.user import UserPermissionUpdate
from ...schemas.admin import SystemSettings
from ...models.application import Application
from ...models.user import User

class AdminService:
    """Service for admin operations"""

    def __init__(self, db: Session):
        self.db = db
        self.application_repo = ApplicationRepository(db)
        self.user_repo = UserRepository(db)
        self._system_settings = SystemSettings(
            application_fee=100.0,
            appointment_slots_per_day=20,
            maintenance_mode=False,
            notification_email="system@passport.gov",
            document_retention_days=30,
            allowed_document_types=["pdf", "jpg", "png"],
            custom_settings={}
        )

    async def get_applications(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Application]:
        """Get all passport applications with optional filtering"""
        return await self.application_repo.get_all(skip=skip, limit=limit, status=status)

    async def update_application_status(self, application_id: str, status_update: ApplicationStatusUpdate) -> Optional[Application]:
        """Update application status"""
        application = await self.application_repo.get_by_id(application_id)
        if not application:
            return None

        # Update application status
        application.status = status_update.status
        if status_update.admin_notes:
            application.admin_notes = status_update.admin_notes
        if status_update.rejection_reason:
            application.rejection_reason = status_update.rejection_reason

        return await self.application_repo.update(application)

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all system users"""
        return await self.user_repo.get_all(skip=skip, limit=limit)

    async def update_user_permissions(self, user_id: str, permission_update: UserPermissionUpdate) -> Optional[User]:
        """Update user permissions"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        # Update user permissions
        user.role = permission_update.role
        if permission_update.is_active is not None:
            user.is_active = permission_update.is_active
        if permission_update.permissions:
            user.permissions = permission_update.permissions

        return await self.user_repo.update(user)

    async def get_settings(self) -> SystemSettings:
        """Get system settings"""
        # In a real implementation, these would be fetched from a database
        return self._system_settings

    async def update_settings(self, settings: SystemSettings) -> SystemSettings:
        """Update system settings"""
        # In a real implementation, these would be persisted to a database
        self._system_settings = settings
        return self._system_settings
