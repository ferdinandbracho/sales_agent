"""
Configuration settings for Kavak AI Agent
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    """Logging configuration settings"""

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
    )
    LOG_FILE: str = "kavak_agent.log"
    LOG_DIR: str = "logs"
    MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT: int = 3

    @property
    def LOG_PATH(self) -> Path:
        """Get the full path to the log file"""
        return Path(self.LOG_DIR) / self.LOG_FILE


class OpenAISettings(BaseSettings):
    """OpenAI configuration settings"""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"


class TwilioSettings(BaseSettings):
    """Twilio configuration settings"""

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = "whatsapp:+14155238886"


class RedisSettings(BaseSettings):
    """Redis configuration settings"""

    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None


class ChromaDBSettings(BaseSettings):
    """ChromaDB configuration settings"""

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # External Services
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    twilio: TwilioSettings = Field(default_factory=TwilioSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    chroma: ChromaDBSettings = Field(default_factory=ChromaDBSettings)

    # Agent Configuration
    AGENT_LANGUAGE: str = "es_MX"
    MAX_CONVERSATION_TURNS: int = 10
    RESPONSE_MAX_LENGTH: int = 1500

    # Mexican Market Configuration
    CURRENCY: str = "MXN"
    CURRENCY_SYMBOL: str = "$"
    DEFAULT_INTEREST_RATE: float = 0.10  # 10% as specified in requirements
    FINANCING_YEARS_OPTIONS: list = [3, 4, 5, 6]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",  # Allows nested settings with __
    )

    @property
    def is_production(self) -> bool:
        """Check if the application is running in production"""
        return self.ENVIRONMENT.lower() == "production"


# Global settings instance
settings = Settings()


# Mexican-specific configurations
MEXICAN_CONFIG = {
    "greetings": {
        "morning": "¡Buenos días!",
        "afternoon": "¡Buenas tardes!",
        "evening": "¡Buenas noches!",
        "general": "¡Hola!",
    },
    "expressions": {
        "positive": ["¡Órale!", "¡Padrísimo!", "¡Excelente!", "¡Perfecto!"],
        "thinking": ["Déjame verificar...", "Un momento por favor...", "Revisando..."],
        "help": ["¿En qué te puedo ayudar?", "¿Qué necesitas?", "¿Cómo te ayudo?"],
    },
    "emojis": {
        "car": "🚗",
        "money": "💰",
        "phone": "📱",
        "happy": "😊",
        "check": "✅",
        "error": "❌",
        "thinking": "🤔",
        "search": "🔍",
    },
}

# Error messages in Spanish
SPANISH_ERROR_RESPONSES = {
    "openai_error": "Disculpa, tengo problemas técnicos. ¿Puedes intentar en un momento? 🔧",
    "search_empty": "No encontré autos con esos criterios. ¿Quieres ajustar tu búsqueda? 🔍",
    "invalid_budget": "El presupuesto debe ser un número válido. ¿Puedes escribirlo nuevamente? 💰",
    "general_error": "Ups, algo salió mal. ¿Puedes intentar de nuevo? 😅",
    "timeout_error": "La búsqueda está tomando mucho tiempo. ¿Intentamos con otros criterios? ⏱️",
    "empty_response": "No recibí una respuesta del agente. Por favor, intenta de nuevo en un momento. 🔄",
}
