import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.appointment import AppointmentStatus
from app.services.appointment_service import AppointmentService

client = TestClient(app)

# Mock authenticated user for testing
def get_test_user():
    return {"user_id": 1}

# Mock JWT token
test_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjcxNzcxMjAwfQ.mock_signature"

def test_create_appointment_success(monkeypatch):
    # Setup
    async def mock_create(*args, **kwargs):
        return {
            "id": 1,
            "user_id": 1,
            "application_id": 1,
            "location_id": 1,
            "appointment_date": datetime.utcnow() + timedelta(days=3),
            "status": AppointmentStatus.SCHEDULED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_modifiable": True,
            "location_name": "Test Office"
        }

    monkeypatch.setattr(AppointmentService, "create_appointment", mock_create)
    monkeypatch.setattr("app.core.security.get_current_user", lambda *args: get_test_user())

    # Test
    response = client.post(
        "/api/appointments/",
        json={
            "application_id": 1,
            "location_id": 1,
            "appointment_date": (datetime.utcnow() + timedelta(days=3)).isoformat()
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["status"] == "scheduled"
    assert data["is_modifiable"] == True

def test_create_appointment_rate_limited(monkeypatch):
    # Setup
    async def mock_create(*args, **kwargs):
        raise ValueError("Rate limit exceeded. Please try again later.")

    monkeypatch.setattr(AppointmentService, "create_appointment", mock_create)
    monkeypatch.setattr("app.core.security.get_current_user", lambda *args: get_test_user())

    # Test
    response = client.post(
        "/api/appointments/",
        json={
            "application_id": 1,
            "location_id": 1,
            "appointment_date": (datetime.utcnow() + timedelta(days=3)).isoformat()
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 400
    assert "Rate limit exceeded" in response.json()["detail"]

def test_update_appointment_unauthorized(monkeypatch):
    # Setup
    async def mock_update(*args, **kwargs):
        raise ValueError("Not authorized to update this appointment")

    monkeypatch.setattr(AppointmentService, "update_appointment", mock_update)
    monkeypatch.setattr("app.core.security.get_current_user", lambda *args: get_test_user())

    # Test
    response = client.put(
        "/api/appointments/1",
        json={
            "appointment_date": (datetime.utcnow() + timedelta(days=5)).isoformat()
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 400
    assert "Not authorized" in response.json()["detail"]

def test_cancel_appointment_requires_reason(monkeypatch):
    # Test
    response = client.delete(
        "/api/appointments/1",
        json={},  # Missing cancellation_reason
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 422  # Validation error
