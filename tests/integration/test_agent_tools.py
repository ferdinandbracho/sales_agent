"""
Integration tests for Kavak agent with tools
"""

import pytest
from langchain_core.runnables import Runnable
from unittest.mock import patch, MagicMock, AsyncMock

from src.agent.kavak_agent import KavakSalesAgent, create_kavak_agent
from src.config import SPANISH_ERROR_RESPONSES
from src.tools.car_search import search_cars_by_budget, search_specific_car
from src.tools.financing import calculate_financing
from src.tools.kavak_info import get_kavak_info


class TestAgentToolsIntegration:
    """Test integration between agent and tools"""

    @pytest.fixture
    def mock_llm(self):
        """Fixture for mocked LLM"""
        with patch("src.agent.kavak_agent.ChatOpenAI") as mock_llm:
            # Configure the mock LLM to return a simple response
            mock_instance = MagicMock()
            mock_instance.invoke.return_value = MagicMock(
                content="Respuesta simulada del agente"
            )
            mock_instance.ainvoke.return_value = MagicMock(
                content="Respuesta simulada del agente"
            )
            mock_llm.return_value = mock_instance
            yield mock_llm

    @pytest.fixture
    def agent_with_tools(self, mock_llm):
        """Fixture for agent with tools"""
        tools = [
            search_cars_by_budget,
            search_specific_car,
            calculate_financing,
            get_kavak_info,
        ]
        return KavakSalesAgent(tools=tools)

    @patch("src.tools.car_search.pd.read_csv")
    async def test_agent_car_search_integration(self, mock_read_csv, agent_with_tools, mocker):
        """Test agent integration with car search tools"""
        # Setup mock data
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.__getitem__.return_value = mock_df
        mock_df.str.contains.return_value = mock_df
        mock_df.to_dict.return_value = [
            {"make": "Toyota", "model": "Corolla", "price": 300000}
        ]
        mock_read_csv.return_value = mock_df

        # Configure agent executor to use car search tool
        mock_executor = AsyncMock()
        mock_executor.ainvoke.return_value = {
            "output": "Te muestro los autos disponibles",
            "intermediate_steps": [
                (
                    MagicMock(tool="search_cars_by_budget"),
                    "Encontré 1 auto en tu presupuesto: Toyota Corolla $300,000 MXN",
                )
            ],
        }
        mocker.patch.object(agent_with_tools, 'agent_executor', mock_executor)

        # Test agent with car search message
        response = await agent_with_tools.process_message(
            message="Busco un auto con presupuesto de 300,000 pesos",
            session_id="test_session",
        )

        # Verify response contains car information
        assert response is not None
        assert "auto" in response.lower() or "toyota" in response.lower()

    @patch("src.tools.financing.calculate_financing")
    async def test_agent_financing_integration(
        self, mock_calculate_financing, agent_with_tools, mocker
    ):
        """Test agent integration with financing tools"""
        # Setup mock financing tool
        financing_result = """
        💰 Plan de Financiamiento:
        Precio: $300,000.00
        Enganche: $60,000.00
        Plazo: 4 años
        Pago mensual: $6,082.33
        """
        mock_calculate_financing.invoke.return_value = financing_result

        # Configure agent executor to use financing tool
        mock_executor = AsyncMock()
        mock_executor.ainvoke.return_value = {
            "output": "Aquí está tu plan de financiamiento",
            "intermediate_steps": [
                (MagicMock(tool="calculate_financing"), financing_result)
            ],
        }
        mocker.patch.object(agent_with_tools, 'agent_executor', mock_executor)

        # Test agent with financing message
        response = await agent_with_tools.process_message(
            message="¿Cuánto pagaría por un auto de 300,000 con 20% de enganche a 4 años?",
            session_id="test_session",
        )

        # Verify response contains financing information
        assert response is not None
        assert "financiamiento" in response.lower() or "plan" in response.lower()

    @patch("src.knowledge.kavak_knowledge.get_kavak_knowledge_base")
    async def test_agent_kavak_info_integration(self, mock_get_kb, agent_with_tools, mocker):
        """Test agent integration with Kavak info tool"""
        # Setup mock KB
        mock_kb = MagicMock()
        mock_kb.is_ready = True
        mock_kb.search_knowledge.return_value = [
            {
                "content": "Kavak ofrece garantía de 3 meses o 3,000 km en todos sus vehículos.",
                "metadata": {"category": "warranty"},
                "distance": 0.1,
            }
        ]
        mock_get_kb.return_value = mock_kb

        # Configure agent executor to use Kavak info tool
        mock_executor = AsyncMock()
        mock_executor.ainvoke.return_value = {
            "output": "Te explico sobre la garantía de Kavak",
            "intermediate_steps": [
                (
                    MagicMock(tool="get_kavak_info"),
                    "Kavak ofrece garantía de 3 meses o 3,000 km en todos sus vehículos.",
                )
            ],
        }
        mocker.patch.object(agent_with_tools, 'agent_executor', mock_executor)

        # Test agent with Kavak info message
        response = await agent_with_tools.process_message(
            message="¿Qué garantía ofrecen en los autos?", session_id="test_session"
        )

        # Verify response contains warranty information
        assert response is not None
        assert "garantía" in response.lower() or "kavak" in response.lower()

    @patch("src.knowledge.kavak_knowledge.get_kavak_knowledge_base")
    async def test_agent_rag_fallback(self, mock_get_kb, agent_with_tools, mocker):
        """Test agent fallback when RAG returns empty"""
        # Setup mock KB that returns empty results
        mock_kb = MagicMock()
        mock_kb.is_ready = True
        mock_kb.search_knowledge.return_value = []
        mock_get_kb.return_value = mock_kb

        # Configure agent executor with empty RAG result but empty final output
        mock_executor = AsyncMock()
        mock_executor.ainvoke.return_value = {
            "output": "",  # Empty output to trigger fallback
            "intermediate_steps": [
                (
                    MagicMock(tool="get_kavak_info"),
                    "",  # Empty RAG result
                )
            ],
        }
        mocker.patch.object(agent_with_tools, 'agent_executor', mock_executor)

        # Configure direct LLM response for fallback
        agent_with_tools.llm.ainvoke.return_value = MagicMock(
            content="Respuesta directa del LLM como fallback"
        )

        # Test agent with message that would trigger RAG
        response = await agent_with_tools.process_message(
            message="¿Cuál es el proceso de compra en Kavak?", session_id="test_session"
        )

        # Verify fallback was used
        assert response is not None
        assert response != SPANISH_ERROR_RESPONSES["empty_response"]

        # Verify LLM was called directly as fallback
        agent_with_tools.llm.ainvoke.assert_called_once()

    async def test_agent_conversation_history(self, agent_with_tools, mocker):
        """Test agent with conversation history"""
        # Setup conversation history
        conversation_history = [
            {"user": "Hola", "agent": "¡Hola! ¿En qué puedo ayudarte?"},
            {"user": "Busco un auto", "agent": "¿Qué tipo de auto buscas?"},
        ]

        # Configure agent executor
        mock_executor = AsyncMock()
        mock_executor.ainvoke.return_value = {
            "output": "Basado en nuestra conversación anterior, te recomiendo...",
            "intermediate_steps": [],
        }
        mocker.patch.object(agent_with_tools, 'agent_executor', mock_executor)

        # Test agent with conversation history
        response = await agent_with_tools.process_message(
            message="Un Toyota Corolla",
            session_id="test_session",
            conversation_history=conversation_history,
        )

        # Verify conversation history was used
        assert response is not None

        # Verify agent executor was called with chat history
        call_args = agent_with_tools.agent_executor.ainvoke.call_args[0][0]
        assert "chat_history" in call_args
        assert len(call_args["chat_history"]) > 0

    @patch("src.agent.kavak_agent.create_openai_tools_agent")
    def test_create_kavak_agent(self, mock_create_agent):
        """Test agent factory function"""
        # Setup mock
        mock_agent = MagicMock(spec=Runnable)
        mock_create_agent.return_value = mock_agent

        # Create tools list
        tools = [search_cars_by_budget, calculate_financing]

        # Call factory function
        agent = create_kavak_agent(tools)

        # Verify agent was created
        assert agent is not None

        # Verify create_openai_tools_agent was called with tools
        mock_create_agent.assert_called_once()
        call_args = mock_create_agent.call_args[1]
        assert "tools" in call_args
        assert call_args["tools"] == tools
