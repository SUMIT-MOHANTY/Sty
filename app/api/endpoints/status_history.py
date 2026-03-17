from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application, ApplicationStatus
from app.schemas.status_history import StatusHistory, StatusUpdate
from app.services.status_history import StatusHistoryService

router = APIRouter(prefix="/applications", tags=["status_history"])

@router.get("/{application_id}/status-history", response_model=List[StatusHistory])
def get_application_status_history(
    application_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve the complete status history for a specific application.
    """
    service = StatusHistoryService(db)
    history = service.get_application_status_history(application_id)
    if not history:
        raise HTTPException(status_code=404, detail="Application not found")
    return history

@router.get("/status-updates", response_model=List[StatusUpdate])
def get_status_updates(
    user_id: int = Query(..., description="Filter status updates by user ID"),
    status: Optional[str] = Query(None, description="Filter by specific status"),
    limit: int = Query(10, description="Number of records to return"),
    skip: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    """
    Get recent status updates for applications associated with a user.
    Optionally filter by specific status.
    """
    service = StatusHistoryService(db)
    return service.get_status_updates(
        user_id=user_id, status=status, limit=limit, skip=skip
    )

@router.get("/status-statistics", response_model=dict)
def get_status_statistics(
    user_id: Optional[int] = Query(None, description="Filter statistics by user ID"),
    db: Session = Depends(get_db),
):
    """
    Get statistics about application statuses.
    Optionally filter by user ID.
    """
    service = StatusHistoryService(db)
    return service.get_status_statistics(user_id=user_id)
