import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import json

from ..app.main import app
from ..app.models.appointment import Appointment
from ..app.models.time_slot import TimeSlot
from ..app.models.location import Location
from ..app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def test_user():
    return {"id": 1, "email": "user@example.com", "is_admin": False}

@pytest.fixture
def test_admin():
    return {"id": 2, "email": "admin@example.com", "is_admin": True}

@pytest.fixture
def user_token(test_user):
    return create_access_token({"sub": test_user["email"], "user_id": test_user["id"]})

@pytest.fixture
def admin_token(test_admin):
    return create_access_token({"sub": test_admin["email"], "user_id": test_admin["id"]})

def test_get_available_slots(mocker):
    # Mock authentication
    mocker.patch("app.core.security.get_current_user", return_value={"id": 1, "email": "test@example.com"})

    # Mock database queries
    mock_location = MagicMock()
    mock_location.id = 1

    mock_time_slot1 = MagicMock()
    mock_time_slot1.id = 1
    mock_time_slot1.location_id = 1
    mock_time_slot1.start_time = datetime.strptime("09:00", "%H:%M").time()
    mock_time_slot1.end_time = datetime.strptime("09:30", "%H:%M").time()
    mock_time_slot1.date = datetime.now().date() + timedelta(days=1)

    mock_time_slot2 = MagicMock()
    mock_time_slot2.id = 2
    mock_time_slot2.location_id = 1
    mock_time_slot2.start_time = datetime.strptime("10:00", "%H:%M").time()
    mock_time_slot2.end_time = datetime.strptime("10:30", "%H:%M").time()
    mock_time_slot2.date = datetime.now().date() + timedelta(days=1)

    mocker.patch("sqlalchemy.orm.session.Session.query").return_value.filter.return_value.first.return_value = mock_location
    mocker.patch("sqlalchemy.orm.session.Session.query").return_value.filter.return_value.all.return_value = [mock_time_slot1, mock_time_slot2]

    # Test the endpoint
    response = client.get(
        f"/appointments/available-slots?location_id=1&date={(datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')}",
        headers={"Authorization": f"Bearer test_token"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_book_appointment(mocker, user_token):
    # Mock authentication
    mocker.patch("app.core.security.get_current_user", return_value={"id": 1, "email": "test@example.com"})

    # Mock time slot
    mock_time_slot = MagicMock()
    mock_time_slot.id = 1
    mock_time_slot.location_id = 1
    mock_time_slot.date = datetime.now().date() + timedelta(days=1)

    # Mock database queries
    mocker.patch("sqlalchemy.orm.session.Session.query").return_value.filter.return_value.first.return_value = None
    mocker.patch("sqlalchemy.orm.session.Session.query").return_value.filter.return_value.with_for_update.return_value.first.return_value = None
    mocker.patch("sqlalchemy.orm.session.Session.add")
    mocker.patch("sqlalchemy.orm.session.Session.commit")
    mocker.patch("sqlalchemy.orm.session.Session.refresh")

    # Mock the appointment creation
    mock_new_appointment = MagicMock()
    mock_new_appointment.id = 1
    mock_new_appointment.user_id = 1
    mock_new_appointment.application_id = 1
    mock_new_appointment.location_id = 1
    mock_new_appointment.time_slot_id = 1
    mock_new_appointment.appointment_date = datetime.now().date() + timedelta(days=1)
    mock_new_appointment.status = "scheduled"
    mock_new_appointment.created_at = datetime.now()
    mock_new_appointment.updated_at = datetime.now()

    mocker.patch("app.models.appointment.Appointment", return_value=mock_new_appointment)

    # Test the endpoint
    response = client.post(
        "/appointments/",
        headers={
            "Authorization": f"Bearer {user_token}",
            "X-CSRF-Token": "valid_csrf_token_12345678901234567890"
        },
        json={
            "application_id": 1,
            "time_slot_id": 1
        }
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["status"] == "scheduled"

def test_get_appointment_unauthorized(mocker, user_token):
    # Mock authentication
    mocker.patch("app.core.security.get_current_user", return_value={"id": 1, "email": "test@example.com"})

    # Mock appointment belonging to another user
    mock_appointment = MagicMock()
    mock_appointment.id = 1
    mock_appointment.user_id = 2  # Different user

    mocker.patch("sqlalchemy.orm.session.Session.query").return_value.filter.return_value.first.return_value = mock_appointment

    # Test the endpoint - should not reveal the appointment
    response = client.get(
        "/appointments/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_rate_limiting(mocker, user_token):
    # Mock authentication
    mocker.patch("app.core.security.get_current_user", return_value={"id": 1, "email": "test@example.com"})

    # Mock rate limiter to trigger limit exceeded
    mocker.patch("app.middleware.rate_limit.rate_limiter", side_effect=HTTPException(status_code=429, detail="Rate limit exceeded"))

    # Test the endpoint
    response = client.get(
        f"/appointments/available-slots?location_id=1&date={(datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
