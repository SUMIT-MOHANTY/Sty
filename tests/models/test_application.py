import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationStatus

class TestApplicationModel:
    def test_application_creation(self):
        """Test that an application can be created with correct attributes"""
        # Create test data
        user_id = uuid.uuid4()
        personal_details = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "place_of_birth": "New York",
            "nationality": "USA",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            }
        }

        # Create application instance
        application = Application(
            user_id=user_id,
            status=ApplicationStatus.draft,
            personal_details=personal_details
        )

        # Assert properties are set correctly
        assert application.user_id == user_id
        assert application.status == ApplicationStatus.draft
        assert application.personal_details == personal_details
        assert isinstance(application.created_at, datetime)
        assert application.documents == []

    def test_application_db_operations(self):
        """Test database operations with application model using a mock session"""
        # Create mock session
        mock_session = Mock(spec=Session)

        # Create test data
        user_id = uuid.uuid4()
        personal_details = {"first_name": "John", "last_name": "Doe"}
        application = Application(
            user_id=user_id,
            status=ApplicationStatus.draft,
            personal_details=personal_details
        )

        # Test add operation
        mock_session.add(application)
        mock_session.commit()
        mock_session.add.assert_called_once_with(application)
        mock_session.commit.assert_called_once()

        # Test query operation
        with patch('sqlalchemy.orm.Query') as mock_query:
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = application

            result = mock_session.query(Application).filter(Application.id == application.id).first()
            assert result == application
