from fastapi import HTTPException, status
import time
import asyncio
from typing import Dict, Tuple
import logging

# Store for rate limiting: {ip: {endpoint: (count, start_time)}}
rate_limit_store: Dict[str, Dict[str, Tuple[int, float]]] = {}
rate_limit_lock = asyncio.Lock()

logger = logging.getLogger("middleware.rate_limit")

async def rate_limiter(client_ip: str, endpoint: str, max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiting middleware to prevent abuse of API endpoints.

    Args:
        client_ip: IP address of the client
        endpoint: Name of the endpoint being accessed
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds

    Raises:
        HTTPException: If rate limit is exceeded
    """
    async with rate_limit_lock:
        current_time = time.time()

        # Initialize if IP not seen before
        if client_ip not in rate_limit_store:
            rate_limit_store[client_ip] = {}

        # Initialize if endpoint not seen before for this IP
        if endpoint not in rate_limit_store[client_ip]:
            rate_limit_store[client_ip][endpoint] = (1, current_time)
            return

        count, start_time = rate_limit_store[client_ip][endpoint]

        # Reset counter if window has passed
        if current_time - start_time > window_seconds:
            rate_limit_store[client_ip][endpoint] = (1, current_time)
            return

        # Increment counter if within window
        count += 1

        # Check if limit exceeded
        if count > max_requests:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on endpoint {endpoint}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {int(window_seconds - (current_time - start_time))} seconds."
            )

        # Update counter
        rate_limit_store[client_ip][endpoint] = (count, start_time)

        # Cleanup old entries
        for ip in list(rate_limit_store.keys()):
            for ep in list(rate_limit_store[ip].keys()):
                if current_time - rate_limit_store[ip][ep][1] > window_seconds:
                    del rate_limit_store[ip][ep]
            if not rate_limit_store[ip]:
                del rate_limit_store[ip]
