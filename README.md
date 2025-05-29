# Kavak AI Sales Agent for WhatsApp

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.0.200-FF6B6B.svg)](https://python.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10.0-2496ED.svg)](https://www.docker.com/)

## Overview

Welcome to the Kavak AI Sales Agent project! This is an intelligent car sales chatbot for the Mexican market, designed to interact with users via WhatsApp. The agent assists users in finding cars, understanding financing options, and answering questions about Kavak's services, all in Spanish (Mexican dialect).

## ⚠️ Disclaimer

**Important**: This is an independent project and is not affiliated with, endorsed by, or connected to Kavak in any way. It's a demonstration project only.

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Quick Start](#quick-start)
4. [Usage Examples](#usage-examples)
5. [Technical Stack](#technical-stack)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)
8. [Development Guide](#development-guide)
9. [Deployment](#deployment)
10. [Production Roadmap & Strategy](#production-roadmap--strategy)
11. [Future Enhancements](#future-enhancements)

## Key Features

### Car Search & Recommendations
* Search vehicles by budget, make, model, or features
* Get personalized recommendations based on user preferences
* View detailed specifications and pricing

### Financing Tools
* Calculate monthly payments with different down payment options
* Compare financing terms (3-6 years)
* Get detailed amortization schedules
* Budget planning based on desired monthly payment

### Kavak Information
* Learn about Kavak's warranty and certification process
* Get answers to frequently asked questions

### WhatsApp Integration
* Native Spanish language support (Mexican dialect)
* Context-aware conversations

### Developer Experience
* Comprehensive logging system
* Local development with Docker
* Automated testing suite
* API documentation with Swagger UI

## Quick Start

### Prerequisites

* **Core Requirements**
  * Python 3.11+
  * [UV](https://github.com/astral-sh/uv) package manager
  * Docker and Docker Compose

* **API Keys & Accounts**
  * [OpenAI API key](https://platform.openai.com/api-keys)
  * [Twilio account](https://www.twilio.com/try-twilio) (for WhatsApp integration)
  * [ngrok account](https://ngrok.com/) (for local development with WhatsApp)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sales_agent
   ```

2. **Run the setup script**

   ```bash
   make setup
   ```

   This will:
   - Create a `.env` file from `.env.example` if it doesn't exist
   - Install all Python dependencies using `uv`
   - Provide next steps for setting up the knowledge base

3. **Start the required services**

   Start all necessary services with one of these options:

   ```bash
   # For development with ngrok (recommended for WhatsApp testing)
   # This includes API, ChromaDB, Redis, and ngrok for webhook testing
   docker-compose --profile dev up -d
   
   # Or for core services only (API, ChromaDB and Redis):
   docker-compose up -d
   ```

   This will start all required services including ChromaDB for the knowledge base.

4. **Set up the knowledge base**

   ```bash
   make setup-knowledge
   ```

   This will populate the ChromaDB with Kavak's knowledge base.

   > **Note:** For more details about the knowledge base implementation, see the [Knowledge Base & RAG System](#knowledge-base--rag-system) section.

5. **Configure your environment**

   Edit the `.env` file with your API keys:

   ```bash
   # API Keys
   OPENAI_API_KEY=your_openai_key_here
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_whatsapp_number
   
   # Optional for local development
   NGROK_AUTHTOKEN=your_ngrok_token
   ```

6. **Configure Twilio Webhook** (for WhatsApp integration)
   - Get the webhook URL: `docker-compose logs -f ngrok-url`
   - Go to [Twilio Console WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
   - Set the webhook URL in the "When a message comes in" field
   - Save changes

### Verify Installation

Check that everything is working:

```bash
# Check service health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Test the agent locally
curl -X POST http://localhost:8000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, busco un auto", "session_id": "test"}'
```

## Usage Examples

### Testing the Agent Locally

You can test the agent without WhatsApp using the test endpoint:

```bash
curl -X POST http://localhost:8000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Busco una camioneta familiar con presupuesto de 300,000 pesos",
    "session_id": "test_session"
  }'
```

### Common User Interactions

**Car Search by Budget:**
```
User: "Busco un auto con presupuesto de 250,000 pesos"
Agent: "¡Perfecto! Encontré varios autos en tu presupuesto de $250,000 MXN..."
```

**Financing Calculation:**
```
User: "¿Cuánto pagaría mensualmente por un Honda Civic de 350,000?"
Agent: "Te ayudo con el cálculo de financiamiento para el Honda Civic..."
```

**Kavak Information:**
```
User: "¿Qué garantía ofrecen?"
Agent: "Kavak ofrece una garantía integral que incluye..."
```

### Development Commands

The project includes a `Makefile` with common development tasks:

```bash
# Install/update dependencies
make install-deps

# Format code
make format

# Run linters
make lint

# Run tests (87% coverage)
make test

# Run demo scenarios
make demo

# View logs in real-time
make logs

# Clean temporary files
make clean
```

## Technical Stack

### Core Technologies
* **FastAPI** - High-performance web framework for building APIs
* **LangChain** - Framework for developing applications powered by language models
* **OpenAI GPT-4o** - Advanced language model for natural language understanding
* **ChromaDB** - Vector database for efficient similarity search
* **Redis** - In-memory data store for conversation memory
* **Docker** - Containerization for consistent development and deployment
* **Twilio** - WhatsApp integration for customer interactions

## System Architecture Diagram

### Core Principles

The Kavak AI Sales Agent follows a Domain-Driven Design (DDD) approach with elements of Clean Architecture, organizing the codebase into distinct layers with clear responsibilities.



```mermaid
graph TB
    subgraph "Client Layer"
        WA[WhatsApp Users]
        TC[Test Clients]
        DEV[Developers]
    end
    
    subgraph "Interface Layer"
        TW[Twilio Webhook Handler]
        API[FastAPI Application]
        DOCS[API Documentation]
        HEALTH[Health Check]
    end
    
    subgraph "Application Layer"
        subgraph "AI Agent Core"
            AGENT[Kavak Sales Agent]
            EXEC[Agent Executor]
            LLM[OpenAI GPT-4o]
        end
        
        subgraph "Memory & Context"
            MEMORY[Conversation Memory]
            HISTORY[Chat History Manager]
            REDIS[Redis Store]
        end
    end
    
    subgraph "Domain Layer - Business Tools"
        subgraph "Car Search Tools"
            SEARCH_BUDGET[Search by Budget]
            SEARCH_SPECIFIC[Search Specific Car]
            SEARCH_POPULAR[Popular Cars]
        end
        
        subgraph "Financing Tools"
            CALC_BASIC[Basic Financing]
            CALC_MULTI[Multiple Options]
            CALC_BUDGET[Budget Calculator]
        end
        
        subgraph "Information Tools"
            KAVAK_INFO[Kavak Information]
            APPOINTMENT[Schedule Appointment]
        end
    end
    
    subgraph "Infrastructure Layer"
        subgraph "Data Sources"
            CSV[Car Catalog CSV]
            KB[Knowledge Base]
            CHROMA[ChromaDB Vector Store]
        end
        
        subgraph "External Services"
            OPENAI[OpenAI API]
            TWILIO[Twilio Service]
        end
        
        subgraph "System Services"
            LOGGING[Logging System]
            MONITORING[Health Monitoring]
            DOCKER[Docker Containers]
        end
    end
    
    %% User Flow
    WA -->|WhatsApp Messages| TW
    TC -->|HTTP Requests| API
    DEV -->|Development| DOCS
    
    %% Interface Processing
    TW --> API
    API --> AGENT
    API --> HEALTH
    
    %% Agent Processing
    AGENT --> EXEC
    EXEC --> LLM
    AGENT <--> MEMORY
    MEMORY <--> REDIS
    HISTORY --> REDIS
    
    %% Tool Execution
    EXEC --> SEARCH_BUDGET
    EXEC --> SEARCH_SPECIFIC
    EXEC --> SEARCH_POPULAR
    EXEC --> CALC_BASIC
    EXEC --> CALC_MULTI
    EXEC --> CALC_BUDGET
    EXEC --> KAVAK_INFO
    EXEC --> APPOINTMENT
    
    %% Data Access
    SEARCH_BUDGET --> CSV
    SEARCH_SPECIFIC --> CSV
    SEARCH_POPULAR --> CSV
    KAVAK_INFO --> KB
    KB --> CHROMA
    
    %% External Services
    LLM --> OPENAI
    TW --> TWILIO
    
    %% System Services
    AGENT --> LOGGING
    API --> MONITORING
    
    %% Styling
    classDef clientLayer fill:#e3f2fd
    classDef interfaceLayer fill:#f3e5f5
    classDef applicationLayer fill:#fff3e0
    classDef domainLayer fill:#e8f5e8
    classDef infrastructureLayer fill:#fce4ec
    
    class WA,TC,DEV clientLayer
    class TW,API,DOCS,HEALTH interfaceLayer
    class AGENT,EXEC,LLM,MEMORY,HISTORY,REDIS applicationLayer
    class SEARCH_BUDGET,SEARCH_SPECIFIC,SEARCH_POPULAR,CALC_BASIC,CALC_MULTI,CALC_BUDGET,KAVAK_INFO,APPOINTMENT domainLayer
    class CSV,KB,CHROMA,OPENAI,TWILIO,LOGGING,MONITORING,DOCKER infrastructureLayer
```

## Agent & Tools Architecture

Add this diagram to show the AI agent's internal architecture:

```mermaid
graph TD
    subgraph "User Input"
        USER_MSG[User Message]
    end
    
    subgraph "Prompt Engineering Pipeline"
        SYS_PROMPT[System Prompt]
        PERSONA[Mexican Sales Persona]
        ANTI_HALLUC[Anti-Hallucination Rules]
        CHAIN_VERIFY[Chain of Verification]
        FEW_SHOT[Few-Shot Examples]
        CONTEXT[Conversation Context]
    end
    
    subgraph "Agent Decision Engine"
        AGENT_CORE[Kavak Sales Agent]
        LLM[OpenAI GPT-4o]
        EXECUTOR[Agent Executor]
    end
    
    subgraph "Available Tools"
        subgraph "Search Tools"
            T1[search_cars_by_budget]
            T2[search_specific_car]
            T3[get_popular_cars]
        end
        
        subgraph "Finance Tools"
            T4[calculate_financing]
            T5[calculate_multiple_options]
            T6[calculate_budget_by_monthly_payment]
        end
        
        subgraph "Info Tools"
            T7[get_kavak_info]
            T8[schedule_appointment]
        end
    end
    
    subgraph "Response Generation"
        RESPONSE_GEN[Response Generator]
        WHATSAPP_OPT[WhatsApp Optimizer]
        EMOJI_ADD[Mexican Emojis]
        CHAR_LIMIT[Character Limiting]
        FINAL_RESP[Final Response]
    end
    
    %% Flow
    USER_MSG --> AGENT_CORE
    
    %% Prompt Assembly (happens in _create_agent method)
    AGENT_CORE --> SYS_PROMPT
    SYS_PROMPT --> PERSONA
    PERSONA --> ANTI_HALLUC
    ANTI_HALLUC --> CHAIN_VERIFY
    CHAIN_VERIFY --> FEW_SHOT
    FEW_SHOT --> CONTEXT
    
    %% LLM Processing (process_message method)
    CONTEXT --> LLM
    LLM --> EXECUTOR
    
    %% Tool Execution (AgentExecutor decides which tools to use)
    EXECUTOR --> T1
    EXECUTOR --> T2
    EXECUTOR --> T3
    EXECUTOR --> T4
    EXECUTOR --> T5
    EXECUTOR --> T6
    EXECUTOR --> T7
    EXECUTOR --> T8
    
    %% Response Pipeline (_optimize_for_whatsapp method)
    T1 --> RESPONSE_GEN
    T2 --> RESPONSE_GEN
    T3 --> RESPONSE_GEN
    T4 --> RESPONSE_GEN
    T5 --> RESPONSE_GEN
    T6 --> RESPONSE_GEN
    T7 --> RESPONSE_GEN
    T8 --> RESPONSE_GEN
    
    RESPONSE_GEN --> WHATSAPP_OPT
    WHATSAPP_OPT --> EMOJI_ADD
    EMOJI_ADD --> CHAR_LIMIT
    CHAR_LIMIT --> FINAL_RESP
    
    %% Styling
    classDef inputLayer fill:#e3f2fd
    classDef promptLayer fill:#f3e5f5
    classDef agentLayer fill:#fff3e0
    classDef toolLayer fill:#e8f5e8
    classDef responseLayer fill:#fce4ec
    
    class USER_MSG inputLayer
    class SYS_PROMPT,PERSONA,ANTI_HALLUC,CHAIN_VERIFY,FEW_SHOT,CONTEXT promptLayer
    class AGENT_CORE,LLM,EXECUTOR agentLayer
    class T1,T2,T3,T4,T5,T6,T7,T8 toolLayer
    class RESPONSE_GEN,WHATSAPP_OPT,EMOJI_ADD,CHAR_LIMIT,FINAL_RESP responseLayer
```

## Data Flow Diagram

Show how data flows through the system:

```mermaid
sequenceDiagram
    participant User as WhatsApp User
    participant Twilio as Twilio Webhook
    participant API as FastAPI App
    participant Agent as Kavak Agent
    participant Tools as Agent Tools
    participant Data as Data Sources
    participant Memory as Redis Memory
    participant LLM as OpenAI GPT-4o
    
    User->>Twilio: WhatsApp Message
    Twilio->>API: HTTP POST /webhook/whatsapp
    API->>Agent: process_message()
    
    Agent->>Memory: Load conversation history
    Memory-->>Agent: Previous context
    
    Agent->>LLM: Generate response with context + tools
    LLM->>Agent: Tool selection & reasoning
    
    alt Car Search Request
        Agent->>Tools: search_cars_by_budget()
        Tools->>Data: Query car catalog CSV
        Data-->>Tools: Matching cars
        Tools-->>Agent: Formatted results
    else Financing Request
        Agent->>Tools: calculate_financing()
        Tools->>Tools: Mathematical calculations
        Tools-->>Agent: Payment plan
    else Kavak Info Request
        Agent->>Tools: get_kavak_info()
        Tools->>Data: RAG query to ChromaDB
        Data-->>Tools: Relevant knowledge
        Tools-->>Agent: Information response
    end
    
    Agent->>Agent: Optimize for WhatsApp
    Agent->>Memory: Save conversation turn
    Agent-->>API: Optimized Spanish response
    API-->>Twilio: TwiML Response
    Twilio-->>User: WhatsApp Message
    
    Note over User,LLM: Complete conversation cycle<br/>with context preservation
```

### Knowledge Base & RAG System

The system implements an on-demand Retrieval-Augmented Generation (RAG) approach to provide accurate and up-to-date information about Kavak's services and policies.

#### Components

1. **Scraper** (`scripts/scrape_kavak.py`)
   - Crawls the Kavak website to extract structured knowledge
   - Handles rate limiting and error cases gracefully
   - Outputs structured JSON data for further processing

2. **Knowledge Base Setup** (`scripts/setup_knowledge_base.py`)
   - Processes scraped data and fallback content
   - Creates and populates a ChromaDB vector store
   - Implements text chunking and embedding generation
   - Handles versioning and updates of the knowledge base

3. **Knowledge Integration** (`src/knowledge/kavak_knowledge.py`)
   - Provides an interface to query the vector store
   - Implements semantic search capabilities
   - Manages the RAG pipeline for question answering

#### Usage

To update the knowledge base with the latest information:

```bash
# Scrape the latest data from Kavak's website
make scrape-kavak

# Set up the knowledge base (includes fallback content)
make setup-knowledge
```

#### Fallback Mechanism

The system includes a robust fallback mechanism:

1. **Primary Source**: Scraped data from Kavak's website
2. **Secondary Source**: Pre-defined fallback content for critical information
3. **Versioning**: Tracks when the knowledge was last updated
4. **Validation**: Ensures minimum required knowledge is always available

This approach ensures the system remains functional even when external sources are unavailable, while still providing the most accurate information possible.

### Redis Conversation Memory

#### Overview

The application uses Redis for persistent conversation memory, enabling stateful interactions with users across multiple sessions.

#### Features

* **Persistence**: Conversation history is preserved across application restarts
* **TTL (Time-To-Live)**: Conversations automatically expire after a configurable period
* **Performance**: In-memory storage ensures low-latency access to conversation history
* **High Availability**: Redis Sentinel support for failover scenarios

#### Configuration

Redis is configured using the following environment variables:

* `REDIS_URL`: Connection URL for Redis (default: `redis://localhost:6379`)
  * Format: `redis://[username:password@]host[:port][/db-number]`
  * Example: `redis://:mypassword@redis-host:6379/0`
* `REDIS_PASSWORD`: Optional password for Redis authentication

#### Docker Compose Setup

The Redis service is pre-configured in `docker-compose.yml` with the following settings:

```yaml
redis:
  image: redis:7-alpine
  container_name: kavak-redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 5s
    retries: 5
  restart: unless-stopped
```

Key features:
* **Persistence**: Data is stored in a Docker volume named `redis_data`
* **Health Checks**: Automatic monitoring of Redis service health
* **Auto-restart**: Service restarts automatically if it fails
* **Resource Limits**: Configured with appropriate memory limits

#### Data Structure

Conversation data is stored using the following Redis data structures:

1. **Conversation History** (List)
   * Key: `conversation:{session_id}`
   * Type: List of JSON-encoded messages
   * TTL: 30 days (configurable)

2. **Session Metadata** (Hash)
   * Key: `session:{session_id}:meta`
   * Fields:
     * `created_at`: Timestamp of session creation
     * `updated_at`: Timestamp of last activity
     * `message_count`: Total messages in conversation

#### Monitoring and Maintenance

To monitor Redis performance and health:

1. **Redis CLI**:
   ```bash
   docker exec -it kavak-redis redis-cli
   ```

2. **Key Metrics**:
   ```bash
   # Check memory usage
   redis-cli info memory
   
   # Monitor connected clients
   redis-cli info clients
   
   # Get all keys matching a pattern
   redis-cli --scan --pattern 'conversation:*' | wc -l
   ```

3. **Backup and Restore**:
   ```bash
   # Create backup
   docker exec kavak-redis redis-cli SAVE
   
   # Copy backup file
   cp /var/lib/docker/volumes/kavak_challenge_commercial_agent_redis_data/_data/dump.rdb /path/to/backup/
   ```

## API Reference

### API Endpoints

#### Root Endpoint

```http
GET /
```

Returns basic information about the API.

**Response Example:**

```json
{
  "message": "¡Hola! Soy el agente comercial de Kavak 🚗",
  "description": "Agente de IA para ayudarte a encontrar tu auto perfecto",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "webhook": "/webhook/whatsapp"
  }
}
```

#### Health Check

```http
GET /health
```

Returns the current status of the service.

**Response Example:**

```json
{
  "status": "OK",
  "service": "Kavak AI Agent",
  "version": "0.1.0",
  "language": "es_MX"
}
```

#### WhatsApp Webhook

```http
POST /webhook/whatsapp
```

Webhook endpoint for receiving and responding to WhatsApp messages via Twilio.

**Form Parameters:**

* `Body` (required): The message text from the user
* `From` (required): User's WhatsApp number with 'whatsapp:' prefix
* `To` (required): Twilio number that received the message
* `MessageSid` (required): Unique message identifier
* `NumMedia` (optional): Number of media files sent with the message

**Response:**
TwiML response for Twilio to send as WhatsApp messages.

**Example Response:**

```xml
<Response>
  <Message>¡Hola! Gracias por tu mensaje. ¿En qué puedo ayudarte hoy? 🚗</Message>
</Response>
```

#### Test Agent Locally

```http
POST /webhook/test
```

Test endpoint for local agent testing without Twilio.

**Request Body:**

```json
{
  "message": "Busco una camioneta familiar",
  "session_id": "test_session"
}
```

**Response Example:**

```json
{
  "response": "¡Hola! Claro, puedo ayudarte a encontrar una camioneta familiar. ¿Tienes alguna preferencia de marca o un presupuesto específico? 🚗",
  "session_id": "test_session",
  "processing_time": 1.25
}
```

#### Clear Conversation

```http
DELETE /webhook/conversation/{session_id}
```

Clear conversation history for a specific session.

**Path Parameters:**
*   `session_id` (required): The ID of the session to clear

**Response Example:**

```json
{
  "success": true,
  "message": "Conversation cleared for session test_session",
  "session_id": "test_session"
}
```

#### List Conversations

```http
GET /webhook/conversations
```

List all active conversation sessions.

**Response Example:**

```json
{
  "conversations": [
    {
      "session_id": "whatsapp_+5215512345678",
      "message_count": 5,
      "last_message": "¿Cuál es el precio de un Honda Civic?",
      "last_updated": "2023-05-28T10:15:30"
    }
  ],
  "count": 1
}
```

### Agent Tools Reference

#### Car Search Tools

##### search_cars_by_budget

Searches for cars within a specific budget range.

**Parameters:**

* `max_price` (float, required): Maximum budget in MXN
* `brand` (string, optional): Car brand to filter by

**Returns:**
Formatted string with search results in Spanish.

##### search_specific_car

Searches for a specific car by make and model.

**Parameters:**

* `brand` (string, required): Car brand
* `model` (string, required): Car model

**Returns:**
Formatted string with search results in Spanish.

##### get_popular_cars

Returns a list of popular cars in the Kavak catalog.

**Parameters:**

None

**Returns:**
Formatted string with popular car models in Spanish.

#### Financing Tools

##### calculate_financing

Calculates financing options for a car.

**Parameters:**

* `car_price` (float, required): Price of the car in MXN
* `down_payment` (float, required): Down payment amount in MXN
* `years` (integer, required): Financing term in years (3-6)

**Returns:**
Formatted string with financing details in Spanish.

##### calculate_multiple_options

Calculates multiple financing scenarios with different terms.

**Parameters:**

* `car_price` (float, required): Price of the car in MXN
* `down_payment` (float, required): Down payment amount in MXN

**Returns:**
Formatted string with multiple financing options in Spanish.

##### calculate_budget_by_monthly_payment

Determines the maximum car price based on desired monthly payment.

**Parameters:**

* `monthly_payment` (float, required): Desired monthly payment in MXN
* `down_payment_percentage` (float, optional): Percentage of down payment (default 20%)
* `years` (integer, optional): Financing term in years (default 4)

**Returns:**
Formatted string with budget estimation in Spanish.

#### Kavak Information Tools

##### get_kavak_info

Retrieves information about Kavak's services, policies, or general FAQs using RAG.

**Parameters:**

* `query` (string, required): User's question about Kavak

**Returns:**
Formatted string with information in Spanish.

## Development Guide

### Development Workflow

#### Code Structure

The project follows a Domain-Driven Design (DDD) approach with elements of Clean Architecture:

* **Interface Layer**: FastAPI application and endpoints
* **Application Layer**: Agent implementation and orchestration
* **Domain Layer**: Business logic and tools
* **Infrastructure Layer**: External services integration

#### Adding a New Tool

1. **Create a new tool file**

   Create a new file in `src/tools/` or add to an existing file:

   ```python
   from langchain.tools import tool
   from ..core.logging import get_logger

   logger = get_logger(__name__)

   @tool
   def mi_nueva_herramienta(parametro1: str, parametro2: int) -> str:
       """
       Descripción de la herramienta en español.

       Args:
           parametro1: Descripción del primer parámetro
           parametro2: Descripción del segundo parámetro

       Returns:
           Respuesta en español formateada para WhatsApp
       """
       try:
           # Implementación de la herramienta
           resultado = f"Resultado con {parametro1} y {parametro2}"
           return f"✅ Resultado: {resultado}"
       except Exception as e:
           logger.error(f"Error en mi_nueva_herramienta: {str(e)}")
           return "❌ Lo siento, hubo un problema. Por favor intenta de nuevo."
   ```

2. **Register the tool with the agent**

   Add your tool to the list in `src/webhook/twilio_handler.py`:

   ```python
   def get_kavak_agent():
       """Initialize Kavak agent with all tools"""
       tools = [
           # Existing tools...
           mi_nueva_herramienta,  # Add your new tool here
       ]
       return create_kavak_agent(tools)
   ```

3. **Add tests for your tool**

   Create tests in `tests/` directory:

   ```python
   def test_mi_nueva_herramienta():
       """Test mi_nueva_herramienta functionality"""
       result = mi_nueva_herramienta.invoke({"parametro1": "test", "parametro2": 123})
       assert "✅" in result
       assert "Resultado" in result
   ```

#### Coding Standards

1. **Type Hints**: Use Python type hints for all function parameters and return values
2. **Docstrings**: Add docstrings to all functions and classes
3. **Error Handling**: Implement proper error handling with Spanish user messages
4. **Logging**: Use the logger from `src.core.logging` for consistent logging
5. **Testing**: Write tests for all new functionality

#### WhatsApp Message Optimization

1. **Character Limit**: Keep responses under 1500 characters
2. **Emojis**: Use contextual emojis for better user experience
3. **Formatting**: Use clear formatting for readability on mobile devices
4. **Response Time**: Optimize for quick responses (under 5 seconds)

### Testing

#### Running Tests

The project includes a comprehensive test suite with 87% code coverage. Use the following `make` commands to run tests:

```bash
# Run all tests
make test

# Run specific test types
make test-unit     # Unit tests only
make test-integration  # Integration tests only
make test-e2e      # End-to-end tests only

# Run with coverage report (87% coverage)
make test-cov

# Run specific test file
uv run pytest tests/test_basic.py -v

# Test individual agent tools
make test-tools
```

#### Test Types

1. **Unit Tests**: Test individual functions and classes in isolation
   - Located in `tests/unit/`
   - Fast execution, no external dependencies

2. **Integration Tests**: Test interaction between components
   - Located in `tests/integration/`

3. **End-to-End Tests**: Test complete user flows
   - Located in `tests/e2e/`
   - Test full request/response cycles

4. **Spanish Language Tests**: Verify all user-facing responses are in Spanish
   - Located in `tests/spanish/`
   - Ensure proper localization and formatting

#### Mocking External Services

For testing without calling external APIs:

```python
from unittest.mock import patch

@patch('src.tools.car_search.search_cars_by_budget')
def test_with_mock(mock_search):
    mock_search.return_value = "Encontré 5 autos en tu presupuesto 🚗"
    # Test code here
```

### Debugging

#### Logging

The application uses a hierarchical logging system:

```python
from src.core.logging import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

Logs are written to `logs/kavak_agent.log` with rotation (10MB per file, keeping 3 backups). Log levels can be configured in `.env`:

```bash
# Logging configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
```

#### Debugging Tools

1. **FastAPI Debug Mode**: Run with `--reload` for auto-reloading
2. **Agent Verbose Mode**: Set `verbose=True` in the agent executor
3. **Tool Debugging**: Add debug logs in tool implementations
4. **Docker Logs**: Use `docker-compose logs -f` to view container logs

## Deployment

This section outlines the steps to build and deploy the Kavak AI Sales Agent using Docker.

### Prerequisites for Deployment

* Docker installed and running
* Docker Compose installed
* A configured `.env` file in the project root (refer to `.env.example`)

### Building Docker Images

The `docker-compose.yml` file defines the services. To build the images:

```bash
docker-compose build
```

This command will build the necessary images for the application (e.g., `kavak-api`, `chromadb`, `redis`).

### Running with Docker Compose

Once the images are built, you can start all services in detached mode:

```bash
docker-compose up -d
```

To view the logs for all services:

```bash
docker-compose logs -f
```

To view logs for a specific service (e.g., `kavak-api`):

```bash
docker-compose logs -f kavak-api
```

### Stopping Services

To stop all running services:

```bash
docker-compose down
```

### Environment Variables

The application relies on environment variables defined in the `.env` file at the root of the project. Ensure this file is correctly configured with necessary API keys (like `OPENAI_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`) and other settings before building or running the containers. The `docker-compose.yml` file is set up to pass these variables to the respective services.

### Accessing the Application

Once the services are running, the FastAPI application will typically be accessible at `http://localhost:8000` (or the port configured in your `.env` and `docker-compose.yml`).

* **API Docs**: `http://localhost:8000/docs`
* **Health Check**: `http://localhost:8000/health`

The WhatsApp webhook endpoint will be `http://<your-ngrok-or-public-url>/webhook/whatsapp`, which you'll need to configure in your Twilio console.

## Production Roadmap & Strategy

### How to Put This in Production?

#### Cloud Deployment Strategy
- **AWS/GCP/Azure**
- **Infrastructure as Code**
- **Container Orchestration**
- **Serverless Options**

#### CI/CD Pipeline
- **Automated Testing**
- **Blue/Green Deployments**
- **Feature Flags**
- **Automated Rollbacks**

#### Security & Compliance
- **Secrets Management**: Use AWS Secrets Manager or HashiCorp Vault
- **Network Security**: VPC, security groups, and WAF configuration
- **Compliance**: Data protection compliance for user data
- **Regular Audits**

#### Monitoring & Observability
- **Metrics Collection**: Prometheus for metrics, Grafana for visualization
- **Logging**: Centralized logging
- **Alerting**: Proactive alerting

### How to Evaluate Agent Performance?

#### Technical Metrics
- **Response Time**
- **Uptime & Reliability**
- **Resource Utilization**

#### Business Metrics
- **Conversion Rate**
- **User Retention**
- **Customer Satisfaction**
- **Cost per Interaction**

#### Quality Metrics
- **Hallucination Rate**
- **Language Quality**
- **Tool Usage**
- **Context Retention**

### How to Prevent Regressions?

#### Testing Strategy
- **Automated Test Suite**
- **Golden Dataset Testing**
- **Load Testing**

#### Monitoring & Safety
- **A/B Testing Framework**
- **Shadow Testing**
- **Canary Deployments**
- **Automated Rollbacks**

## Future Enhancements

* **Multi-language support**: Extend beyond Spanish to support other languages (English, Portuguese, Turkish)
* **Voice message integration**: Add support for WhatsApp voice messages
* **Image recognition**: Process car images sent by users
* **Advanced analytics**: Track user interactions and preferences
* **Integration with real Kavak API**: Connect to actual inventory and pricing data
* **Appointment scheduling**: Allow users to schedule test drives and visits
* **Payment processing**: Integrate with payment gateways for deposits

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.