from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt,
    current_user
)
from marshmallow import Schema, fields, validate, ValidationError

from .service import AuthService
from ..middleware.rate_limiter import limiter
from ..models.token_blacklist import TokenBlacklist, db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Request validation schemas
class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class LoginSchema(Schema):
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10/hour")  # Rate limit registrations
def register():
    """Register a new user"""
    # Validate request data
    schema = RegisterSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 400

    # Register user with service
    success, message = AuthService.register_user(
        data['username'],
        data['email'],
        data['password']
    )

    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10/minute")  # Rate limit login attempts
def login():
    """Authenticate user and issue JWT token"""
    # Validate request data
    schema = LoginSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 400

    # Authenticate user
    result, message = AuthService.authenticate_user(
        data['username_or_email'],
        data['password']
    )

    if result:
        return jsonify({
            "message": message,
            "access_token": result['access_token'],
            "refresh_token": result['refresh_token'],
            "user": result['user']
        }), 200
    return jsonify({"error": message}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    # Check if token is blacklisted
    jwt_data = get_jwt()
    token_jti = jwt_data['jti']

    if TokenBlacklist.query.filter_by(jti=token_jti).first():
        return jsonify({"error": "Token has been revoked"}), 401

    # Generate new access token
    result, message = AuthService.refresh_access_token()
    if result:
        return jsonify({
            "message": message,
            "access_token": result['access_token']
        }), 200
    return jsonify({"error": message}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by blacklisting current token"""
    jwt_data = get_jwt()
    user_id = get_jwt_identity()

    # Add token to blacklist
    success, message = AuthService.logout(
        token_jti=jwt_data['jti'],
        user_id=user_id,
        expires_at=jwt_data['exp']
    )

    if success:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    from ..models.user import User

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200
