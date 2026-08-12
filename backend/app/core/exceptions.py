"""
Custom Application Exceptions & Global Error Handlers
"""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger


class BaseAppException(Exception):
    """Base class for custom application exceptions."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationException(BaseAppException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedException(BaseAppException):
    """Raised when a user lacks required permissions."""
    def __init__(self, message: str = "Permission denied for this resource"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(BaseAppException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers for standardized API error responses.
    """
    @app.exception_handler(BaseAppException)
    async def custom_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        logger.error(f"Application Exception: {exc.message} on path {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "details": {}
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Request Validation Failure on path {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "message": "Input validation error",
                    "details": exc.errors()
                }
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled Internal System Error: {str(exc)} on path {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "An unexpected internal server error occurred.",
                    "details": {}
                }
            }
        )
