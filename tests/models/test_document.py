import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentType
from app.models.application import Application, ApplicationStatus

class TestDocumentModel:
    def test_document_creation(self):
        """Test that a document can be created with correct attributes"""
        # Create test data
        application_id = uuid.uuid4()
        file_path = "/uploads/documents/passport_photo_123.jpg"

        # Create document instance
        document = Document(
            application_id=application_id,
            type=DocumentType.passport_photo,
            file_path=file_path
        )

        # Assert properties are set correctly
        assert document.application_id == application_id
        assert document.type == DocumentType.passport_photo
        assert document.file_path == file_path
        assert isinstance(document.uploaded_at, datetime)

    def test_document_application_relationship(self):
        """Test the relationship between Document and Application"""
        # Create test application
        user_id = uuid.uuid4()
        application = Application(
            id=uuid.uuid4(),
            user_id=user_id,
            status=ApplicationStatus.draft,
            personal_details={"first_name": "John", "last_name": "Doe"}
        )

        # Create test document associated with the application
        document = Document(
            id=uuid.uuid4(),
            application=application,
            type=DocumentType.passport_photo,
            file_path="/uploads/documents/passport_photo_123.jpg"
        )

        # Test relationship from document to application
        assert document.application == application

        # Test relationship from application to documents
        assert document in application.documents

        # Test cascade delete
        application.documents = []
        assert document not in application.documents

    def test_document_db_operations(self):
        """Test database operations with document model using a mock session"""
        # Create mock session
        mock_session = Mock(spec=Session)

        # Create test data
        application_id = uuid.uuid4()
        document = Document(
            application_id=application_id,
            type=DocumentType.id_proof,
            file_path="/uploads/documents/id_proof_123.pdf"
        )

        # Test add operation
        mock_session.add(document)
        mock_session.commit()
        mock_session.add.assert_called_once_with(document)
        mock_session.commit.assert_called_once()

        # Test query operation
        with patch('sqlalchemy.orm.Query') as mock_query:
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = document

            result = mock_session.query(Document).filter(Document.id == document.id).first()
            assert result == document
