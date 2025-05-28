"""
End-to-end tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from src.main import app
from src.webhook.twilio_handler import process_with_kavak_agent


class TestAPIEndpoints:
    """Test API endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture for FastAPI test client"""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")

        # Verify response
        assert response.status_code == 200
        assert (
            response.json()["message"] == "¡Hola! Soy el agente comercial de Kavak 🚗"
        )
        assert "endpoints" in response.json()
        assert "webhook" in response.json()["endpoints"]

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        # Verify response
        assert response.status_code == 200
        assert response.json()["status"] == "OK"
        assert response.json()["service"] == "Kavak AI Agent"
        assert response.json()["language"] == "es_MX"

    @patch("src.webhook.twilio_handler.process_with_kavak_agent")
    def test_whatsapp_webhook(self, mock_process, client):
        """Test WhatsApp webhook endpoint"""
        # Setup mock
        mock_process.return_value = (
            "¡Hola! Soy el agente de Kavak. ¿En qué puedo ayudarte?"
        )

        # Test webhook
        response = client.post(
            "/webhook/whatsapp",
            data={
                "Body": "Hola",
                "From": "whatsapp:+5215512345678",
                "To": "whatsapp:+14155238886",
                "MessageSid": "SM123456789",
            },
        )

        # Verify response
        assert response.status_code == 200
        assert "<Response>" in response.text
        assert "<Message>" in response.text
        assert "¡Hola!" in response.text

        # Verify process_with_kavak_agent was called
        mock_process.assert_called_once()
        call_args = mock_process.call_args[1]
        assert call_args["message"] == "Hola"
        assert "session_id" in call_args

    @patch("src.webhook.twilio_handler.process_with_kavak_agent")
    def test_whatsapp_webhook_error(self, mock_process, client):
        """Test WhatsApp webhook with error"""
        # Setup mock to raise exception
        mock_process.side_effect = Exception("Test error")

        # Test webhook
        response = client.post(
            "/webhook/whatsapp",
            data={
                "Body": "Hola",
                "From": "whatsapp:+5215512345678",
                "To": "whatsapp:+14155238886",
                "MessageSid": "SM123456789",
            },
        )

        # Verify response contains error message in Spanish
        assert response.status_code == 200
        assert "<Response>" in response.text
        assert "<Message>" in response.text
        assert "¡Ups!" in response.text or "Lo siento" in response.text

    @patch(
        "src.webhook.twilio_handler.process_with_kavak_agent", new_callable=AsyncMock
    )
    def test_test_agent_endpoint(self, mock_process, client):
        """Test agent test endpoint"""
        # Setup mock
        mock_process.return_value = "Respuesta de prueba del agente"

        # Test endpoint
        response = client.post(
            "/webhook/test-agent",
            json={"message": "Hola", "session_id": "test_session"},
        )

        # Verify response
        assert response.status_code == 200
        assert response.json()["agent_response"] == "Respuesta de prueba del agente"
        assert response.json()["session_id"] == "test_session"

    def test_clear_conversation(self, client):
        """Test clear conversation endpoint"""
        # First add a conversation to memory
        with patch(
            "src.webhook.twilio_handler.conversation_memory",
            {"test_session": [{"user": "test", "agent": "test"}]},
        ):
            response = client.delete("/webhook/conversations/test_session")

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "Conversation test_session cleared"

    def test_list_conversations(self, client):
        """Test list conversations endpoint"""
        # Setup mock conversations
        with patch(
            "src.webhook.twilio_handler.conversation_memory",
            {"test_session": [{"user": "test", "agent": "test", "timestamp": "123"}]},
        ):
            response = client.get("/webhook/conversations")

            # Verify response
            assert response.status_code == 200
            assert "sessions" in response.json()
            assert len(response.json()["sessions"]) == 1
            assert response.json()["sessions"][0]["session_id"] == "test_session"


class TestProcessWithKavakAgent:
    """Test process_with_kavak_agent function"""

    @patch("src.webhook.twilio_handler.kavak_agent")
    async def test_process_with_agent(self, mock_agent):
        """Test processing message with agent"""
        # Setup mock
        mock_process = AsyncMock(return_value="Respuesta del agente")
        mock_agent.process_message = mock_process

        # Process message
        result = await process_with_kavak_agent(
            message="Hola", session_id="test_session", conversation_history=[]
        )

        # Verify result
        assert result == "Respuesta del agente"

        # Verify agent was called
        mock_process.assert_called_once()
        call_args = mock_process.call_args[1]
        assert call_args["message"] == "Hola"
        assert call_args["session_id"] == "test_session"

    @patch("src.webhook.twilio_handler.kavak_agent")
    async def test_process_with_agent_error(self, mock_agent):
        """Test processing message with agent error"""
        # Setup mock to raise exception
        mock_agent.process_message = AsyncMock(side_effect=Exception("Test error"))

        # Process message
        result = await process_with_kavak_agent(
            message="Hola", session_id="test_session", conversation_history=[]
        )

        # Verify result contains the specific fallback response from the handler for 'Hola'
        assert "¡Hola! Soy tu agente comercial de Kavak" in result
        assert "¿Qué tipo de auto buscas?" in result

    @patch("src.webhook.twilio_handler.kavak_agent")
    async def test_process_with_agent_empty_response(self, mock_agent):
        """Test processing message with empty agent response"""
        # Setup mock to return empty response
        mock_agent.process_message = AsyncMock(return_value="")

        # Process message
        result = await process_with_kavak_agent(
            message="Hola", session_id="test_session", conversation_history=[]
        )

        # Verify result contains fallback message
        assert "No recibí una respuesta" in result or "¡Ups!" in result

    @patch("src.webhook.twilio_handler.kavak_agent")
    async def test_process_with_agent_long_response(self, mock_agent):
        """Test processing message with long agent response"""
        # Setup mock to return very long response
        long_response = "Respuesta " * 1000  # Very long response
        mock_agent.process_message = AsyncMock(return_value=long_response)

        # Process message
        result = await process_with_kavak_agent(
            message="Hola", session_id="test_session", conversation_history=[]
        )

        # Verify result is the full long response from the mock, as process_with_kavak_agent doesn't truncate
        assert len(result) == 10000
        assert "Respuesta" in result
