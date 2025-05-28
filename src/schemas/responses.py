"""
Response schemas for the API
"""

from enum import Enum
from typing import Dict, Optional

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


class TestAgentRequest(BaseModel):
    """Test agent request schema"""

    message: str = Field(
        ...,
        description="User message to process",
        example="¿Qué autos tienen disponibles?",
    )
    session_id: str = Field(
        "test_session",
        description="Unique session ID for conversation tracking",
        example="user_12345",
    )


class TestAgentResponse(BaseModel):
    """Test agent response schema"""

    user_message: str = Field(..., description="Original user message")
    agent_response: str = Field(..., description="Agent's response")
    session_id: str = Field(..., description="Session ID used for the conversation")


class ErrorResponse(BaseModel):
    """Generic error response schema"""

    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")
    status_code: int = Field(..., description="HTTP status code")


class WhatsAppWebhookRequest(BaseModel):
    """Schema for incoming WhatsApp webhook requests"""

    Body: str = Field(..., description="The message text from the user")
    From: str = Field(..., description="User's WhatsApp number with 'whatsapp:' prefix")
    To: str = Field(..., description="Twilio number that received the message")
    MessageSid: str = Field(..., description="Unique message identifier")
    NumMedia: str = Field(
        default="0", description="Number of media files sent with the message"
    )


class WhatsAppMessageResponse(BaseModel):
    """Schema for WhatsApp message responses"""

    to: str = Field(..., description="Recipient's WhatsApp number")
    from_: str = Field(..., alias="from", description="Sender's Twilio number")
    body: str = Field(..., description="The message content")
    message_sid: str = Field(..., description="Unique message identifier")
    status: str = Field(..., description="Message status")


class WhatsAppWebhookResponse(BaseModel):
    """Schema for WhatsApp webhook responses"""

    success: bool = Field(
        ..., description="Whether the message was processed successfully"
    )
    message: str = Field(..., description="Status message")
    message_sid: str = Field(..., description="Unique message identifier")
    recipient: str = Field(..., description="Recipient's WhatsApp number")
