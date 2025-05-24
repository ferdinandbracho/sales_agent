"""
Kavak AI Sales Agent - Main FastAPI Application
Agente comercial de IA para Kavak México
"""
import os

import uvicorn
from fastapi import FastAPI, status

# Import configuration and core components first
from src.core.exceptions import setup_exception_handlers
from src.core.middleware import setup_middleware

# Import routes and schemas
from src.webhook.twilio_handler import router as webhook_router
from src.schemas.responses import HealthCheckResponse, RootResponse, HealthStatus

# Initialize logging
from src.core.logging import setup_logging, get_logger

# Configure logging using settings from config
setup_logging()

# Get logger for this module
logger = get_logger(__name__)
logger.info("Starting application...")

# Create FastAPI app
app = FastAPI(
    title="Kavak AI Sales Agent",
    description="Agente comercial de IA para Kavak México 🚗",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "WhatsApp",
            "description": "Endpoints for WhatsApp integration",
        },
        {
            "name": "Health",
            "description": "Endpoints for monitoring and service status",
        },
    ],
)

# Setup middlewares and exception handlers
app = setup_middleware(app)
app = setup_exception_handlers(app)

# --- Routes ---
@app.get(
    "/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="Root endpoint",
    description="Provides basic information about the API",
    responses={
        200: {
            "description": "Basic information about the API",
            "content": {
                "application/json": {
                    "example": {
                        "message": "¡Hola! Soy el agente comercial de Kavak 🚗",
                        "description": "Agente de IA para ayudarte a encontrar tu auto perfecto",
                        "endpoints": {
                            "health": "/health",
                            "docs": "/docs",
                            "webhook": "/webhook/whatsapp",
                        }
                    }
                }
            }
        }
    },
    tags=["Root"]
)
async def root() -> RootResponse:
    """
    Root endpoint that provides basic information about the API.
    """
    return RootResponse(
        message="¡Hola! Soy el agente comercial de Kavak 🚗",
        description="Agente de IA para ayudarte a encontrar tu auto perfecto",
        endpoints={
            "health": "/health",
            "docs": "/docs",
            "webhook": "/webhook/whatsapp",
        },
    )

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check service status",
    description="Check service status",
    tags=["Health"],
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "service": "Kavak AI Agent",
                        "version": "0.1.0",
                        "language": "es_MX"
                    }
                }
            },
        }
    }
)
async def health_check() -> HealthCheckResponse:
    """
    Check service status.
    """
    return HealthCheckResponse(
        status=HealthStatus.OK,
        service="Kavak AI Agent",
        version="0.1.0",
        language="es_MX",
    )

# Include webhook routes
app.include_router(
    webhook_router,
    prefix="/webhook",
    tags=["WhatsApp"],
    responses={
        200: {"description": "Success"},
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"},
    },
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
        #proxy_headers=True, # Only for production
    )
