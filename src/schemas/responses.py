"""
Response schemas for the API
"""

from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status values"""

    OK = "OK"
    ERROR = "ERROR"


class HealthCheckResponse(BaseModel):
    """Health check response schema"""

    status: HealthStatus = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    language: str = Field(..., description="Primary language")


class RootResponse(BaseModel):
    """Root endpoint response schema"""

    message: str = Field(..., description="Welcome message")
    description: str = Field(..., description="Service description")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints")
