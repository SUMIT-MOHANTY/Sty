from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from ..core.database import get_db
from ..models.application import Application
from ..models.status_update import StatusUpdate
from ..models.user import User
from ..schemas.application import ApplicationCreate, ApplicationResponse
from ..schemas.status_update import StatusUpdateResponse
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["applications"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new passport application
    """
    db_application = Application(
        user_id=current_user.id,
        application_type=application.application_type,
        first_name=application.first_name,
        last_name=application.last_name,
        date_of_birth=application.date_of_birth,
        place_of_birth=application.place_of_birth,
        gender=application.gender,
        address=application.address,
        phone_number=application.phone_number,
        emergency_contact=application.emergency_contact,
        previous_passport_number=application.previous_passport_number
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    # Create initial status update (SUBMITTED)
    initial_status = StatusUpdate(
        application_id=db_application.id,
        status="SUBMITTED",
        notes="Application successfully submitted"
    )
    db.add(initial_status)
    db.commit()

    return db_application

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an application by ID
    """
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if the user is the owner or an admin
    if application.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this application")

    return application

@router.get("/", response_model=List[ApplicationResponse])
def get_user_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all applications for the current user
    """
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications

@router.get("/{application_id}/status-history", response_model=List[StatusUpdateResponse])
def get_status_history(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status history for an application
    """
    # First check if the application exists and user has access
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if the user is the owner or an admin
    if application.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this application")

    # Get the status history
    status_updates = db.query(StatusUpdate).filter(
        StatusUpdate.application_id == application_id
    ).order_by(StatusUpdate.created_at.desc()).all()

    return status_updates

@router.get("/{application_id}/latest-status", response_model=StatusUpdateResponse)
def get_latest_status(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the latest status for an application
    """
    # First check if the application exists and user has access
    application = db.query(Application).filter(Application.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if the user is the owner or an admin
    if application.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this application")

    # Get the latest status
    latest_status = db.query(StatusUpdate).filter(
        StatusUpdate.application_id == application_id
    ).order_by(StatusUpdate.created_at.desc()).first()

    if not latest_status:
        raise HTTPException(status_code=404, detail="No status updates found for this application")

    return latest_status
