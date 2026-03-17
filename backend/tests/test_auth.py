import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.utils.database import get_db, Base
from app.models.user import User

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as c:
        yield c

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 200
    assert "message" in response.json()

def test_register_existing_email(client):
    # Register a user
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123"
        }
    )

    # Try to register again with the same email
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Another User",
            "email": "test@example.com",
            "password": "AnotherPassword123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_unverified_user(client):
    # Register but don't verify
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123"
        }
    )

    # Try to login
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "Password123"}
    )
    assert response.status_code == 403
    assert "Email not verified" in response.json()["detail"]
