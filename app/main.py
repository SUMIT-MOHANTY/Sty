from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.middlewares.rate_limit import RateLimitMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_limit=settings.RATE_LIMIT_REQUESTS,
    time_window=settings.RATE_LIMIT_PERIOD
)

# Add security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add security headers
        for header, value in settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
