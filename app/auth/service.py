from datetime import datetime, timezone
import os
from flask import current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt
)
import re

from ..models.user import User, db
from ..models.token_blacklist import TokenBlacklist

class AuthService:
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets minimum security requirements"""
        min_length = int(os.environ.get('PASSWORD_MIN_LENGTH', 12))

        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"

        # Check for complexity requirements
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if not (has_uppercase and has_lowercase and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, digit, and special characters"

        # Check for common passwords
        common_passwords = ["Password123!", "Admin123!", "Welcome123!", "Qwerty123!"]
        if password in common_passwords:
            return False, "Password is too common. Please choose a stronger password"

        return True, "Password meets requirements"

    @staticmethod
    def register_user(username, email, password, role=None):
        # Check if user already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return False, "Username or email already exists"

        # Validate password strength
        is_valid, message = AuthService.validate_password_strength(password)
        if not is_valid:
            return False, message

        # Create new user
        new_user = User(username=username, email=email)
        new_user.password = password  # This will hash the password

        db.session.add(new_user)
        try:
            db.session.commit()
            return True, "User created successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating user: {str(e)}"

    @staticmethod
    def authenticate_user(username_or_email, password):
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        # Check if user exists and is active
        if not user:
            return None, "Invalid credentials"

        if not user.active:
            return None, "Account is disabled"

        if user.is_account_locked():
            return None, "Account is locked due to too many failed login attempts"

        # Verify password
        if not user.check_password(password):
            user.increment_failed_login()
            return None, "Invalid credentials"

        # Reset failed login attempts on successful login
        user.reset_failed_login()

        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            }
        )
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, "Login successful"

    @staticmethod
    def logout(token_jti, user_id, expires_at, token_type="access"):
        """Add token to blacklist when user logs out"""
        blacklisted_token = TokenBlacklist(
            jti=token_jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(expires_at, timezone.utc)
        )
        db.session.add(blacklisted_token)
        try:
            db.session.commit()
            return True, "Logged out successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error during logout: {str(e)}"

    @staticmethod
    def refresh_access_token():
        """Generate new access token from refresh token"""
        identity = get_jwt_identity()
        user = User.query.get(identity)
        if not user or not user.active:
            return None, "Invalid user or account disabled"

        new_access_token = create_access_token(
            identity=identity,
            additional_claims={
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            }
        )
        return {'access_token': new_access_token}, "Token refreshed"
