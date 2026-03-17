from flask import request, jsonify
from functools import wraps
import jwt
from config import Config
from backend.models.user import User

def admin_required(f):
    """Decorator to check if the user is an admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token is missing or invalid'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Decode token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])

            # Check if user exists and is admin
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403

        except Exception as e:
            return jsonify({'error': str(e)}), 401

        return f(*args, **kwargs)

    return decorated
