from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.models.appointment import Appointment, AppointmentSlot, AppointmentStatus

class AppointmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_appointment_slot(self, slot_data) -> AppointmentSlot:
        """Create a new appointment slot"""
        db_slot = AppointmentSlot(
            location_id=slot_data.location_id,
            start_time=slot_data.start_time,
            end_time=slot_data.end_time,
            max_appointments=slot_data.max_appointments,
            is_available=True
        )
        self.session.add(db_slot)
        await self.session.commit()
        await self.session.refresh(db_slot)
        return db_slot

    async def get_appointment_slots(
        self,
        location_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        available_only: bool = False
    ) -> List[AppointmentSlot]:
        """Get appointment slots with optional filtering"""
        query = select(AppointmentSlot)

        # Apply filters
        conditions = []
        if location_id:
            conditions.append(AppointmentSlot.location_id == location_id)
        if start_date:
            conditions.append(AppointmentSlot.start_time >= start_date)
        if end_date:
            conditions.append(AppointmentSlot.end_time <= end_date)
        if available_only:
            conditions.append(AppointmentSlot.is_available == True)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_slots_by_time_range(
        self,
        location_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[AppointmentSlot]:
        """Check if slots exist for a given time range and location"""
        query = select(AppointmentSlot).where(
            and_(
                AppointmentSlot.location_id == location_id,
                or_(
                    and_(
                        AppointmentSlot.start_time <= start_time,
                        AppointmentSlot.end_time > start_time
                    ),
                    and_(
                        AppointmentSlot.start_time < end_time,
                        AppointmentSlot.end_time >= end_time
                    ),
                    and_(
                        AppointmentSlot.start_time >= start_time,
                        AppointmentSlot.end_time <= end_time
                    )
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_slot_by_id(self, slot_id: UUID) -> Optional[AppointmentSlot]:
        """Get appointment slot by ID"""
        query = select(AppointmentSlot).where(AppointmentSlot.id == slot_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_appointment_slot(self, slot_id: UUID, slot_data) -> AppointmentSlot:
        """Update an appointment slot"""
        db_slot = await self.get_slot_by_id(slot_id)
        if not db_slot:
            return None

        # Update slot attributes
        db_slot.location_id = slot_data.location_id
        db_slot.start_time = slot_data.start_time
        db_slot.end_time = slot_data.end_time
        db_slot.max_appointments = slot_data.max_appointments
        db_slot.is_available = slot_data.is_available

        await self.session.commit()
        await self.session.refresh(db_slot)
        return db_slot

    async def delete_appointment_slot(self, slot_id: UUID) -> bool:
        """Delete an appointment slot"""
        db_slot = await self.get_slot_by_id(slot_id)
        if not db_slot:
            return False

        await self.session.delete(db_slot)
        await self.session.commit()
        return True

    async def get_appointments_by_slot_id(self, slot_id: UUID) -> List[Appointment]:
        """Get appointments by slot ID"""
        query = select(Appointment).where(Appointment.slot_id == slot_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_appointments(
        self,
        location_id: Optional[UUID] = None,
        status: Optional[AppointmentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[UUID] = None
    ) -> List[Appointment]:
        """Get appointments with optional filtering"""
        query = select(Appointment)

        # Apply filters
        conditions = []
        if location_id:
            conditions.append(Appointment.location_id == location_id)
        if status:
            conditions.append(Appointment.status == status)
        if start_date:
            conditions.append(Appointment.start_time >= start_date)
        if end_date:
            conditions.append(Appointment.end_time <= end_date)
        if user_id:
            conditions.append(Appointment.user_id == user_id)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalars().all()
