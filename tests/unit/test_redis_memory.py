"""
Unit tests for Redis-based conversation memory
"""

import json
from unittest.mock import patch, MagicMock

import redis

from src.agent.redis_memory import RedisConversationMemory


class TestRedisConversationMemory:
    """Test Redis-based conversation memory functionality"""

    def test_initialization(self):
        """Test memory initialization with mocked Redis"""
        with patch("src.agent.redis_memory.redis.from_url") as mock_redis:
            # Mock Redis client
            mock_client = MagicMock()
            mock_redis.return_value = mock_client

            # Create memory instance
            memory = RedisConversationMemory(ttl_seconds=3600)

            # Verify Redis client was created with correct parameters
            mock_redis.assert_called_once()
            assert memory.ttl_seconds == 3600
            assert memory.redis_client is not None

    def test_get_conversation_key(self):
        """Test key generation for conversations"""
        with patch("src.agent.redis_memory.redis.from_url"):
            memory = RedisConversationMemory()
            key = memory.get_conversation_key("test_session")
            assert key == "kavak:conversation:test_session"

    @patch("src.agent.redis_memory.redis.from_url")
    def test_save_conversation(self, mock_redis):
        """Test saving conversation to Redis"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        # Create memory instance
        memory = RedisConversationMemory()
        memory.is_connected = True
        memory.redis_client = mock_client

        # Test data
        session_id = "test_session"
        conversation = [
            {
                "user": "Hola",
                "agent": "¡Hola! ¿En qué puedo ayudarte?",
                "timestamp": "123",
            }
        ]

        # Call save method
        result = memory.save_conversation(session_id, conversation)

        # Verify Redis setex was called with correct parameters
        assert mock_client.setex.call_count == 2

        # Get the first call arguments (conversation data)
        first_call = mock_client.setex.call_args_list[0][0]
        assert first_call[0] == "kavak:conversation:test_session"
        assert first_call[1] == 86400  # Default TTL
        assert json.loads(first_call[2]) == conversation

        # Get the second call arguments (activity timestamp)
        second_call = mock_client.setex.call_args_list[1][0]
        assert second_call[0] == "kavak:activity:test_session"
        assert second_call[1] == 86400  # Default TTL
        assert isinstance(second_call[2], int)  # Timestamp

        assert result is True

    @patch("src.agent.redis_memory.redis.from_url")
    def test_get_conversation(self, mock_redis):
        """Test retrieving conversation from Redis"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        # Create memory instance
        memory = RedisConversationMemory()
        memory.is_connected = True
        memory.redis_client = mock_client

        # Test data
        session_id = "test_session"
        conversation = [
            {
                "user": "Hola",
                "agent": "¡Hola! ¿En qué puedo ayudarte?",
                "timestamp": "123",
            }
        ]

        # Mock Redis get to return serialized conversation
        mock_client.get.return_value = json.dumps(conversation)

        # Call get method
        result = memory.get_conversation(session_id)

        # Verify Redis get was called with correct key
        mock_client.get.assert_called_once_with("kavak:conversation:test_session")
        assert result == conversation

    @patch("src.agent.redis_memory.redis.from_url")
    def test_get_conversation_empty(self, mock_redis):
        """Test retrieving non-existent conversation"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        # Create memory instance
        memory = RedisConversationMemory()
        memory.is_connected = True
        memory.redis_client = mock_client

        # Mock Redis get to return None (no conversation found)
        mock_client.get.return_value = None

        # Call get method
        result = memory.get_conversation("test_session")

        # Verify result is empty list
        assert result == []

    @patch("src.agent.redis_memory.redis.from_url")
    def test_delete_conversation(self, mock_redis):
        """Test deleting conversation from Redis"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        # Create memory instance
        memory = RedisConversationMemory()
        memory.is_connected = True
        memory.redis_client = mock_client

        # Call delete method
        result = memory.delete_conversation("test_session")

        # Verify Redis delete was called with correct keys
        mock_client.delete.assert_called_once()
        call_args = mock_client.delete.call_args[0]
        assert "kavak:conversation:test_session" in call_args
        assert "kavak:activity:test_session" in call_args
        assert result is True

    @patch("src.agent.redis_memory.redis.from_url")
    def test_list_active_sessions(self, mock_redis):
        """Test listing active sessions from Redis"""
        # Mock Redis client
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        # Create memory instance
        memory = RedisConversationMemory()
        memory.is_connected = True
        memory.redis_client = mock_client

        # Mock Redis keys to return session keys
        mock_client.keys.return_value = [
            "kavak:conversation:session1",
            "kavak:conversation:session2",
        ]

        # Mock get_conversation to return test data
        memory.get_conversation = MagicMock(
            return_value=[{"user": "test", "agent": "test"}]
        )

        # Mock ttl and get for activity
        mock_client.ttl.return_value = 3600
        mock_client.get.return_value = "1621234567"

        # Call list method
        result = memory.list_active_sessions()

        # Verify Redis keys was called with correct pattern
        mock_client.keys.assert_called_once_with("kavak:conversation:*")

        # Verify result contains expected sessions
        assert "session1" in result
        assert "session2" in result
        assert result["session1"]["message_count"] == 1
        assert result["session1"]["ttl_seconds"] == 3600
        assert result["session1"]["last_activity"] == 1621234567

    @patch("src.agent.redis_memory.redis.from_url")
    def test_redis_error_handling(self, mock_redis):
        """Test error handling for Redis operations"""
        # Mock Redis client to raise exception
        mock_redis.side_effect = redis.RedisError("Connection error")

        # Create memory instance
        memory = RedisConversationMemory()

        # Verify connection failed
        assert memory.is_connected is False

        # Test operations with failed connection
        assert memory.get_conversation("test_session") == []
        assert memory.save_conversation("test_session", []) is False
        assert memory.delete_conversation("test_session") is False
        assert memory.list_active_sessions() == {}
