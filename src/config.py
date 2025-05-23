"""
Configuration settings for Kavak AI Agent
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Twilio Configuration
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # ChromaDB Configuration
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8001"))
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_data")
    
    # Agent Configuration
    agent_language: str = os.getenv("AGENT_LANGUAGE", "es_MX")
    max_conversation_turns: int = int(os.getenv("MAX_CONVERSATION_TURNS", "10"))
    response_max_length: int = int(os.getenv("RESPONSE_MAX_LENGTH", "1500"))
    
    # Mexican Market Configuration
    currency: str = "MXN"
    currency_symbol: str = "$"
    default_interest_rate: float = 0.10  # 10% as specified in requirements
    financing_years_options: list = [3, 4, 5, 6]
    
    # Application
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Mexican-specific configurations
MEXICAN_CONFIG = {
    "greetings": {
        "morning": "¡Buenos días!",
        "afternoon": "¡Buenas tardes!", 
        "evening": "¡Buenas noches!",
        "general": "¡Hola!"
    },
    "expressions": {
        "positive": ["¡Órale!", "¡Padrísimo!", "¡Excelente!", "¡Perfecto!"],
        "thinking": ["Déjame verificar...", "Un momento por favor...", "Revisando..."],
        "help": ["¿En qué te puedo ayudar?", "¿Qué necesitas?", "¿Cómo te ayudo?"]
    },
    "emojis": {
        "car": "🚗",
        "money": "💰", 
        "phone": "📱",
        "happy": "😊",
        "check": "✅",
        "error": "❌",
        "thinking": "🤔",
        "search": "🔍"
    }
}

# Error messages in Spanish
SPANISH_ERROR_RESPONSES = {
    "openai_error": "Disculpa, tengo problemas técnicos. ¿Puedes intentar en un momento? 🔧",
    "search_empty": "No encontré autos con esos criterios. ¿Quieres ajustar tu búsqueda? 🔍", 
    "invalid_budget": "El presupuesto debe ser un número válido. ¿Puedes escribirlo nuevamente? 💰",
    "general_error": "Ups, algo salió mal. ¿Puedes intentar de nuevo? 😅",
    "timeout_error": "La búsqueda está tomando mucho tiempo. ¿Intentamos con otros criterios? ⏱️"
}
