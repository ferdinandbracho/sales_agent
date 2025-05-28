# Kavak AI Sales Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.0.200-FF6B6B.svg)](https://python.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10.0-2496ED.svg)](https://www.docker.com/)

An intelligent sales agent for Kavak Mexico that operates via WhatsApp, capable of recommending cars, calculating financing, and answering questions about Kavak's services.

An intelligent sales agent for Kavak Mexico that operates via WhatsApp, capable of recommending cars, calculating financing, and answering questions about Kavak's services.

## 🛠 Technical Stack

### Core Technologies
- **FastAPI** - High-performance web framework for building APIs
- **LangChain** - Framework for developing applications powered by language models
- **OpenAI GPT-4o** - Advanced language model for natural language understanding
- **ChromaDB** - Vector database for efficient similarity search
- **Redis** - In-memory data store for conversation memory
- **Docker** - Containerization for consistent development and deployment
- **Twilio** - WhatsApp integration for customer interactions

## Key Features

### Car Search & Recommendations
- Search vehicles by budget, make, model, or features
- Get personalized recommendations based on user preferences
- View detailed specifications and pricing

### Financing Tools
- Calculate monthly payments with different down payment options
- Compare financing terms (3-6 years)
- Get detailed amortization schedules
- Budget planning based on desired monthly payment

### Kavak Information
- Learn about Kavak's warranty and certification process
- Understand the vehicle inspection and delivery process
- Get answers to frequently asked questions

### WhatsApp Integration
- Native Spanish language support (Mexican dialect)
- Context-aware conversations
- Rich media support (images, documents)

### Developer Experience
- Comprehensive logging system
- Local development with Docker
- Automated testing suite
- API documentation with Swagger UI

## ⚠️ Disclaimer

**Important**: This is an independent project and is not affiliated with, endorsed by, or connected to Kavak in any way. It's a demonstration project only.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- [UV](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Twilio account (for WhatsApp integration)
- ngrok account (for local development with WhatsApp)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd commercial_agent
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys and configuration:
   ```bash
   # API Keys
   OPENAI_API_KEY=your_openai_key_here
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_whatsapp_number
   
   # Optional for local development
   NGROK_AUTHTOKEN=your_ngrok_token
   ```

3. **Start the services**
   ```bash
   # Start all services including ngrok
   docker-compose --profile dev up -d
   
   # Or start just the core services
   # docker-compose up -d
   ```

4. **Get the webhook URL** (if using ngrok)
   ```bash
   docker-compose logs -f ngrok-url
   ```
   Copy the webhook URL (e.g., `https://xxxx-xxxx-xxxx.ngrok-free.app/webhook/whatsapp`)

