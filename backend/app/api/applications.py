import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.application import (
    ApplicationCreate,
    ApplicationResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentType
)
from app.db.models.application import Application, Document, StatusUpdate
from app.models.user import User

router = APIRouter()

UPLOAD_DIRECTORY = "uploads/documents"

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new passport application.

    Parameters:
    - application: Application data
    - current_user: Currently authenticated user
    - db: Database session

    Returns:
    - The created application
    """
    try:
        # Create new application
        db_application = Application(
            user_id=current_user.id,
            **application.dict()
        )

        db.add(db_application)
        db.commit()
        db.refresh(db_application)

        return db_application
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/{application_id}/documents", response_model=DocumentResponse)
async def upload_document(
    application_id: UUID,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document for a specific application.

    Parameters:
    - application_id: ID of the application
    - document_type: Type of document being uploaded
    - file: The document file
    - current_user: Currently authenticated user
    - db: Database session

    Returns:
    - The created document metadata
    """
    # Check if application exists and belongs to the user
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or you don't have permission to access it"
        )

    # Create directory if it doesn't exist
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload file: {str(e)}"
        )

    # Create document record in database
    try:
        db_document = Document(
            application_id=application_id,
            document_type=document_type,
            filename=file.filename,
            file_path=file_path,
            mime_type=file.content_type or "application/octet-stream"
        )

        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        return db_document
    except SQLAlchemyError as e:
        db.rollback()
        # Clean up the file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications for the current user.

    Parameters:
    - current_user: Currently authenticated user
    - db: Database session

    Returns:
    - List of applications belonging to the user
    """
    applications = db.query(Application).filter(
        Application.user_id == current_user.id
    ).all()

    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific application by ID.

    Parameters:
    - application_id: ID of the application
    - current_user: Currently authenticated user
    - db: Database session

    Returns:
    - The requested application if it belongs to the user
    """
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or you don't have permission to access it"
        )

    return application
