from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from backend.app.db.session import get_db
from backend.app.schemas.application import ApplicationCreate, ApplicationResponse
from backend.app.services.application_service import create_application, get_user_applications
from backend.app.core.security import get_current_user
from backend.app.schemas.user import User

router = APIRouter()

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def submit_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Submit a new passport application.
    """
    return create_application(db=db, application=application, user_id=current_user.id)

@router.get("/", response_model=List[ApplicationResponse])
def read_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve applications for the current user.
    """
    return get_user_applications(db=db, user_id=current_user.id, skip=skip, limit=limit)
