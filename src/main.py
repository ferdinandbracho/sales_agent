"""
Kavak AI Sales Agent - Main FastAPI Application
Agente comercial de IA para Kavak México
"""

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import and include webhook routes
from src.webhook.twilio_handler import router as webhook_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Kavak AI Sales Agent",
    description="Agente comercial de IA para Kavak México 🚗",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - Saludo inicial"""
    return {
        "message": "¡Hola! Soy el agente comercial de Kavak 🚗",
        "description": "Agente de IA para ayudarte a encontrar tu auto perfecto",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "webhook": "/webhook/whatsapp",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Kavak AI Agent",
        "version": "0.1.0",
        "language": "es_MX",
    }


# Include webhook routes
app.include_router(webhook_router, prefix="/webhook", tags=["WhatsApp"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
