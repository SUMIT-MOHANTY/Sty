import secrets
import time
from typing import Dict, Optional

# Store CSRF tokens with expiration time
# In production, this should use Redis or another persistent store
_csrf_tokens: Dict[str, float] = {}
CSRF_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour

def generate_csrf_token() -> str:
    """Generate a secure random token for CSRF protection"""
    return secrets.token_urlsafe(32)

def store_csrf_token(token: str) -> None:
    """Store a CSRF token with expiration time"""
    current_time = time.time()

    # Clean up expired tokens
    expired_tokens = [t for t, expires in _csrf_tokens.items() if current_time > expires]
    for t in expired_tokens:
        _csrf_tokens.pop(t, None)

    # Store new token
    _csrf_tokens[token] = current_time + CSRF_TOKEN_EXPIRE_SECONDS

def validate_csrf_token(token: str) -> bool:
    """Validate that a CSRF token exists and has not expired"""
    if not token:
        return False

    current_time = time.time()
    expiry_time = _csrf_tokens.get(token)

    if not expiry_time or current_time > expiry_time:
        return False

    # Token used - remove it (one-time use)
    _csrf_tokens.pop(token, None)
    return True
