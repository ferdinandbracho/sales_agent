"""
Kavak AI Sales Agent - Core Agent Implementation
"""

from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from ..config import MEXICAN_CONFIG, SPANISH_ERROR_RESPONSES, settings
from .prompts import KAVAK_SYSTEM_PROMPT, MEXICAN_SALES_PERSONA
from ..core.logging import get_logger

logger = get_logger(__name__)


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
            model=settings.openai.OPENAI_MODEL,
            temperature=0.7,  # Slightly creative for sales conversations
            openai_api_key=settings.openai.OPENAI_API_KEY,
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
        logger.info(f"🔍 Procesando mensaje: {message}")

        try:
            # Build conversation history
            logger.info("📚 Construyendo historial de conversación...")
            chat_history_for_agent = self._build_chat_history(conversation_history)
            logger.debug(
                f"📜 Historial de conversación para agente: {chat_history_for_agent}"
            )

            # Process with agent
            logger.info("🤖 Invocando al agente principal...")
            agent_executor_response = await self.agent_executor.ainvoke(
                {"input": message, "chat_history": chat_history_for_agent}
            )
            logger.debug(f"📦 Respuesta cruda del agente: {agent_executor_response}")

            agent_final_output = agent_executor_response.get("output", "")

            # Check if RAG tool (get_kavak_info) was called and returned empty,
            # and if the agent's final output is also empty.
            rag_tool_returned_empty = False
            if agent_executor_response.get("intermediate_steps"):
                for action, observation in agent_executor_response[
                    "intermediate_steps"
                ]:
                    if (
                        hasattr(action, "tool")
                        and action.tool == "get_kavak_info"
                        and observation == ""
                    ):
                        logger.info(
                            "🛠️ Herramienta 'get_kavak_info' fue llamada y no devolvió resultados específicos (RAG). "
                        )
                        rag_tool_returned_empty = True
                        break

            if rag_tool_returned_empty and (
                not agent_final_output or not agent_final_output.strip()
            ):
                logger.warning(
                    "RAG no encontró información específica y el agente generó una respuesta vacía. "
                    "Intentando respuesta directa con LLM y prompt de sistema."
                )

                # Construct a simpler prompt for direct LLM call
                direct_llm_messages = [
                    ("system", KAVAK_SYSTEM_PROMPT),
                    ("system", MEXICAN_SALES_PERSONA),
                ]
                # chat_history_for_agent is already List[BaseMessage]
                direct_llm_messages.extend(chat_history_for_agent)
                direct_llm_messages.append(HumanMessage(content=message))

                simple_prompt = ChatPromptTemplate.from_messages(direct_llm_messages)

                # Directly invoke the LLM
                llm_response_obj = await self.llm.ainvoke(simple_prompt)
                agent_final_output = (
                    llm_response_obj.content if llm_response_obj else ""
                )
                logger.info(
                    f"💬 Respuesta directa del LLM (fallback RAG): {agent_final_output[:100]}..."
                )

            # Validate final response (either from agent or direct LLM call)
            if not agent_final_output or not agent_final_output.strip():
                logger.error(
                    "❌ El agente (o el LLM de respaldo) devolvió una respuesta vacía."
                )
                return SPANISH_ERROR_RESPONSES["empty_response"]

            # Optimize response for WhatsApp
            logger.info("✨ Optimizando respuesta para WhatsApp...")
            optimized_response = self._optimize_for_whatsapp(agent_final_output)

            logger.info(
                f"✅ Respuesta final: {optimized_response[:200]}..."
                if len(optimized_response) > 200
                else f"✅ Respuesta final: {optimized_response}"
            )
            return optimized_response

        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {str(e)}", exc_info=True)
            logger.error(f"🔧 Tipo de error: {type(e).__name__}")

            # Log the full error for debugging
            import traceback

            logger.error(f"📜 Stack trace: {traceback.format_exc()}")

            fallback = self._get_fallback_response(message)
            logger.warning(f"🔄 Usando respuesta de respaldo: {fallback[:200]}...")
            return fallback

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
        # Truncate if too long (using settings.RESPONSE_MAX_LENGTH instead of settings.response_max_length)
        if len(response) > settings.RESPONSE_MAX_LENGTH:
            response = (
                response[: settings.RESPONSE_MAX_LENGTH - 50]
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
