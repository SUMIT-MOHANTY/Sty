"""
Admin routes for dashboard statistics and monitoring.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...middleware.auth import get_current_admin_user
from ...models.user import User
from ...models.application import Application
from ...models.appointment import Appointment
from ...schemas.admin import AdminDashboardStats

router = APIRouter(prefix="/dashboard")

@router.get("/stats", response_model=AdminDashboardStats)
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get aggregated statistics for the admin dashboard.
    Includes counts of applications by status, appointments, etc.
    Only accessible to admin users.
    """
    # Get application counts by status
    app_stats = db.query(
        Application.current_status,
        func.count(Application.id).label('count')
    ).group_by(Application.current_status).all()

    # Create a dictionary of status counts
    application_counts = {status: count for status, count in app_stats}

    # Total applications
    total_applications = sum(application_counts.values())

    # Get appointment counts by status
    appt_stats = db.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).group_by(Appointment.status).all()

    # Create a dictionary of appointment status counts
    appointment_counts = {status: count for status, count in appt_stats}

    # Total appointments
    total_appointments = sum(appointment_counts.values())

    # Count flagged applications
    flagged_applications = db.query(func.count(Application.id)).filter(
        Application.is_flagged == True
    ).scalar()

    return AdminDashboardStats(
        total_applications=total_applications,
        total_appointments=total_appointments,
        pending_applications=application_counts.get('pending', 0),
        approved_applications=application_counts.get('approved', 0),
        rejected_applications=application_counts.get('rejected', 0),
        flagged_applications=flagged_applications,
        scheduled_appointments=appointment_counts.get('scheduled', 0),
        completed_appointments=appointment_counts.get('completed', 0),
        cancelled_appointments=appointment_counts.get('cancelled', 0)
    )
