"""
Twilio WhatsApp Webhook Handler
"""

import time

from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from ..agent.kavak_agent import create_kavak_agent
from ..agent.redis_memory import redis_memory
from ..core.logging import get_logger
from ..tools.car_search import (
    get_popular_cars,
    search_cars_by_budget,
    search_specific_car,
)
from ..tools.financing import (
    calculate_financing,
    calculate_budget_by_monthly_payment,
    calculate_multiple_options,
)
from ..tools.kavak_info import get_kavak_info, schedule_appointment

# Configure logging
logger = get_logger(__name__)

# Create router
router = APIRouter()


# Initialize agent with tools
def get_kavak_agent():
    """Initialize Kavak agent with all tools"""
    tools = [
        # Car search tools
        search_cars_by_budget,
        search_specific_car,
        get_popular_cars,
        # Financing tools
        calculate_financing,
        calculate_multiple_options,
        calculate_budget_by_monthly_payment,
        # Kavak information tools
        get_kavak_info,
        schedule_appointment,
    ]

    return create_kavak_agent(tools)


# Global agent instance
kavak_agent = get_kavak_agent()


@router.post(
    "/whatsapp",
    status_code=status.HTTP_200_OK,
    summary="WhatsApp Webhook",
    description="""
    Webhook endpoint for receiving and responding to WhatsApp messages via Twilio.
    This endpoint processes incoming messages, generates responses using the Kavak AI agent,
    and returns TwiML for Twilio to send as WhatsApp messages.
    """,
    responses={
        200: {
            "description": "Successfully processed WhatsApp message",
            "content": {
                "application/xml": {
                    "example": """
                    <Response>
                        <Message>¡Hola! Gracias por tu mensaje. ¿En qué puedo ayudarte hoy? 🚗</Message>
                    </Response>
                    """
                }
            },
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing required form field: Body"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/xml": {
                    "example": """
                    <Response>
                        <Message>¡Ups! Algo salió mal. Por favor, inténtalo de nuevo en un momento. 🛠️</Message>
                    </Response>
                    """
                }
            },
        },
    },
    tags=["WhatsApp"],
    response_class=Response,
    response_description="TwiML response for Twilio",
)
async def whatsapp_webhook(
    Body: str = Form(..., description="The message text from the user"),
    From: str = Form(..., description="User's WhatsApp number with 'whatsapp:' prefix"),
    To: str = Form(..., description="Twilio number that received the message"),
    MessageSid: str = Form(..., description="Unique message identifier"),
    NumMedia: str = Form(
        default="0", description="Number of media files sent with the message"
    ),
) -> Response:
    """
    Process incoming WhatsApp messages and generate AI responses.

    This endpoint:
    - Validates incoming Twilio webhook request
    - Processes the message using the Kavak AI agent
    - Maintains conversation history by session
    - Handles message chunking for long responses
    - Returns properly formatted TwiML

    Args:
        Body: The message content from the user
        From: Sender's WhatsApp number (with 'whatsapp:' prefix)
        To: Recipient's Twilio number
        MessageSid: Unique message identifier
        NumMedia: Number of media files (images, documents, etc.)

    Returns:
        Response: TwiML response for Twilio to process
    """
    try:
        logger.info("WhatsApp message received")
        logger.info(f"From: {From}")
        logger.info(f"MessageSid: {MessageSid}")
        logger.debug(f"Message body: {Body}")

        # Clean phone number (remove whatsapp: prefix)
        user_phone = From.replace("whatsapp:", "")

        # Get conversation context
        session_id = f"whatsapp_{user_phone}"
        conversation_history = redis_memory.get_conversation(session_id)

        # Process message with Kavak agent
        agent_response = await process_with_kavak_agent(
            message=Body,
            session_id=session_id,
            conversation_history=conversation_history,
        )

        # Save conversation turn
        conversation_history.append(
            {"user": Body, "agent": agent_response, "timestamp": MessageSid}
        )
        redis_memory.save_conversation(session_id, conversation_history)

        # Create TwiML response
        twiml_response = MessagingResponse()

        # Split response if too long (WhatsApp limit is 4096 chars per message)
        max_length = 3000  # Conservative limit to account for TwiML overhead
        if len(agent_response) > max_length:
            chunks = [
                agent_response[i : i + max_length]
                for i in range(0, len(agent_response), max_length)
            ]
            for chunk in chunks:
                twiml_response.message(chunk)
                logger.info(f"Sending chunk: {chunk[:100]}...")
        else:
            twiml_response.message(agent_response)
            logger.info(f"Sending response: {agent_response[:100]}...")

        # Convert to string and log the raw TwiML for debugging
        twiml_str = str(twiml_response)
        logger.debug(f"Raw TwiML response: {twiml_str}")

        # Return response with proper headers
        return Response(
            content=twiml_str,
            media_type="application/xml",
            headers={"X-Twilio-Webhook": "true"},
        )

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions with their original status codes
        logger.error(f"HTTP error processing message: {http_exc.detail}")
        error_response = MessagingResponse()
        error_response.message(
            "¡Ups! No pude procesar tu solicitud. Por favor, inténtalo de nuevo más tarde. 🛠️"
        )
        return Response(
            content=str(error_response),
            media_type="application/xml",
            status_code=http_exc.status_code,
            headers={"X-Twilio-Webhook": "true"},
        )

    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}", exc_info=True)

        # Create a user-friendly error response
        error_response = MessagingResponse()
        error_message = (
            "¡Ups! Algo salió mal en nuestro sistema. "
            "Nuestro equipo ha sido notificado. Por favor, inténtalo de nuevo en un momento. 🛠️"
        )
        error_response.message(error_message)

        # Log the error with additional context
        logger.error(
            f"Error processing message from {From}. "
            f"MessageSid: {MessageSid}. Error: {str(e)}",
            exc_info=True,
        )

        return Response(
            content=str(error_response),
            media_type="application/xml",
            status_code=status.HTTP_200_OK,  # Must return 200 to Twilio
            headers={"X-Twilio-Webhook": "true"},
        )


