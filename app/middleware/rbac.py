from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(allowed_roles):
    """
    Decorator to restrict access based on user roles

    Args:
        allowed_roles: List of role names or single role string
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if isinstance(allowed_roles, str):
                roles = [allowed_roles]
            else:
                roles = allowed_roles

            if claims.get('role') not in roles:
                return jsonify({"error": "Access denied: insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Convenient role decorators
def admin_required(fn):
    """Decorator for admin-only routes"""
    return role_required("admin")(fn)

def user_required(fn):
    """Decorator for authenticated user routes"""
    return role_required(["user", "admin"])(fn)
