import pytest
import json
from flask import Flask
from flask_jwt_extended import JWTManager

from app.auth.routes import auth_bp
from app.auth.service import AuthService
from app.models.user import User, UserRole, db
from app.models.token_blacklist import TokenBlacklist

@pytest.fixture
def app():
    """Create Flask test app with auth routes"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register routes
    app.register_blueprint(auth_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()

@pytest.fixture
def user_data():
    """Return test user data"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePassword123!'
    }

def test_register_user(client, user_data):
    """Test user registration"""
    response = client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert 'created' in data['message'].lower()

def test_register_duplicate_user(client, user_data):
    """Test registration with duplicate username"""
    # Register first user
    response = client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    assert response.status_code == 201

    # Try to register again with same data
    response = client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'already exists' in data['error'].lower()

def test_login_success(client, user_data):
    """Test successful login"""
    # Register user
    client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )

    # Login
    login_data = {
        'username_or_email': user_data['username'],
        'password': user_data['password']
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data

def test_login_invalid_credentials(client, user_data):
    """Test login with invalid credentials"""
    # Register user
    client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )

    # Login with wrong password
    login_data = {
        'username_or_email': user_data['username'],
        'password': 'WrongPassword123!'
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_protected_route(client, user_data):
    """Test access to protected route"""
    # Register and login
    client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    login_data = {
        'username_or_email': user_data['username'],
        'password': user_data['password']
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    access_token = data['access_token']

    # Access protected route
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/auth/me', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['username'] == user_data['username']

def test_refresh_token(client, user_data):
    """Test refreshing access token"""
    # Register and login
    client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    login_data = {
        'username_or_email': user_data['username'],
        'password': user_data['password']
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    refresh_token = data['refresh_token']

    # Refresh token
    headers = {'Authorization': f'Bearer {refresh_token}'}
    response = client.post('/api/auth/refresh', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_logout(client, user_data):
    """Test user logout"""
    # Register and login
    client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    login_data = {
        'username_or_email': user_data['username'],
        'password': user_data['password']
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    access_token = data['access_token']

    # Logout
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/auth/logout', headers=headers)
    assert response.status_code == 200

    # Try to access protected route with revoked token
    response = client.get('/api/auth/me', headers=headers)
    assert response.status_code == 401
