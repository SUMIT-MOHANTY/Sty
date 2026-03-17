import os
import re
import uuid
import magic
from typing import List, Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.core.config import settings

# List of allowed file types with their MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf': '.pdf',
    'image/jpeg': '.jpg',
    'image/png': '.png'
}

# Maximum file size in bytes (from settings in MB)
MAX_FILE_SIZE = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal and command injection
    """
    # Get file extension
    _, ext = os.path.splitext(filename)

    # Generate a random filename with original extension
    safe_filename = f"{uuid.uuid4().hex}{ext.lower()}"

    # Make sure the extension is allowed
    allowed_extensions = list(ALLOWED_MIME_TYPES.values())
    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File extension not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
        )

    return safe_filename

async def validate_and_save_document(
    file: UploadFile,
    application_id: int,
    document_type: str
) -> str:
    """
    Validate document upload (type, size, content) and save to storage
    Returns the file path where the document is saved
    """
    # Validate file size
    content = await file.read()
    await file.seek(0)  # Reset file pointer for later processing

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_DOCUMENT_SIZE_MB}MB"
        )

    # Detect MIME type
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: PDF, JPEG, PNG"
        )

    # Ensure the file extension matches the MIME type
    expected_ext = ALLOWED_MIME_TYPES[mime_type]
    _, ext = os.path.splitext(file.filename)
    if ext.lower() != expected_ext:
        raise HTTPException(
            status_code=400,
            detail=f"File extension doesn't match its content"
        )

    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)

    # Create directory structure if it doesn't exist
    upload_dir = Path(settings.DOCUMENT_STORAGE_PATH) / str(application_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save the file
    file_path = upload_dir / safe_filename
    with open(file_path, 'wb') as f:
        f.write(content)

    return str(file_path)
