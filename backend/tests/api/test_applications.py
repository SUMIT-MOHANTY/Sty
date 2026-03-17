import os
import uuid
import pytest
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.applications import router as applications_router
from app.models.application import ApplicationStatus
from app.db.models.application import Application, Document

@pytest.fixture
def app():
    """Create a FastAPI test app with applications router"""
    app = FastAPI()
    app.include_router(applications_router, prefix="/api/applications")
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return TestClient(app)

@pytest.fixture
def mock_current_user():
    """Mock the current user for testing"""
    return {
        "id": uuid.uuid4(),
        "email": "testuser@example.com",
        "role": "regular"
    }

@pytest.fixture
def mock_get_current_user(monkeypatch, mock_current_user):
    """Patch the get_current_user dependency"""
    async def mock_get_user():
        return mock_current_user

    # Apply the mock to the applications router
    for route in applications_router.routes:
        if hasattr(route, "dependencies"):
            for i, dependency in enumerate(route.dependencies):
                if "get_current_user" in str(dependency.dependency):
                    route.dependencies[i].dependency = lambda: mock_get_user()

@pytest.fixture
def mock_db(monkeypatch):
    """Mock the database session"""
    class MockDB:
        def __init__(self):
            self.applications = {}
            self.documents = {}
            self.committed = False
            self.rolled_back = False

        def add(self, obj):
            if isinstance(obj, Application):
                obj.id = uuid.uuid4()
                self.applications[obj.id] = obj
            elif isinstance(obj, Document):
                obj.id = uuid.uuid4()
                self.documents[obj.id] = obj

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled_back = True

        def refresh(self, obj):
            pass

        def query(self, model):
            return MockQuery(model, self)

    class MockQuery:
        def __init__(self, model, db):
            self.model = model
            self.db = db
            self.filters = []

        def filter(self, *args):
            self.filters.extend(args)
            return self

        def first(self):
            if self.model == Application:
                for app_id, app in self.db.applications.items():
                    # Simple matching against filter conditions
                    for f in self.filters:
                        if str(f.left).endswith("id") and f.right == app_id:
                            return app
            return None

        def all(self):
            if self.model == Application:
                return list(self.db.applications.values())
            return []

    mock_db_instance = MockDB()

    def get_mock_db():
        return mock_db_instance

    # Apply the mock to the applications router
    for route in applications_router.routes:
        if hasattr(route, "dependencies"):
            for i, dependency in enumerate(route.dependencies):
                if "get_db" in str(dependency.dependency):
                    route.dependencies[i].dependency = get_mock_db

    return mock_db_instance

def test_create_application(client, mock_get_current_user, mock_db, monkeypatch):
    """Test creating a passport application"""
    # Mock SQLAlchemyError to not actually interact with DB
    monkeypatch.setattr(
        "app.api.applications.SQLAlchemyError",
        type("MockSQLAlchemyError", (Exception,), {})
    )

    application_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "date_of_birth": (datetime.now() - timedelta(days=365*30)).isoformat(),
        "phone_number": "1234567890",
        "address_line_1": "123 Main St",
        "city": "Anytown",
        "state": "State",
        "postal_code": "12345",
        "country": "Country",
        "previous_passport": False,
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "0987654321",
        "emergency_contact_relation": "Spouse"
    }

    response = client.post("/api/applications/", json=application_data)

    assert response.status_code == 201
    assert mock_db.committed is True
    assert len(mock_db.applications) == 1

    app_id = list(mock_db.applications.keys())[0]
    created_app = mock_db.applications[app_id]

    assert created_app.first_name == application_data["first_name"]
    assert created_app.last_name == application_data["last_name"]
    assert created_app.email == application_data["email"]
    assert created_app.status == ApplicationStatus.SUBMITTED

def test_get_application(client, mock_get_current_user, mock_db, monkeypatch):
    """Test retrieving a specific application"""
    # Create a test application
    app_id = uuid.uuid4()
    mock_db.applications[app_id] = Application(
        id=app_id,
        user_id=mock_get_current_user["id"],
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        date_of_birth=datetime.now() - timedelta(days=365*30),
        phone_number="1234567890",
        address_line_1="123 Main St",
        city="Anytown",
        state="State",
        postal_code="12345",
        country="Country",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="0987654321",
        emergency_contact_relation="Spouse",
        status=ApplicationStatus.SUBMITTED,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    response = client.get(f"/api/applications/{app_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(app_id)
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Doe"

def test_get_nonexistent_application(client, mock_get_current_user, mock_db):
    """Test attempting to retrieve a nonexistent application"""
    non_existent_id = uuid.uuid4()
    response = client.get(f"/api/applications/{non_existent_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_applications(client, mock_get_current_user, mock_db):
    """Test retrieving all applications for the user"""
    # Create a few test applications
    for i in range(3):
        app_id = uuid.uuid4()
        mock_db.applications[app_id] = Application(
            id=app_id,
            user_id=mock_get_current_user["id"],
            first_name=f"John {i}",
            last_name=f"Doe {i}",
            email=f"john.doe{i}@example.com",
            date_of_birth=datetime.now() - timedelta(days=365*30),
            phone_number="1234567890",
            address_line_1="123 Main St",
            city="Anytown",
            state="State",
            postal_code="12345",
            country="Country",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="0987654321",
            emergency_contact_relation="Spouse",
            status=ApplicationStatus.SUBMITTED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    response = client.get("/api/applications/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3
