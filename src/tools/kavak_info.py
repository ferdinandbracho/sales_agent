"""
Kavak Information Tool

This module provides tools to retrieve and format information about Kavak's services,
warranties, and value proposition in Mexican Spanish.
"""

from langchain.tools import tool
from ..config import settings
from ..knowledge.kavak_knowledge import get_kavak_knowledge_base
import logging

logger = logging.getLogger(__name__)


@tool
def get_kavak_info(query: str) -> str:
    """
    Gets general information about Kavak and its services.

    Args:
        query: User's query about Kavak, its services, processes, etc.

    Returns:
        Response in Mexican Spanish with the requested information about Kavak,
        formatted for WhatsApp.
    """
    try:
        kb = get_kavak_knowledge_base()
        if not kb or not kb.is_ready:
            logger.warning(
                f"KavakKnowledgeBase not ready or not available in get_kavak_info. Status: {kb.initialization_error if kb else 'KB is None'}"
            )
            # Return an empty string to signal that no specific info was found by RAG.
            return ""

        # Obtain information from the knowledge base using search_knowledge
        search_results = kb.search_knowledge(
            query=query, top_k=1
        )  # Fetch top 1 for now, can be adjusted

        if not search_results:
            # Return an empty string to signal that no specific info was found by RAG.
            # The agent will then attempt to answer using its general system prompt knowledge.
            logger.info(
                f"No specific RAG results for query: '{query}'. Returning empty string to agent."
            )
            return ""

        # Combine content from results into a single string
        # If search_knowledge structures results differently, this needs adjustment.
        combined_content = "\n\n".join(
            [res.get("content", "") for res in search_results if res.get("content")]
        )

        if not combined_content.strip():
            return "🤔 Encontré información relacionada, pero no un texto claro para mostrar. ¿Puedes intentar otra pregunta?"

        # Ensure the response does not exceed the character limit
        max_length = (
            getattr(settings, "RESPONSE_MAX_LENGTH", 1500) - 100
        )  # Leave space for the closing
        if len(combined_content) > max_length:
            # Find the last period before the limit for a clean cut
            cutoff = combined_content.rfind(".", 0, max_length)
            if cutoff == -1:  # If no periods, cut at the limit
                cutoff = max_length
            results_string = (
                combined_content[:cutoff]
                + ".\n\n¿Te gustaría que profundice en algún aspecto en particular? 😊"
            )
        else:
            results_string = combined_content

        return results_string

    except Exception as e:
        logger.error(f"Error en get_kavak_info: {str(e)}")
        return "⚠️ ¡Ups! Hubo un problema al buscar la información. Por favor, inténtalo de nuevo en un momento. Si el problema persiste, no dudes en contactar a nuestro equipo de soporte."


@tool
def schedule_appointment() -> str:
    """
    Provides information on how to schedule an appointment to view a car.

    Returns:
        Instructions for scheduling an appointment in Mexican Spanish, formatted for WhatsApp.
    """
    return """📅 **¡Agenda tu Cita en Kavak!** 🚗

    ¡Perfecto! Uno de nuestros asesores se pondrá en contacto contigo a la brevedad para ayudarte a agendar tu cita.

    📋 **Por favor ten a la mano:**
    • Identificación oficial (INE/IFE)
    • Comprobante de domicilio
    • Comprobantes de ingresos (si aplica para financiamiento)
    • Documentos de tu auto actual (si planeas dejarlo a cuenta)
    """
