from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusResponse
)
from app.models.application import Application, ApplicationStatus
from app.models.status_update import StatusUpdate
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Logic for creating a new application
    db_application = Application(
        user_id=current_user.id,
        application_type=application.application_type,
        application_number=generate_application_number(),
        status=ApplicationStatus.SUBMITTED,
        notes=application.notes
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    # Create initial status update
    status_update = StatusUpdate(
        application_id=db_application.id,
        status=ApplicationStatus.SUBMITTED,
        comment="Application submitted successfully",
        created_by=current_user.id
    )
    db.add(status_update)
    db.commit()

    return db_application

@router.get("/", response_model=List[ApplicationResponse])
def get_user_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    applications = db.query(Application).filter(
        Application.user_id == current_user.id
    ).all()
    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return application

@router.get("/{application_id}/status", response_model=ApplicationStatusResponse)
def get_application_status(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    status_updates = db.query(StatusUpdate).filter(
        StatusUpdate.application_id == application_id
    ).order_by(StatusUpdate.created_at).all()

    return {
        "application": application,
        "current_status": application.status,
        "status_history": status_updates
    }

# Helper function to generate unique application number
def generate_application_number():
    import uuid
    import datetime

    prefix = "PPS"  # Passport Processing System
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()

    return f"{prefix}-{date_str}-{unique_id}"
