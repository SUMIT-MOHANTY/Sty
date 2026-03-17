from flask import Flask
from flask_jwt_extended import JWTManager

from .routes import auth_bp
from .password_reset import password_bp
from .jwt_callbacks import register_jwt_callbacks
from ..config.jwt_config import JWTConfig

def init_auth(app):
    """Initialize authentication system for Flask application"""
    if not isinstance(app, Flask):
        raise TypeError("Expected Flask instance")

    # Configure JWT
    app.config.update(
        JWT_SECRET_KEY=JWTConfig.JWT_SECRET_KEY,
        JWT_ACCESS_TOKEN_EXPIRES=JWTConfig.JWT_ACCESS_TOKEN_EXPIRES,
        JWT_REFRESH_TOKEN_EXPIRES=JWTConfig.JWT_REFRESH_TOKEN_EXPIRES,
        JWT_BLACKLIST_ENABLED=JWTConfig.JWT_BLACKLIST_ENABLED,
        JWT_BLACKLIST_TOKEN_CHECKS=JWTConfig.JWT_BLACKLIST_TOKEN_CHECKS
    )

    # Initialize JWT
    jwt = JWTManager(app)
    register_jwt_callbacks(jwt)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(password_bp)

    return app
