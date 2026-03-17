from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

class DocumentBase(BaseModel):
    application_id: int
    document_type: str
    file_name: str
    file_path: str
    content_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    uploaded_at: datetime
    download_url: HttpUrl

    class Config:
        orm_mode = True
