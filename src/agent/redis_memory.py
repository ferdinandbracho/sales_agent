"""
Redis-based conversation memory system for Kavak AI Agent.
Provides persistent storage for conversation history with TTL support.
"""

import json
import time
from typing import Dict, List, Any

import redis
from redis.exceptions import RedisError

from ..config import settings
from ..core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class RedisConversationMemory:
    """Redis-based conversation memory implementation with TTL support"""

    def __init__(self, ttl_seconds: int = 86400):  # Default TTL: 24 hours
        """
        Initialize Redis connection

        Args:
            ttl_seconds: Time-to-live in seconds for conversation data
        """
        self.ttl_seconds = ttl_seconds
        self.redis_client = None
        self.is_connected = False
        self.connect()

    def connect(self) -> bool:
        """
        Connect to Redis server

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Parse Redis URL from settings
            redis_url = settings.redis.REDIS_URL
            redis_password = settings.redis.REDIS_PASSWORD

            # Create Redis client
            self.redis_client = redis.from_url(
                redis_url,
                password=redis_password if redis_password else None,
                decode_responses=True,  # Automatically decode responses to strings
            )

            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis at {redis_url}")
            return True

        except RedisError as e:
            logger.error(f"Redis connection error: {str(e)}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {str(e)}")
            self.is_connected = False
            return False

    def get_conversation_key(self, session_id: str) -> str:
        """
        Generate Redis key for a conversation

        Args:
            session_id: Unique session identifier

        Returns:
            str: Formatted Redis key
        """
        return f"kavak:conversation:{session_id}"

    def save_conversation(
        self, session_id: str, conversation_history: List[Dict[str, Any]]
    ) -> bool:
        """
        Save conversation history to Redis

        Args:
            session_id: Unique session identifier
            conversation_history: List of conversation turns

        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.is_connected and not self.connect():
            logger.error("Cannot save conversation - Redis not connected")
            return False

        try:
            # Limit conversation history to the most recent turns
            max_turns = settings.MAX_CONVERSATION_TURNS
            if len(conversation_history) > max_turns:
                conversation_history = conversation_history[-max_turns:]

            # Serialize conversation history
            key = self.get_conversation_key(session_id)
            serialized_data = json.dumps(conversation_history)

            # Save to Redis with TTL
            self.redis_client.setex(key, self.ttl_seconds, serialized_data)

            # Update last activity timestamp
            self.update_session_activity(session_id)

            logger.debug(
                f"Saved conversation for session {session_id} ({len(conversation_history)} turns)"
            )
            return True

        except RedisError as e:
            logger.error(f"Redis error saving conversation: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return False

    def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history from Redis

        Args:
            session_id: Unique session identifier

        Returns:
            List[Dict[str, Any]]: Conversation history or empty list if not found
        """
        if not self.is_connected and not self.connect():
            logger.error("Cannot get conversation - Redis not connected")
            return []

        try:
            # Get serialized data from Redis
            key = self.get_conversation_key(session_id)
            serialized_data = self.redis_client.get(key)

            if not serialized_data:
                logger.debug(f"No conversation found for session {session_id}")
                return []

            # Deserialize conversation history
            conversation_history = json.loads(serialized_data)

            # Update last activity timestamp
            self.update_session_activity(session_id)

            logger.debug(
                f"Retrieved conversation for session {session_id} ({len(conversation_history)} turns)"
            )
            return conversation_history

        except RedisError as e:
            logger.error(f"Redis error retrieving conversation: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for session {session_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return []

    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete conversation history from Redis

        Args:
            session_id: Unique session identifier

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if not self.is_connected and not self.connect():
            logger.error("Cannot delete conversation - Redis not connected")
            return False

        try:
            # Delete conversation and activity key
            key = self.get_conversation_key(session_id)
            activity_key = f"kavak:activity:{session_id}"

            self.redis_client.delete(key, activity_key)
            logger.info(f"Deleted conversation for session {session_id}")
            return True

        except RedisError as e:
            logger.error(f"Redis error deleting conversation: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False

    def update_session_activity(self, session_id: str) -> None:
        """
        Update last activity timestamp for a session

        Args:
            session_id: Unique session identifier
        """
        try:
            # Set activity timestamp
            activity_key = f"kavak:activity:{session_id}"
            timestamp = int(time.time())
            self.redis_client.setex(activity_key, self.ttl_seconds, timestamp)

        except RedisError as e:
            logger.error(f"Redis error updating activity: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating activity: {str(e)}")

    def list_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active conversation sessions with metadata

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of session IDs and their metadata
        """
        if not self.is_connected and not self.connect():
            logger.error("Cannot list sessions - Redis not connected")
            return {}

        try:
            # Get all conversation keys
            conversation_pattern = "kavak:conversation:*"
            all_keys = self.redis_client.keys(conversation_pattern)

            result = {}
            for key in all_keys:
                # Extract session ID from key
                session_id = key.split(":", 2)[2]

                # Get conversation data
                conversation_data = self.get_conversation(session_id)

                # Get TTL
                ttl = self.redis_client.ttl(key)

                # Get last activity timestamp
                activity_key = f"kavak:activity:{session_id}"
                last_activity = self.redis_client.get(activity_key) or "0"

                # Add session metadata
                result[session_id] = {
                    "message_count": len(conversation_data),
                    "ttl_seconds": ttl,
                    "last_activity": int(last_activity),
                    "last_message": conversation_data[-1]["user"]
                    if conversation_data
                    else "",
                }

            return result

        except RedisError as e:
            logger.error(f"Redis error listing sessions: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            return {}


# Global instance
redis_memory = RedisConversationMemory()
