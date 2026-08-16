import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("audit_logger")

class AuditLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        logger.info(f"AUDIT | Method: {method} | Path: {path} | Status: {response.status_code} | IP: {client_ip} | Duration: {process_time:.2f}ms")
        return response
