import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.application import Application, ApplicationStatus
from app.services.status_history import StatusHistoryService

@pytest.fixture
def test_app():
    return TestClient(app)

def test_get_application_status_history(test_app, db: Session, test_user):
    # Create test application
    application = Application(
        user_id=test_user.id,
        company_name="Test Company",
        position_title="Test Position",
        location="Test Location",
        current_status="applied",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Create test status history entries
    statuses = [
        ApplicationStatus(
            application_id=application.id,
            status="applied",
            notes="Initial application submitted",
            created_by=test_user.id,
        ),
        ApplicationStatus(
            application_id=application.id,
            status="interview_scheduled",
            notes="Interview scheduled for next week",
            created_by=test_user.id,
        ),
    ]
    db.add_all(statuses)
    db.commit()

    # Test authenticated endpoint
    response = test_app.get(
        f"/applications/{application.id}/status-history",
        headers={"Authorization": f"Bearer {test_user.access_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["status"] == "interview_scheduled"
    assert data[1]["status"] == "applied"

def test_get_status_updates(test_app, db: Session, test_user):
    # Create test application (reusing from previous test)
    application = db.query(Application).filter(Application.user_id == test_user.id).first()
    if not application:
        application = Application(
            user_id=test_user.id,
            company_name="Test Company",
            position_title="Test Position",
            location="Test Location",
            current_status="applied",
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        # Add status history
        status = ApplicationStatus(
            application_id=application.id,
            status="applied",
            notes="Initial application",
            created_by=test_user.id,
        )
        db.add(status)
        db.commit()

    # Test the endpoint
    response = test_app.get(
        f"/applications/status-updates?user_id={test_user.id}",
        headers={"Authorization": f"Bearer {test_user.access_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "application_id" in data[0]
    assert "company_name" in data[0]
    assert "status" in data[0]

def test_get_status_statistics(test_app, db: Session, test_user):
    # Test the endpoint
    response = test_app.get(
        f"/applications/status-statistics?user_id={test_user.id}",
        headers={"Authorization": f"Bearer {test_user.access_token}"},
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "by_status" in data
    assert isinstance(data["by_status"], dict)
