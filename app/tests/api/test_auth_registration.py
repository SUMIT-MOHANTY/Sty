import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import re
import bcrypt

# Import the main application (assumes it's at /workspace/app/main.py)
from app.main import app
from app.services.email_service import EmailVerificationService

client = TestClient(app)

@pytest.fixture
def mock_db():
    """Create a mock database session for testing"""
    db = MagicMock()
    # Mock the query for existing user to return None initially
    db.execute.return_value.fetchone.return_value = None
    return db

def test_register_user_success(mock_db):
    """Test successful user registration"""
    # Patch the get_db dependency to return our mock
    with patch('app.api.auth.routes.get_db', return_value=mock_db):
        # Patch email service to avoid actually sending emails
        with patch.object(EmailVerificationService, 'send_verification_email', return_value=True):
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "Password123",
                    "confirm_password": "Password123",
                    "first_name": "Test",
                    "last_name": "User"
                }
            )

            # Check response
            assert response.status_code == 201
            data = response.json()
            assert "user_id" in data
            assert data["email"] == "test@example.com"
            assert data["message"] == "Verification email sent"

            # Verify DB interactions
            # 1. Check if user exists
            mock_db.execute.assert_any_call(
                "SELECT * FROM users WHERE email = :email",
                {"email": "test@example.com"}
            )

            # 2. Insert user
            mock_db.execute.assert_called()
            # Check that we've committed the transaction
            mock_db.commit.assert_called_once()

def test_register_duplicate_email(mock_db):
    """Test registration with an email that already exists"""
    # Mock that a user with this email already exists
    mock_db.execute.return_value.fetchone.return_value = {"id": "existing-id"}

    with patch('app.api.auth.routes.get_db', return_value=mock_db):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "existing@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
                "first_name": "Test",
                "last_name": "User"
            }
        )

        # Check response
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

def test_register_password_mismatch():
    """Test registration with mismatched passwords"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123",
            "confirm_password": "DifferentPassword123",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    # Check response
    assert response.status_code == 422
    assert "passwords do not match" in response.json()["detail"][0]["msg"].lower()

def test_register_invalid_email():
    """Test registration with an invalid email format"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "password": "Password123",
            "confirm_password": "Password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    # Check response
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["msg"].lower()

def test_register_weak_password():
    """Test registration with a weak password"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "password",
            "confirm_password": "password",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    # Check response
    assert response.status_code == 422
    assert "uppercase" in response.json()["detail"][0]["msg"].lower()

def test_verify_email_success(mock_db):
    """Test successful email verification"""
    # Mock token verification
    token_data = {
        "user_id": "test-user-id",
        "email": "test@example.com"
    }

    with patch.object(EmailVerificationService, 'verify_token', return_value=token_data):
        with patch('app.api.auth.routes.get_db', return_value=mock_db):
            response = client.post(
                "/api/auth/verify-email",
                json={"token": "valid-token"}
            )

            # Check response
            assert response.status_code == 200
            assert response.json()["message"] == "Email verified successfully"

            # Verify DB interaction
            mock_db.execute.assert_called_with(
                "UPDATE users SET is_verified = TRUE WHERE id = :user_id",
                {"user_id": "test-user-id"}
            )
            mock_db.commit.assert_called_once()

def test_verify_email_invalid_token():
    """Test email verification with an invalid token"""
    with patch.object(EmailVerificationService, 'verify_token', return_value=None):
        response = client.post(
            "/api/auth/verify-email",
            json={"token": "invalid-token"}
        )

        # Check response
        assert response.status_code == 400
        assert "invalid or expired token" in response.json()["detail"].lower()
