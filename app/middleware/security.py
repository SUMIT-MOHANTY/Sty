from flask import Flask, request, Response
import os

def configure_security(app):
    """Configure security headers and options for Flask app"""
    if not isinstance(app, Flask):
        raise TypeError("Expected Flask instance")

    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Prevent clickjacking attacks
        response.headers['X-Frame-Options'] = 'DENY'

        # Block MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy
        if os.environ.get('ENABLE_CSP', 'true').lower() == 'true':
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none';"
            )

        # HTTP Strict Transport Security (HSTS)
        if os.environ.get('ENABLE_HSTS', 'true').lower() == 'true':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Remove server header if present
        response.headers.pop('Server', None)

        return response

    # Check for HTTPS
    @app.before_request
    def enforce_https():
        """Redirect HTTP to HTTPS in production"""
        if app.env == 'production' and not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return Response(f'<html><head><meta http-equiv="refresh" content="0;url={url}"></head></html>', 301)

    return app
