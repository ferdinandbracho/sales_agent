"""
Twilio WhatsApp Webhook Handler
Maneja mensajes de WhatsApp enviados por Twilio
"""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
from typing import Optional
import asyncio

from ..agent.kavak_agent import create_kavak_agent
from ..tools.car_search import buscar_autos_por_presupuesto, buscar_auto_especifico, obtener_autos_populares
from ..tools.financing import calcular_financiamiento, calcular_multiples_opciones, calcular_presupuesto_por_mensualidad
from ..tools.kavak_info import informacion_kavak, agendar_cita, comparar_con_competencia
from ..config import settings, SPANISH_ERROR_RESPONSES

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
        informacion_kavak,
        agendar_cita,
        comparar_con_competencia
    ]
    
    return create_kavak_agent(tools)

# Global agent instance
kavak_agent = get_kavak_agent()

# Simple in-memory conversation storage (for demo - use Redis in production)
conversation_memory = {}

@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),           # Message text
    From: str = Form(...),           # User's WhatsApp number  
    To: str = Form(...),             # Twilio number
    MessageSid: str = Form(...),     # Unique message ID
    NumMedia: str = Form(default="0") # Number of media files
):
    """
    Webhook endpoint for Twilio WhatsApp messages
    Receives messages and responds with TwiML
    """
    try:
        logger.info(f"📱 WhatsApp message received:")
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
            conversation_history=conversation_history
        )
        
        # Save conversation turn
        conversation_history.append({
            "user": Body,
            "agent": agent_response,
            "timestamp": MessageSid
        })
        
        # Keep only last 10 turns to manage memory
        conversation_memory[session_id] = conversation_history[-10:]
        
        # Create TwiML response
        twiml_response = MessagingResponse()
        twiml_response.message(agent_response)
        
        logger.info(f"📤 Sending response: {agent_response[:100]}...")
        
        return Response(
            content=str(twiml_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing WhatsApp message: {e}")
        
        # Send error response to user
        error_response = MessagingResponse()
        error_response.message(SPANISH_ERROR_RESPONSES["general_error"])
        
        return Response(
            content=str(error_response),
            media_type="application/xml"
        )

async def process_with_kavak_agent(
    message: str, 
    session_id: str, 
    conversation_history: list
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
    try:
        # Process with agent
        response = await kavak_agent.process_message(
            message=message,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Agent processing error: {e}")
        
        # Return contextual fallback based on message content
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hola", "hello", "hi", "buenas"]):
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
            return """
¡Perfecto! Te ayudo a encontrar tu auto ideal 🚗

¿Me puedes decir:
• ¿Cuál es tu presupuesto aproximado?
• ¿Tienes alguna marca de preferencia?
• ¿Para qué lo vas a usar principalmente?

¡Tengo excelentes opciones para ti! 😊
"""
        
        elif any(word in message_lower for word in ["precio", "financiamiento", "pago"]):
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
            return SPANISH_ERROR_RESPONSES["general_error"]

@router.get("/webhook-status")
async def webhook_status():
    """Check webhook status"""
    return {
        "status": "active",
        "service": "Kavak WhatsApp Webhook",
        "agent_tools": len(kavak_agent.tools),
        "conversation_sessions": len(conversation_memory)
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
            conversation_history=conversation_memory.get(session_id, [])
        )
        
        return {
            "user_message": message,
            "agent_response": response,
            "session_id": session_id
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
        sessions.append({
            "session_id": session_id,
            "message_count": len(history),
            "last_message": history[-1]["user"] if history else None
        })
    
    return {"active_sessions": len(sessions), "sessions": sessions}
