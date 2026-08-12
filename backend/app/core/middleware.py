import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        response = await call_next(request)

        process_time = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(process_time)

        print(f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({process_time}ms)")

        return response