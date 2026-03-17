from datetime import datetime
from typing import List, Optional
from uuid import UUID
import uuid

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.appointment import Appointment, AppointmentSlot, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

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

    async def create_appointment(self, obj_in: AppointmentCreate, user_id: int) -> Appointment:
        """Create a new appointment with security measures"""
        # Create secure ID for safer lookups
        secure_id = str(uuid.uuid4())

        db_obj = Appointment(
            user_id=user_id,
            application_id=obj_in.application_id,
            location_id=obj_in.location_id,
            appointment_date=obj_in.appointment_date,
            created_by=user_id,
            updated_by=user_id,
            secure_id=secure_id
        )

        # Check for appointment conflicts
        query = select(Appointment).where(
            and_(
                Appointment.location_id == obj_in.location_id,
                Appointment.appointment_date == obj_in.appointment_date,
                Appointment.status == AppointmentStatus.SCHEDULED
            )
        )
        result = await self.session.execute(query)
        existing = result.scalars().first()

        if existing:
            raise ValueError("This appointment time is no longer available")

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        query = select(Appointment).where(Appointment.id == appointment_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_appointments(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Appointment]:
        """Get appointments for a specific user with pagination"""
        query = select(Appointment).where(
            Appointment.user_id == user_id
        ).order_by(
            Appointment.appointment_date.desc()
        ).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_application_appointments(
        self,
        application_id: int,
        user_id: int = None
    ) -> List[Appointment]:
        """Get appointments for a specific application with user check"""
        query = select(Appointment).where(Appointment.application_id == application_id)

        # Add user check for non-admins to prevent unauthorized access
        if user_id is not None:
            query = query.where(Appointment.user_id == user_id)

        query = query.order_by(Appointment.appointment_date.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_appointment(
        self,
        appointment_id: int,
        user_id: int,
        obj_in: AppointmentUpdate,
        is_admin: bool = False
    ) -> Optional[Appointment]:
        """Update an appointment with security checks"""
        db_obj = await self.get_by_id(appointment_id)

        if not db_obj:
            return None

        # Security: Only allow users to update their own appointments unless admin
        if not is_admin and db_obj.user_id != user_id:
            raise ValueError("Not authorized to update this appointment")

        # Prevent changes to past appointments or non-scheduled ones
        if not db_obj.is_modifiable() and not is_admin:
            raise ValueError("This appointment can no longer be modified")

        # Check for appointment conflicts on reschedule
        if obj_in.appointment_date and obj_in.appointment_date != db_obj.appointment_date:
            query = select(Appointment).where(
                and_(
                    Appointment.location_id == db_obj.location_id,
                    Appointment.appointment_date == obj_in.appointment_date,
                    Appointment.status == AppointmentStatus.SCHEDULED,
                    Appointment.id != appointment_id
                )
            )
            result = await self.session.execute(query)
            existing = result.scalars().first()

            if existing:
                raise ValueError("This appointment time is no longer available")

        # Apply updates
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Set audit fields
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by = user_id

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete_appointment(self, appointment_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Cancel an appointment (soft delete) with security checks"""
        db_obj = await self.get_by_id(appointment_id)

        if not db_obj:
            return False

        # Security: Only allow users to cancel their own appointments unless admin
        if not is_admin and db_obj.user_id != user_id:
            raise ValueError("Not authorized to cancel this appointment")

        # Only allow cancellation of future appointments
        if db_obj.appointment_date < datetime.utcnow():
            raise ValueError("Cannot cancel past appointments")

        # Mark as cancelled instead of hard deleting
        db_obj.status = AppointmentStatus.CANCELLED
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by = user_id

        self.session.add(db_obj)
        await self.session.commit()
        return True