5. **Configure Twilio Webhook**
   - Go to [Twilio Console WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
   - Set the webhook URL in the "When a message comes in" field
   - Save changes

### Development Commands

```bash
# Install/update dependencies
make install-deps

# Format code
make format

# Run linters
make lint

# Run tests
make test

# Run specific test
make test-tools

# Run demo scenarios
make demo

# View logs in real-time
make logs

# Clean temporary files
make clean
```

## Example Usage

### Car Search
```
Usuario: Busco una camioneta familiar
Agente: ¡Hola! ¿Tienes alguna preferencia de marca o presupuesto?
Usuario: Máximo $500,000 MXN
Agente: Excelente, tengo varias opciones de SUV familiares en ese rango...
```

### Financing Calculation
```
Usuario: ¿Cuánto pagaría por un auto de $350,000 con 20% de enganche a 5 años?
Agente: 💰 **Plan de Financiamiento**

🚗 Precio: $350,000.00
💵 Enganche (20%): $70,000.00
📊 Monto a financiar: $280,000.00

⏱️ Plazo: 5 años (60 meses)
📅 Pago mensual: $5,947.42
💳 Total a pagar: $356,845.20
📈 Intereses: $76,845.20

✅ Tasa de interés: 10% anual
```

### Budget Planning
```
Usuario: Quiero pagar máximo $8,000 al mes
Agente: Con un pago de $8,000 mensuales, podrías considerar estos vehículos...
```

### Demo Commands
```bash
make demo         # Run demo scenarios
make test-tools   # Test individual tools
make logs         # View application logs
```

## Architecture

### Main Components
- **FastAPI**: Main API and webhook handling
- **LangChain**: Agent orchestration and tools
- **OpenAI GPT-4o**: Main language model
- **Pandas**: Car catalog processing
- **Twilio**: WhatsApp integration
- **ChromaDB**: Vector database for RAG (with dynamic fallback to base knowledge)
- **Redis**: Conversation memory storage

### Data Flow
```
WhatsApp User → Twilio → FastAPI → AI Agent → Tools → Response → WhatsApp
```

## Agent Tools

### Car Search Tools
- `search_cars_by_budget`: Find vehicles within a specific price range
- `search_specific_car`: Search by make, model, or features
- `get_popular_cars`: Get a list of popular car models

### Financing Tools
- `calculate_financing`: Calculate monthly payments with various terms
- `calculate_multiple_options`: View different financing scenarios with varying terms
- `calculate_budget_by_monthly_payment`: Determine maximum car price based on monthly budget

### Information & Appointment Tools
- `get_kavak_info`: Answer questions about Kavak's services and policies
- `schedule_appointment`: Schedule a test drive or sales consultation

## Data

The system uses `sample_caso_ai_engineer.csv` with 100 sample vehicles including:
- Make, model, year, version
- Price, mileage, dimensions
- Features (Bluetooth, CarPlay)
- Dimensions

## Development

### Project Structure
```
.
├── data/                    # Data files and datasets
│   ├── chroma_db/           # Vector database storage (ChromaDB)
│   └── logs/                # Application logs
├── scripts/                 # Utility and setup scripts
│   ├── demo_test.py         # Demo scenarios for testing
│   ├── scrape_kavak.py      # Web scraping utility
│   └── setup_knowledge_base.py  # Knowledge base initialization
├── src/                     # Source code
│   ├── agent/               # AI agent implementation
│   │   ├── kavak_agent.py   # Main agent class
│   │   └── prompts.py       # Agent prompts and system messages
│   ├── core/                # Core functionality
│   │   ├── config.py        # Application configuration
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── logging.py       # Logging configuration
│   │   └── middleware.py    # FastAPI middleware
│   ├── knowledge/           # Knowledge base management
│   │   ├── kavak_knowledge.py  # Knowledge base implementation
│   │   └── vector_store.py  # Vector store utilities
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── tools/               # Agent tools
│   │   ├── car_search.py    # Car search functionality
│   │   ├── financing.py     # Financing calculations
│   │   └── kavak_info.py    # Kavak information tools
│   ├── webhook/             # Webhook handlers
│   │   ├── twilio_handler.py # Twilio integration
│   │   └── response_formatter.py
│   ├── config.py            # Application settings
│   └── main.py              # FastAPI application entry point
├── tests/                   # Test suite
│   └── test_basic.py        # Basic functionality tests
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Makefile                # Common tasks and commands
├── README.md               # Project documentation
├── docker-compose.yml      # Docker Compose configuration
├── pyproject.toml          # Project metadata and dependencies
└── uv.lock                # Dependency lock file
```

### Logging

Logs are written to `logs/kavak_agent.log` with rotation (10MB per file, keeping 3 backups). Log levels can be configured in `.env`:

```bash
# Logging configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
```

### Local Development

1. **Start services**
```bash
docker-compose up -d
```

- 1.1 **Start services with ngrok**
```bash
docker-compose --profile dev up -d
```

2. **Run tests**
```bash
make test
```

3. **View logs**
```bash
tail -f logs/kavak_agent.log
```
- 3.1 **View logs in real-time**
```bash
make logs
```

4. **Access API documentation**
```
http://localhost:8000/docs
```

### Development Commands
```bash
make install-deps    # Install/update dependencies
make format         # Format code with Black
make lint           # Run code quality checks
make test           # Run tests
make clean          # Clean temporary files
```

### Adding New Features
1. Create new tool in `src/tools/`
2. Register tool with the agent
3. Add tests in `tests/`
4. Update documentation

## Testing

### Running Tests
```bash
# Run all tests
make test

# Test tools only
make test-tools

# Run demo scenarios
make demo

# Run with coverage report
make test-cov
```

### Testing WhatsApp Integration
1. Ensure the application is running with the webhook configured
2. Send a message to your Twilio sandbox number
3. Verify the agent's response in the logs:
   ```bash
   make logs
   ```
4. Check the API documentation at `http://localhost:8000/docs` for manual testing

## Development

### Local Development
```bash
make dev  # Local server with auto-reload
```

### Docker
```bash
docker-compose --profile dev up -d  # With Redis, ChromaDB and ngrok
```

## WhatsApp Setup

### 1. Set Up Twilio Sandbox
1. Create account at [Twilio](https://console.twilio.com)
2. Go to Messaging → Try it out → Send a WhatsApp message
3. Send `join [sandbox-name]` to +1 415 523 8886

### 2. Configure Webhook
1. Start application: `make dev`
2. Get public URL with ngrok
3. In Twilio Console → WhatsApp Sandbox Settings
4. Webhook URL: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`

### 3. Test Integration
Send a message to your Twilio sandbox number and verify the agent's response.

## Project Roadmap

### Phase 1: Core Infrastructure

- **Cloud Deployment**: Container orchestration with AWS ECS/Fargate for scalable container management
- **Database**: Integrate with PostgreSQL for connection pooling
- **Monitoring & Observability**:
  - Application monitoring with DataDog for metrics
  - Error tracking with Sentry for real-time error reporting
  - LLM-specific monitoring with LangSmith for prompt engineering and model performance
  - Custom metrics for tracking token usage and response quality
- **Security Layer**:
  - API Gateway with rate limiting and authentication
  - AWS Secrets Manager for secure credential management
  - VPC configuration for network isolation

### Phase 2: Performance & Scale

- **Caching Layer**: Implement Redis for frequent queries
- **API Optimization**: Add response compression and caching headers
- **Load Testing**: Identify and address performance bottlenecks
- **Auto-scaling**: Configure horizontal scaling for high availability

### Phase 3: Advanced Features

- **Analytics Dashboard**: User interaction metrics
- **A/B Testing**: Test different agent responses
- **Multi-language Support**: Expand beyond Spanish
- **CI/CD Pipeline**: Automated testing and deployment

## Evaluation Framework

### Code Quality

- **Testing**: Achieve >80% test coverage
- **Type Safety**: Implement MyPy for static type checking
- **Code Style**: Enforce consistent formatting with Ruff
- **Documentation**: Maintain up-to-date API and inline docs

### Performance

- **Response Time**: <500ms for 95% of requests
- **Error Rate**: <0.1% error rate in production
- **Uptime**: 99.9% availability target

### Security

- **Authentication**: Implement API key rotation
- **Data Protection**: Encrypt sensitive data at rest
- **Compliance**: Follow OWASP security guidelines

### Business Features
- CRM Integration
- Lead Scoring
- Appointment Scheduling
- Sales Analytics

## Contributing

### Development Process
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

### Code Standards
- Python 3.11+ with type hints
- Follow PEP 8 conventions

## Support

For issues or questions:
- Create a GitHub issue
- Check API documentation in `/docs`

## License

MIT License - see LICENSE file for details

---