async def process_with_kavak_agent(
    message: str, session_id: str, conversation_history: list
) -> str:
    """
    Process message with Kavak AI agent

    Args:
        message: User's message
        session_id: Session identifier
        conversation_history: Previous conversation turns

    Returns:
        Agent's response optimized for WhatsApp
    """
    logger.info(f"Processing message with agent: {message}")

    try:
        # Process with agent
        logger.info("Sending message to agent...")
        response = await kavak_agent.process_message(
            message=message,
            session_id=session_id,
            conversation_history=conversation_history,
        )

        logger.info(
            f"Agent response: {response[:200]}..."
            if len(str(response)) > 200
            else f"Agent response: {response}"
        )

        if not response or response.strip() == "":
            logger.warning("Agent returned empty response, using fallback")
            return "¡Hola! Soy tu agente comercial de Kavak 🚗"

        return response

    except Exception as e:
        logger.error(f"Agent processing error: {str(e)}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")

        # Log the full error for debugging
        import traceback

        logger.error(f"Stack trace: {traceback.format_exc()}")

        # Return contextual fallback based on message content
        message_lower = message.lower()

        if any(word in message_lower for word in ["hola", "hello", "hi", "buenas"]):
            logger.info("Using greeting fallback")
            return """
            ¡Hola! Soy tu agente comercial de Kavak 🚗

            Te puedo ayudar con:
            • Encontrar tu auto ideal
            • Calcular financiamiento 💰
            • Info sobre garantías ✅ 
            • Agendar cita de prueba 📅

            ¿Qué tipo de auto buscas?
            """

        elif any(
            word in message_lower for word in ["auto", "carro", "vehiculo", "coche"]
        ):
            logger.info("Using car search fallback")
            return """
            ¡Perfecto! Te ayudo a encontrar tu auto ideal 🚗

            ¿Me puedes decir:
            • ¿Cuál es tu presupuesto aproximado?
            • ¿Tienes alguna marca de preferencia?
            • ¿Para qué lo vas a usar principalmente?

            ¡Tengo excelentes opciones para ti! 😊
            """

        elif any(
            word in message_lower
            for word in ["precio", "financiamiento", "pago", "dinero", "pagar"]
        ):
            logger.info("Using financing fallback")
            return """
            💰 ¡Claro! Te ayudo con el financiamiento.

            En Kavak ofrecemos:
            • Financiamiento hasta 72 meses
            • Tasa desde 10% anual
            • Aprobación en 24 horas

            ¿Cuál es el precio del auto que te interesa? Te calculo las mensualidades 📊
            """

        else:
            logger.warning(f"Using general error fallback for message: {message}")
            return "¡Ups! Algo salió mal. Por favor, inténtalo de nuevo en un momento."


