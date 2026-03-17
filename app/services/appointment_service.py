from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.repositories.appointment_repository import AppointmentRepository
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentOut,
    AppointmentSlotCreate,
    AppointmentSlot,
    AppointmentAdminResponse
)

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

    async def create_appointment_slot(self, slot_data: AppointmentSlotCreate) -> AppointmentSlot:
        """Create available appointment slots as admin"""
        # Check if slots already exist for this time
        existing_slots = await self.repository.get_slots_by_time_range(
            location_id=slot_data.location_id,
            start_time=slot_data.start_time,
            end_time=slot_data.end_time
        )

        if existing_slots:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment slots already exist for this time range"
            )

        return await self.repository.create_appointment_slot(slot_data)

    async def get_all_slots(
        self,
        location_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        available_only: bool = False
    ) -> List[AppointmentSlot]:
        """Get all appointment slots with optional filtering"""
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=30)

        return await self.repository.get_appointment_slots(
            location_id=location_id,
            start_date=start_date,
            end_date=end_date,
            available_only=available_only
        )

    async def update_appointment_slot(self, slot_id: UUID, slot_data: AppointmentSlotCreate) -> AppointmentSlot:
        """Update an appointment slot as admin"""
        slot = await self.repository.get_slot_by_id(slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment slot not found"
            )

        # Check if the slot has booked appointments
        appointments = await self.repository.get_appointments_by_slot_id(slot_id)
        if any(appointment.status != AppointmentStatus.CANCELLED for appointment in appointments):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify slot with active appointments"
            )

        return await self.repository.update_appointment_slot(slot_id, slot_data)

    async def delete_appointment_slot(self, slot_id: UUID) -> bool:
        """Delete an appointment slot if no active appointments"""
        slot = await self.repository.get_slot_by_id(slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment slot not found"
            )

        # Check if the slot has booked appointments
        appointments = await self.repository.get_appointments_by_slot_id(slot_id)
        if any(appointment.status != AppointmentStatus.CANCELLED for appointment in appointments):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete slot with active appointments"
            )

        return await self.repository.delete_appointment_slot(slot_id)

    async def get_all_appointments(
        self,
        location_id: Optional[UUID] = None,
        status: Optional[AppointmentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[UUID] = None
    ) -> List[AppointmentAdminResponse]:
        """Get all appointments with optional filtering for admin view"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)  # Include recent past appointments
        if not end_date:
            end_date = datetime.now() + timedelta(days=30)

        appointments = await self.repository.get_appointments(
            location_id=location_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )

        # Convert to admin response format with user and application details
        return [
            await self._enrich_appointment_with_details(appointment)
            for appointment in appointments
        ]

    async def _enrich_appointment_with_details(self, appointment: Appointment) -> AppointmentAdminResponse:
        """Enrich appointment with user and application details"""
        # In a real implementation, this would fetch user and application details
        # For now we'll return a simplified version
        return AppointmentAdminResponse(
            id=appointment.id,
            slot_id=appointment.slot_id,
            user_id=appointment.user_id,
            application_id=appointment.application_id,
            status=appointment.status,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
            location_id=appointment.location_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            user={
                "id": appointment.user_id,
                "email": "",  # Would be populated from user service
                "first_name": "",
                "last_name": ""
            },
            application={
                "id": appointment.application_id,
                "type": "",  # Would be populated from application service
                "status": ""
            }
        )

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
