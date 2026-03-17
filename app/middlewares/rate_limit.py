import time
from typing import Dict, Tuple, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class RateLimitExceeded(Exception):
    pass

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        requests_limit: int = 100,
        time_window: int = 60,
        custom_key_func: Callable = None
    ):
        """
        Rate limiting middleware:

        - requests_limit: Maximum number of requests allowed in time window
        - time_window: Time window in seconds
        - custom_key_func: Function to extract custom key from request (defaults to IP address)
        """
        super().__init__(app)
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.custom_key_func = custom_key_func or (lambda r: r.client.host)
        self.requests: Dict[str, Tuple[int, float]] = {}  # key -> (count, window_start)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for static files
        if request.url.path.startswith("/static"):
            return await call_next(request)

        key = self.custom_key_func(request)
        current_time = time.time()

        # Initialize or reset counter if time window has elapsed
        if key not in self.requests or (current_time - self.requests[key][1]) > self.time_window:
            self.requests[key] = (1, current_time)
        else:
            count, window_start = self.requests[key]
            # Check if limit exceeded
            if count >= self.requests_limit:
                headers = {
                    "Retry-After": str(int(window_start + self.time_window - current_time))
                }
                return Response(
                    content="Rate limit exceeded. Please try again later.",
                    status_code=429,
                    headers=headers
                )
            # Increment request count
            self.requests[key] = (count + 1, window_start)

        # Process the request
        return await call_next(request)