@router.get(
    "/webhook-status",
    status_code=status.HTTP_200_OK,
    summary="Check webhook status",
    description="Returns the current status and version information of the WhatsApp webhook service",
    responses={
        200: {
            "description": "Service status information",
            "content": {
                "application/json": {
                    "example": {
                        "status": "operational",
                        "service": "kavak-whatsapp-webhook",
                        "version": "1.0.0",
                        "timestamp": "2023-06-15T10:30:00Z",
                    }
                }
            },
        }
    },
    tags=["Health"],
)
async def webhook_status():
    """
    Check the status of the WhatsApp webhook service

    Returns basic information about the service including:
    - status: Current operational status
    - service: Service name
    - version: API version
    - timestamp: Current server time
    """
    from datetime import datetime, timezone

    return {
        "status": "operational",
        "service": "kavak-whatsapp-webhook",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post(
    "/test-agent",
    status_code=status.HTTP_200_OK,
    summary="Test the Kavak AI Agent",
    description="""
    Test endpoint to interact with the Kavak AI agent directly.
    This endpoint processes a message and returns the agent's response.
    Maintains conversation context using the provided session_id.
    """,
    responses={
        200: {
            "description": "Successful response from the agent",
            "content": {
                "application/json": {
                    "example": {
                        "user_message": "¿Qué autos tienen disponibles?",
                        "agent_response": "¡Hola! Tenemos varias opciones disponibles. ¿Qué tipo de auto estás buscando? 🚗",
                        "session_id": "test_user_123",
                    }
                }
            },
        },
        400: {
            "description": "Invalid request",
            "content": {
                "application/json": {"example": {"detail": "Message is required"}}
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error processing your request"}
                }
            },
        },
    },
    tags=["Testing"],
)
async def test_agent_locally(message: str, session_id: str = "test_session"):
    """
    Test endpoint for local agent testing

    - **message**: The message to send to the agent (required)
    - **session_id**: Optional session ID for conversation tracking (default: "test_session")
    """
    try:
        start_time = time.time()
        response = await process_with_kavak_agent(
            message=message,
            session_id=session_id,
            conversation_history=redis_memory.get_conversation(session_id),
        )

        return {
            "user_message": message,
            "agent_response": response,
            "session_id": session_id,
            "processing_time": time.time() - start_time,
        }

    except Exception as e:
        logger.error(f"Error in test_agent_locally: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your request",
        )


# Conversation memory management
@router.delete(
    "/conversations/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Clear conversation history",
    description="Clears the conversation history for a specific session ID",
    responses={
        200: {
            "description": "Successfully cleared conversation",
            "content": {
                "application/json": {
                    "example": {"message": "Conversation session_123 cleared"}
                }
            },
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {"message": "Conversation session_123 not found"}
                }
            },
        },
    },
    tags=["Conversations"],
)
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a specific session

    - **session_id**: The ID of the session to clear (required)
    """
    # Delete conversation from Redis
    success = redis_memory.delete_conversation(session_id)

    if success:
        return {"message": f"Conversation {session_id} cleared"}
    else:
        raise HTTPException(
            status_code=404, detail=f"Conversation {session_id} not found"
        )


@router.get(
    "/conversations",
    status_code=status.HTTP_200_OK,
    summary="List active conversations",
    description="Returns a list of all active conversation sessions with their metadata",
    responses={
        200: {
            "description": "List of active conversations",
            "content": {
                "application/json": {
                    "example": {
                        "sessions": [
                            {
                                "session_id": "session_123",
                                "message_count": 5,
                                "last_message": "¿Qué autos tienen disponibles?",
                                "created_at": "2023-06-15T10:30:00Z",
                            }
                        ]
                    }
                }
            },
        }
    },
    tags=["Conversations"],
)
async def list_conversations():
    """
    List all active conversation sessions

    Returns a list of all active conversations with their metadata including:
    - session_id: Unique identifier for the conversation
    - message_count: Number of messages in the conversation
    - last_message: Content of the last message in the conversation
    """
    active_sessions = redis_memory.list_active_sessions()
    sessions = [
        {
            "session_id": session_id,
            "message_count": metadata["message_count"],
            "last_message": metadata["last_message"],
            "ttl_seconds": metadata["ttl_seconds"],
            "last_activity": metadata["last_activity"],
        }
        for session_id, metadata in active_sessions.items()
    ]
    return {"sessions": sessions}
