from datetime import datetime
from typing import List, Optional
import uuid
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_appointment(self, obj_in: AppointmentCreate, user_id: int) -> Appointment:
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
        existing = self.db.query(Appointment).filter(
            Appointment.location_id == obj_in.location_id,
            Appointment.appointment_date == obj_in.appointment_date,
            Appointment.status == AppointmentStatus.SCHEDULED
        ).first()

        if existing:
            raise ValueError("This appointment time is no longer available")

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_user_appointments(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Appointment]:
        """Get appointments for a specific user with pagination"""
        return (
            self.db.query(Appointment)
            .filter(Appointment.user_id == user_id)
            .order_by(Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_application_appointments(
        self,
        application_id: int,
        user_id: int = None
    ) -> List[Appointment]:
        """Get appointments for a specific application with user check"""
        query = self.db.query(Appointment).filter(Appointment.application_id == application_id)

        # Add user check for non-admins to prevent unauthorized access
        if user_id is not None:
            query = query.filter(Appointment.user_id == user_id)

        return query.order_by(Appointment.appointment_date.desc()).all()

    def update_appointment(
        self,
        appointment_id: int,
        user_id: int,
        obj_in: AppointmentUpdate,
        is_admin: bool = False
    ) -> Optional[Appointment]:
        """Update an appointment with security checks"""
        db_obj = self.get_by_id(appointment_id)

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
            existing = self.db.query(Appointment).filter(
                Appointment.location_id == db_obj.location_id,
                Appointment.appointment_date == obj_in.appointment_date,
                Appointment.status == AppointmentStatus.SCHEDULED,
                Appointment.id != appointment_id
            ).first()

            if existing:
                raise ValueError("This appointment time is no longer available")

        # Apply updates
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Set audit fields
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by = user_id

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_appointment(self, appointment_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Cancel an appointment (soft delete) with security checks"""
        db_obj = self.get_by_id(appointment_id)

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

        self.db.add(db_obj)
        self.db.commit()
        return True
