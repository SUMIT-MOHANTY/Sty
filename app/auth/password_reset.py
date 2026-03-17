from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import datetime
from marshmallow import Schema, fields, validate, ValidationError
from ..models.user import User, db
from .service import AuthService

# Blueprint for password reset routes
password_bp = Blueprint('password', __name__, url_prefix='/api/auth')

# Schema for request validation
class RequestResetSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

# In-memory token storage (replace with database for production)
reset_tokens = {}

@password_bp.route('/request-reset', methods=['POST'])
def request_password_reset():
    """Request a password reset link"""
    # Validate request
    schema = RequestResetSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 400

    # Find user
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        # Return success even if user doesn't exist (prevents user enumeration)
        return jsonify({"message": "If your email is registered, you will receive a reset link"}), 200

    # Generate reset token
    token = str(uuid.uuid4())
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    # Store token (in production, store in database with proper hashing)
    reset_tokens[token] = {
        'user_id': user.id,
        'expires': expiry
    }

    # In a real app, send email with reset link
    # send_reset_email(user.email, token)

    # For demo/testing purposes, return token directly
    # In production, don't return the token in response
    return jsonify({
        "message": "Password reset link sent",
        "debug_token": token  # Remove in production
    }), 200

@password_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    # Validate request
    schema = ResetPasswordSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 400

    # Check if token exists and is valid
    token = data['token']
    if token not in reset_tokens:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Check if token is expired
    token_data = reset_tokens[token]
    if token_data['expires'] < datetime.datetime.utcnow():
        # Remove expired token
        del reset_tokens[token]
        return jsonify({"error": "Reset token has expired"}), 400

    # Validate password
    is_valid, message = AuthService.validate_password_strength(data['password'])
    if not is_valid:
        return jsonify({"error": message}), 400

    # Reset password
    user = User.query.get(token_data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
    user.password = data['password']
    user.failed_login_attempts = 0  # Reset login attempts

    # Commit changes
    try:
        db.session.commit()
        # Remove used token
        del reset_tokens[token]
        return jsonify({"message": "Password has been reset successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error resetting password: {str(e)}"}), 500

@password_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for authenticated user"""
    # Validate request
    schema = ChangePasswordSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 401

    # Validate new password
    is_valid, message = AuthService.validate_password_strength(data['new_password'])
    if not is_valid:
        return jsonify({"error": message}), 400

    # Update password
    user.password = data['new_password']

    # Commit changes
    try:
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error changing password: {str(e)}"}), 500
