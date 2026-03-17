from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.repositories.appointment_repository import AppointmentRepository
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut

class AppointmentService:
    def __init__(self, db: Session):
        self.repository = AppointmentRepository(db)
        self.db = db

    async def create_appointment(self, data: AppointmentCreate, user_id: int) -> AppointmentOut:
        """Create a new appointment with rate limiting check"""
        # Rate limiting: Check if user has created too many appointments recently
        recent_count = (
            self.db.query(Appointment)
            .filter(
                Appointment.user_id == user_id,
                Appointment.created_at >= datetime.utcnow() - timedelta(hours=1)
            )
            .count()
        )

        if recent_count >= 5:  # Max 5 appointment bookings per hour
            raise ValueError("Rate limit exceeded. Please try again later.")

        appointment = self.repository.create_appointment(data, user_id)
        return self._map_to_schema(appointment)

    async def get_appointment(self, appointment_id: int, user_id: int, is_admin: bool = False) -> Optional[AppointmentOut]:
        """Get appointment by ID with security checks"""
        appointment = self.repository.get_by_id(appointment_id)

        if not appointment:
            return None

        # Security: Only allow users to view their own appointments unless admin
        if not is_admin and appointment.user_id != user_id:
            return None

        return self._map_to_schema(appointment)

    async def get_user_appointments(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AppointmentOut]:
        """Get all appointments for a user"""
        appointments = self.repository.get_user_appointments(user_id, skip, limit)
        return [self._map_to_schema(appointment) for appointment in appointments]

    async def update_appointment(
        self,
        appointment_id: int,
        data: AppointmentUpdate,
        user_id: int,
        is_admin: bool = False
    ) -> Optional[AppointmentOut]:
        """Update an appointment with security checks"""
        try:
            appointment = self.repository.update_appointment(appointment_id, user_id, data, is_admin)
            if appointment:
                return self._map_to_schema(appointment)
            return None
        except ValueError as e:
            # Re-raise the exception to be handled by API layer
            raise

    async def cancel_appointment(
        self,
        appointment_id: int,
        user_id: int,
        cancellation_reason: str,
        is_admin: bool = False
    ) -> bool:
        """Cancel an appointment with audit trail"""
        # First update with cancellation reason
        update_data = AppointmentUpdate(
            status=AppointmentStatus.CANCELLED,
            cancellation_reason=cancellation_reason
        )

        try:
            result = self.repository.update_appointment(appointment_id, user_id, update_data, is_admin)
            return result is not None
        except ValueError as e:
            # Re-raise the exception to be handled by API layer
            raise

    def _map_to_schema(self, appointment: Appointment) -> AppointmentOut:
        """Map appointment model to schema with additional info"""
        appointment_dict = {
            "id": appointment.id,
            "user_id": appointment.user_id,
            "application_id": appointment.application_id,
            "location_id": appointment.location_id,
            "appointment_date": appointment.appointment_date,
            "status": appointment.status,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
            "is_modifiable": appointment.is_modifiable()
        }

        # Add location name if available through relationship
        if hasattr(appointment, "location") and appointment.location:
            appointment_dict["location_name"] = appointment.location.name

        return AppointmentOut(**appointment_dict)
