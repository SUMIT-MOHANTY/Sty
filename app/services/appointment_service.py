from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from uuid import UUID

from app.db.repositories.appointment_repository import AppointmentRepository
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentSlotCreate,
    AppointmentSlot,
    AppointmentAdminResponse
)

class AppointmentService:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.repository = appointment_repository

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
