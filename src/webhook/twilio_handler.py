"""
Twilio WhatsApp Webhook Handler
"""

import logging

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from src.agent.kavak_agent import create_kavak_agent
from src.config import SPANISH_ERROR_RESPONSES
from src.tools.car_search import (
    buscar_auto_especifico,
    buscar_autos_por_presupuesto,
    obtener_autos_populares,
)
from src.tools.financing import (
    calcular_financiamiento,
    calcular_multiples_opciones,
    calcular_presupuesto_por_mensualidad,
)
from src.tools.kavak_info import (
    schedule_appointment,
    get_kavak_info,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Initialize agent with tools
def get_kavak_agent():
    """Initialize Kavak agent with all tools"""
    tools = [
        # Car search tools
        buscar_autos_por_presupuesto,
        buscar_auto_especifico,
        obtener_autos_populares,
        # Financing tools
        calcular_financiamiento,
        calcular_multiples_opciones,
        calcular_presupuesto_por_mensualidad,
        # Kavak information tools
        get_kavak_info,
        schedule_appointment,
    ]

    return create_kavak_agent(tools)


# Global agent instance
kavak_agent = get_kavak_agent()

# Simple in-memory conversation storage (for demo - use Redis in production)
conversation_memory = {}


@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),  # Message text
    From: str = Form(...),  # User's WhatsApp number
    To: str = Form(...),  # Twilio number
    MessageSid: str = Form(...),  # Unique message ID
    NumMedia: str = Form(default="0"),  # Number of media files
):
    """
    Webhook endpoint for Twilio WhatsApp messages
    Receives messages and responds with TwiML
    """
    try:
        logger.info("📱 WhatsApp message received")
        logger.info(f"   From: {From}")
        logger.info(f"   Body: {Body}")
        logger.info(f"   MessageSid: {MessageSid}")

        # Clean phone number (remove whatsapp: prefix)
        user_phone = From.replace("whatsapp:", "")

        # Get conversation context
        session_id = f"whatsapp_{user_phone}"
        conversation_history = conversation_memory.get(session_id, [])

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
        conversation_memory[session_id] = conversation_history[-10:]

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
                logger.info(f"📤 Sending chunk: {chunk[:100]}...")
        else:
            twiml_response.message(agent_response)
            logger.info(f"📤 Sending response: {agent_response[:100]}...")

        # Convert to string and log the raw TwiML for debugging
        twiml_str = str(twiml_response)
        logger.debug(f"📝 Raw TwiML response: {twiml_str}")

        # Return response with proper headers
        return Response(
            content=twiml_str,
            media_type="application/xml",
            headers={"X-Twilio-Webhook": "true"},
        )

    except Exception as e:
        logger.error(f"❌ Error processing WhatsApp message: {str(e)}", exc_info=True)

        # Create a simple error response
        error_response = MessagingResponse()
        error_message = (
            "¡Ups! Algo salió mal. Por favor, inténtalo de nuevo en un momento. 🛠️"
        )
        error_response.message(error_message)

        logger.error(f"⚠️ Sending error response: {error_message}")

        return Response(
            content=str(error_response),
            media_type="application/xml",
            status_code=200,
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
    logger.info(f"🔍 Processing message with agent: {message}")

    try:
        # Process with agent
        logger.info("🤖 Sending message to agent...")
        response = await kavak_agent.process_message(
            message=message,
            session_id=session_id,
            conversation_history=conversation_history,
        )

        logger.info(
            f"✅ Agent response: {response[:200]}..."
            if len(str(response)) > 200
            else f"✅ Agent response: {response}"
        )

        if not response or response.strip() == "":
            logger.warning("⚠️ Agent returned empty response, using fallback")
            return SPANISH_ERROR_RESPONSES["empty_response"]

        return response

    except Exception as e:
        logger.error(f"❌ Agent processing error: {str(e)}", exc_info=True)
        logger.error(f"🔧 Error type: {type(e).__name__}")

        # Log the full error for debugging
        import traceback

        logger.error(f"📜 Stack trace: {traceback.format_exc()}")

        # Return contextual fallback based on message content
        message_lower = message.lower()

        if any(word in message_lower for word in ["hola", "hello", "hi", "buenas"]):
            logger.info("👋 Using greeting fallback")
            return """
            ¡Hola! Soy tu agente comercial de Kavak 🚗

            Te puedo ayudar con:
            • Encontrar tu auto ideal
            • Calcular financiamiento 💰
            • Info sobre garantías ✅  
            • Agendar cita de prueba 📅

            ¿Qué tipo de auto buscas?
            """

        elif any(word in message_lower for word in ["auto", "carro", "vehiculo"]):
            logger.info("🚗 Using car search fallback")
            return """
            ¡Perfecto! Te ayudo a encontrar tu auto ideal 🚗

            ¿Me puedes decir:
            • ¿Cuál es tu presupuesto aproximado?
            • ¿Tienes alguna marca de preferencia?
            • ¿Para qué lo vas a usar principalmente?

            ¡Tengo excelentes opciones para ti! 😊
            """

        elif any(
            word in message_lower for word in ["precio", "financiamiento", "pago"]
        ):
            logger.info("💰 Using financing fallback")
            return """
            💰 ¡Claro! Te ayudo con el financiamiento.

            En Kavak ofrecemos:
            • Financiamiento hasta 84 meses
            • Tasa desde 10% anual
            • Aprobación en 24 horas
            • Sin aval ni garantías adicionales

            ¿Cuál es el precio del auto que te interesa? Te calculo las mensualidades 📊
            """

        else:
            logger.warning(f"⚠️ Using general error fallback for message: {message}")
            return SPANISH_ERROR_RESPONSES["general_error"]


@router.get("/webhook-status")
async def webhook_status():
    """Check webhook status"""
    return {
        "status": "active",
        "service": "Kavak WhatsApp Webhook",
        "agent_tools": len(kavak_agent.tools),
        "conversation_sessions": len(conversation_memory),
    }


@router.post("/test-agent")
async def test_agent_locally(request: dict):
    """
    Test endpoint for local agent testing
    """
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", "test_session")

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        response = await process_with_kavak_agent(
            message=message,
            session_id=session_id,
            conversation_history=conversation_memory.get(session_id, []),
        )

        return {
            "user_message": message,
            "agent_response": response,
            "session_id": session_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Conversation memory management
@router.delete("/conversations/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_memory:
        del conversation_memory[session_id]
        return {"message": f"Conversation {session_id} cleared"}
    else:
        return {"message": f"Conversation {session_id} not found"}


@router.get("/conversations")
async def list_conversations():
    """List active conversation sessions"""
    sessions = []
    for session_id, history in conversation_memory.items():
        sessions.append(
            {
                "session_id": session_id,
                "message_count": len(history),
                "last_message": history[-1]["user"] if history else None,
            }
        )

    return {"active_sessions": len(sessions), "sessions": sessions}
