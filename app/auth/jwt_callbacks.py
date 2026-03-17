from flask import jsonify
from flask_jwt_extended import JWTManager
from ..models.token_blacklist import TokenBlacklist, cleanup_expired_tokens
from ..models.user import User

def register_jwt_callbacks(jwt):
    """Register JWT callbacks for token validation"""
    if not isinstance(jwt, JWTManager):
        raise TypeError("Expected JWTManager instance")

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token is in blacklist"""
        jti = jwt_payload['jti']
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_header, jwt_data):
        """Look up user from token identity"""
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token has expired",
            "code": "token_expired"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "Invalid token",
            "code": "invalid_token"
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "Authentication required",
            "code": "authorization_required"
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token has been revoked",
            "code": "token_revoked"
        }), 401

    # Run token cleanup task
    cleanup_expired_tokens()

    return jwt
