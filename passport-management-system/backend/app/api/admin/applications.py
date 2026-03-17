"""
Admin routes for passport applications management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...middleware.auth import get_current_admin_user
from ...models.user import User
from ...models.application import Application
from ...models.status_update import StatusUpdate
from ...schemas.application import (
    ApplicationAdminResponse,
    ApplicationStatusUpdate,
    ApplicationListParams,
    ApplicationDetailedResponse
)

router = APIRouter(prefix="/applications")

@router.get("/", response_model=List[ApplicationAdminResponse])
async def get_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Retrieve all passport applications with filtering options.
    Only accessible to admin users.
    """
    query = db.query(Application)

    # Apply filters if provided
    if status:
        query = query.filter(Application.current_status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Application.application_id.ilike(search_term)) |
            (Application.passport_number.ilike(search_term))
        )

    # Apply pagination
    applications = query.offset(skip).limit(limit).all()

    return applications

@router.get("/{application_id}", response_model=ApplicationDetailedResponse)
async def get_application_details(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Retrieve detailed information for a specific application including status history.
    Only accessible to admin users.
    """
    application = db.query(Application).filter(Application.application_id == application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    # Get all status updates for this application
    status_updates = db.query(StatusUpdate).filter(
        StatusUpdate.application_id == application_id
    ).order_by(StatusUpdate.created_at.desc()).all()

    # Enhance the application data with status history
    application_data = ApplicationDetailedResponse.from_orm(application)
    application_data.status_history = status_updates

    return application_data

@router.put("/{application_id}/status", response_model=ApplicationDetailedResponse)
async def update_application_status(
    application_id: str,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update the status of a passport application.
    Creates a new status update record and updates the application's current status.
    Only accessible to admin users.
    """
    application = db.query(Application).filter(Application.application_id == application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    # Create a new status update record
    new_status = StatusUpdate(
        application_id=application_id,
        status=status_update.status,
        comments=status_update.comments,
        updated_by=current_user.id
    )
    db.add(new_status)

    # Update the application's current status
    application.current_status = status_update.status
    if status_update.status == "approved":
        application.approved_at = new_status.created_at
    elif status_update.status == "rejected":
        application.rejected_at = new_status.created_at

    db.commit()
    db.refresh(application)
    db.refresh(new_status)

    # Get all status updates to include in response
    status_updates = db.query(StatusUpdate).filter(
        StatusUpdate.application_id == application_id
    ).order_by(StatusUpdate.created_at.desc()).all()

    # Create detailed response
    application_data = ApplicationDetailedResponse.from_orm(application)
    application_data.status_history = status_updates

    return application_data

@router.post("/{application_id}/flag", status_code=status.HTTP_200_OK)
async def flag_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Flag an application for further review.
    Only accessible to admin users.
    """
    application = db.query(Application).filter(Application.application_id == application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    application.is_flagged = True
    db.commit()

    return {"message": f"Application {application_id} has been flagged for review"}

@router.post("/{application_id}/unflag", status_code=status.HTTP_200_OK)
async def unflag_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Remove flag from an application.
    Only accessible to admin users.
    """
    application = db.query(Application).filter(Application.application_id == application_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    application.is_flagged = False
    db.commit()

    return {"message": f"Flag has been removed from application {application_id}"}
