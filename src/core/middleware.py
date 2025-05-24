"""
Application middlewares for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


def setup_middleware(app: FastAPI) -> FastAPI:
    """
    Configure and add all middlewares to the FastAPI application.

    Args:
        app: FastAPI application instance

    Returns:
        FastAPI: Configured FastAPI application
    """
    # CORS Middleware (in production, replace with actual config)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Host Middleware (in production, replace with actual config)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )

    return app


# Alias for backward compatibility
setup_middlewares = setup_middleware
