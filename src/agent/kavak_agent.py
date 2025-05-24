"""
Kavak AI Sales Agent - Core Agent Implementation
Agente comercial principal de Kavak México
"""

import logging
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from ..config import MEXICAN_CONFIG, SPANISH_ERROR_RESPONSES, settings
from .prompts import KAVAK_SYSTEM_PROMPT, MEXICAN_SALES_PERSONA

logger = logging.getLogger(__name__)


class KavakSalesAgent:
    """
    Agente comercial de IA para Kavak México
    Maneja conversaciones en español y utiliza herramientas específicas
    """

    def __init__(self, tools: List[Any]):
        """
        Inicializa el agente con herramientas específicas de Kavak

        Args:
            tools: Lista de herramientas disponibles para el agente
        """
        self.tools = tools
        self.llm = self._setup_llm()
        self.agent_executor = self._create_agent()

    def _setup_llm(self) -> ChatOpenAI:
        """Configura el modelo de lenguaje"""
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,  # Slightly creative for sales conversations
            openai_api_key=settings.openai_api_key,
            max_tokens=1000,  # Limit for WhatsApp optimization
        )

    def _create_agent(self) -> AgentExecutor:
        """Crea el ejecutor del agente con herramientas"""

        # Create prompt template with Mexican Spanish persona
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", KAVAK_SYSTEM_PROMPT),
                ("system", MEXICAN_SALES_PERSONA),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agent with tools
        agent = create_openai_tools_agent(llm=self.llm, tools=self.tools, prompt=prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            handle_parsing_errors=True,
        )

    async def process_message(
        self,
        message: str,
        session_id: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Procesa un mensaje del usuario y genera respuesta

        Args:
            message: Mensaje del usuario
            session_id: ID de la sesión de conversación
            conversation_history: Historial de conversación

        Returns:
            Respuesta del agente optimizada para WhatsApp
        """
        try:
            # Build conversation history
            chat_history = self._build_chat_history(conversation_history)

            # Process with agent
            response = await self.agent_executor.ainvoke(
                {"input": message, "chat_history": chat_history}
            )

            # Extract and optimize response
            agent_response = response.get("output", "")
            optimized_response = self._optimize_for_whatsapp(agent_response)

            return optimized_response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._get_fallback_response(message)

    def _build_chat_history(
        self, conversation_history: Optional[List[Dict]]
    ) -> List[BaseMessage]:
        """Convierte historial a formato de LangChain"""
        if not conversation_history:
            return []

        messages = []
        # Only use last 5 turns to manage context
        for turn in conversation_history[-5:]:
            if "user" in turn and "agent" in turn:
                messages.append(HumanMessage(content=turn["user"]))
                messages.append(AIMessage(content=turn["agent"]))

        return messages

    def _optimize_for_whatsapp(self, response: str) -> str:
        """
        Optimiza la respuesta para WhatsApp
        - Límite de caracteres
        - Emojis mexicanos
        - Formato móvil
        """
        # Truncate if too long
        if len(response) > settings.response_max_length:
            response = (
                response[: settings.response_max_length - 50]
                + "...\n\n¿Te interesa saber más detalles? 😊"
            )

        # Add contextual emojis if not present
        if not any(emoji in response for emoji in MEXICAN_CONFIG["emojis"].values()):
            response = self._add_contextual_emoji(response)

        return response

    def _add_contextual_emoji(self, response: str) -> str:
        """Agrega emojis contextuales mexicanos"""
        emojis = MEXICAN_CONFIG["emojis"]

        if any(word in response.lower() for word in ["auto", "carro", "vehículo"]):
            return f"{emojis['car']} {response}"
        elif any(
            word in response.lower() for word in ["precio", "pago", "financiamiento"]
        ):
            return f"{emojis['money']} {response}"
        elif any(word in response.lower() for word in ["buscar", "encontrar"]):
            return f"{emojis['search']} {response}"
        else:
            return f"{emojis['happy']} {response}"

    def _get_fallback_response(self, original_message: str) -> str:
        """
        Respuesta de emergencia cuando el agente falla
        Siempre en español mexicano
        """
        fallback_responses = [
            f"¡Hola! Soy tu agente de Kavak {MEXICAN_CONFIG['emojis']['car']}\n\nTe puedo ayudar con:\n• Encontrar tu auto ideal\n• Calcular financiamiento {MEXICAN_CONFIG['emojis']['money']}\n• Info sobre garantías\n• Agendar cita de prueba\n\n¿Qué necesitas?",
            f"Disculpa, tuve un problemita técnico {MEXICAN_CONFIG['emojis']['thinking']}\n\n¿Me puedes decir qué tipo de auto buscas? Te ayudo a encontrar las mejores opciones en Kavak.",
            f"¡Perfecto! Estoy aquí para ayudarte a encontrar tu auto ideal {MEXICAN_CONFIG['emojis']['car']}\n\n¿Cuál es tu presupuesto aproximado?",
        ]

        # Simple context-based selection
        if any(word in original_message.lower() for word in ["hola", "hello", "hi"]):
            return fallback_responses[0]
        elif any(word in original_message.lower() for word in ["error", "problema"]):
            return fallback_responses[1]
        else:
            return fallback_responses[2]


def create_kavak_agent(tools: List[Any]) -> KavakSalesAgent:
    """Factory function para crear el agente de Kavak"""
    return KavakSalesAgent(tools)
