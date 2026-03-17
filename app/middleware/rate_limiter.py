from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[os.environ.get("RATE_LIMIT_DEFAULT", "100 per day")],
    storage_uri="memory://",
)

# Configure specific limits for sensitive routes
auth_limit = os.environ.get("RATE_LIMIT_AUTH", "10 per minute")

def configure_rate_limits(app):
    """Configure rate limiting for the application"""
    limiter.init_app(app)

    # Define custom rate limits per route pattern
    limiter.limit(auth_limit)(app.route('/api/auth/login'))
    limiter.limit(auth_limit)(app.route('/api/auth/register'))
    limiter.limit("5/minute")(app.route('/api/auth/reset-password'))

    return limiter
