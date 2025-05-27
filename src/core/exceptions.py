"""
Custom exception handlers for the API.
"""

from typing import Any, Dict
from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.logging import get_logger

# Get logger instance
logger = get_logger(__name__)


def get_client_info(request: Request) -> Dict[str, Any]:
    """Extract client information from request."""
    client = request.client
    return {
        "client_host": client.host if client else None,
        "client_port": client.port if client else None,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
    }


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions with detailed logging.

    Args:
        request: The request that caused the exception.
        exc: The exception that was raised.

    Returns:
        JSONResponse: A JSON response with error details.
    """
    # Generate unique error ID
    error_id = str(uuid4())[:8]

    # Prepare error context
    error_context = {
        "error_id": error_id,
        "path": request.url.path,
        "method": request.method,
        "query_params": dict(request.query_params),
        **get_client_info(request),
    }

    # Log the error with context
    logger.error(
        f"Unhandled exception: {str(exc) or type(exc).__name__} - Context: {error_context}",
        exc_info=True
    )

    # Return generic error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Ha ocurrido un error interno",
            "error_id": error_id,
            "documentation_url": "https://docs.kavak.ai/errors",
        },
    )


def setup_exception_handlers(app):
    """
    Add exception handlers to the FastAPI app.

    Args:
        app: The FastAPI application instance.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    app.add_exception_handler(Exception, generic_exception_handler)

    # We can add more specific exception handlers here
    # Example:
    # @app.exception_handler(ValueError)
    # async def value_error_handler(request: Request, exc: ValueError):
    #     logger.warning(f"Value error: {str(exc)}")
    #     return JSONResponse(
    #         status_code=400,
    #         content={"detail": str(exc)},
    #     )

    return app
