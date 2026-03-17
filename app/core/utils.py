import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Request

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    async def log_request(
        request: Request,
        user_id: Optional[int] = None,
        action: str = "",
        resource_type: str = "",
        resource_id: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log API request for audit purposes with a unique correlation ID

        Args:
            request: The FastAPI request object
            user_id: ID of the authenticated user (if available)
            action: Action being performed (e.g., "create", "update", "delete")
            resource_type: Type of resource being accessed (e.g., "appointment", "application")
            resource_id: ID of the resource being accessed (if applicable)
            status_code: HTTP status code of the response
            details: Additional details about the request/action

        Returns:
            correlation_id: A unique ID for correlating related audit logs
        """
        correlation_id = str(uuid.uuid4())

        # Extract request data
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Create audit log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "request": {
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
            "response": {
                "status_code": status_code,
            },
            "details": details or {},
        }

        # Log as JSON for easy parsing by log analytics tools
        logger.info(f"AUDIT: {json.dumps(log_entry)}")

        return correlation_id

    @staticmethod
    def log_security_event(
        event_type: str,
        user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Log security-related events

        Args:
            event_type: Type of security event (e.g., "login_attempt", "access_denied")
            user_id: ID of the user involved (if applicable)
            details: Additional details about the security event
            ip_address: IP address where the event originated
            correlation_id: Correlation ID to link related events
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "details": details or {},
        }

        logger.warning(f"SECURITY: {json.dumps(log_entry)}")
