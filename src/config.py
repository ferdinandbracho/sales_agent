"""
Configuration settings for Kavak AI Agent
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Twilio Configuration
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = "whatsapp:+14155238886"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None

    # ChromaDB Configuration
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_persist_directory: str = "./chroma_data"

    # Agent Configuration
    agent_language: str = "es_MX"
    max_conversation_turns: int = 10
    response_max_length: int = 1500

    # Mexican Market Configuration
    currency: str = "MXN"
    currency_symbol: str = "$"
    default_interest_rate: float = 0.10  # 10% as specified in requirements
    financing_years_options: list = [3, 4, 5, 6]

    # Application
    port: int = 8000
    host: str = "0.0.0.0"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


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
}
