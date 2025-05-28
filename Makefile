# Makefile for Kavak AI Agent
# One-command operations for development

.PHONY: help setup dev test clean logs install-deps run-local

help: ## Show this help message
	@echo "🚗 Kavak AI Agent - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "🚀 Setting up Kavak AI Agent..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "⚠️  Please edit .env file with your API keys"; \
		echo "⚠️  Required: OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"; \
		echo ""; \
		echo "📝 Edit .env file and then run 'make dev'"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "📦 Installing dependencies with uv..."
	uv sync
	@echo "📚 Setting up Kavak knowledge base..."
	uv run python scripts/setup_knowledge_base.py
	@echo "✅ Setup complete!"

setup-knowledge: ## Setup Kavak knowledge base (scraping + fallback)
	@echo "🌐 Setting up Kavak knowledge base..."
	uv run python scripts/setup_knowledge_base.py
	@echo "✅ Knowledge base ready!"

scrape-kavak: ## Scrape Kavak website for knowledge base
	@echo "🌐 Scraping Kavak website..."
	uv run python scripts/scrape_kavak.py
	@echo "✅ Scraping complete!"

install-deps: ## Install/update dependencies with uv
	@echo "📦 Installing dependencies with uv..."
	uv sync

dev: ## Start development environment
	@echo "🔥 Starting Kavak AI Agent in development mode..."
	@echo "📱 API will be available at: http://localhost:8000"
	@echo "📊 API Docs: http://localhost:8000/docs"
	@echo ""
	uv run python src/main.py

run-local: ## Run the application locally
	@echo "🚗 Starting Kavak AI Agent..."
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run all tests
	@echo "🧪 Running all tests..."
	uv run pytest -v -p pytest_dotenv -p pytest_asyncio --cache-clear tests/

.PHONY: test-unit test-integration test-e2e test-cov

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	uv run python tests/run_tests.py --unit --verbose

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	uv run python tests/run_tests.py --integration --verbose

test-e2e: ## Run end-to-end tests only
	@echo "🧪 Running end-to-end tests..."
	uv run python tests/run_tests.py --e2e --verbose

test-cov: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	uv run python tests/run_tests.py --all --verbose --coverage

test-tools: ## Test individual agent tools
	@echo "🔧 Testing agent tools..."
	@echo "\n🚗 Testing car search tool..."
	uv run python -c "from src.tools.car_search import search_cars_by_budget; print(search_cars_by_budget.invoke({'max_price': 300000, 'brand': 'Toyota'}))"
	@echo "\n💰 Testing financing tool..."
	uv run python -c "from src.tools.financing import calculate_financing; print(calculate_financing.invoke({'car_price': 250000, 'down_payment': 50000, 'years': 4}))"
	@echo "\nℹ️  Testing Kavak info tool..."
	uv run python -c "from src.tools.kavak_info import get_kavak_info; print(get_kavak_info.invoke({'query': 'garantía'}))"

demo: ## Run demo conversation scenarios
	@echo "🎭 Running demo scenarios..."
	@echo "Demo scenarios:"
	@echo "1. Search for cars under 300k"
	@echo "2. Calculate financing for 250k car"
	@echo "3. Get Kavak information"
	uv run python scripts/demo_test.py

lint: ## Run code quality checks
	@echo "🔍 Running code quality checks..."
	uv run black --check src/
	uv run isort --check-only src/
	@echo "✅ Code quality checks passed"

format: ## Format code
	@echo "✨ Formatting code..."
	uv run black src/
	uv run isort src/
	@echo "✅ Code formatted"

logs: ## Show application logs and logging configuration
	@echo "📋 Application Logs"
	@echo "================"
	@echo "Log File: data/logs/app.log"
	@echo "Current Log Level: $$(grep LOG_LEVEL .env 2>/dev/null | cut -d '=' -f2 || echo 'INFO (default)')"
	@echo "\n🔍 Viewing Logs:"
	@echo "  make logs-tail    # Follow logs in real-time"
	@echo "  make logs-view    # View last 50 log entries"
	@echo "  make logs-errors  # View only error messages"

logs-tail: ## Follow application logs in real-time
	@echo "🔍 Following application logs (Ctrl+C to exit)..."
	@mkdir -p data/logs
	@touch data/logs/app.log
	@tail -f data/logs/app.log

logs-view: ## View recent log entries
	@echo "📜 Last 50 log entries:"
	@mkdir -p data/logs
	@touch data/logs/app.log
	@tail -n 50 data/logs/app.log 2>/dev/null || echo "No log file found at data/logs/app.log"

logs-errors: ## View error logs
	@echo "❌ Error log entries:"
	@mkdir -p data/logs
	@touch data/logs/app.log
	@grep -i "error\|exception\|critical\|fatal" data/logs/app.log 2>/dev/null || echo "No errors found in logs"

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

check-env: ## Check if environment variables are set
	@echo "🔍 Checking environment configuration..."
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
		if grep -q "your_openai_api_key_here" .env; then \
			echo "⚠️  Please update OPENAI_API_KEY in .env"; \
		else \
			echo "✅ OPENAI_API_KEY configured"; \
		fi; \
		if grep -q "your_twilio_account_sid" .env; then \
			echo "⚠️  Please update TWILIO_ACCOUNT_SID in .env"; \
		else \
			echo "✅ TWILIO_ACCOUNT_SID configured"; \
		fi; \
	else \
		echo "❌ .env file not found. Run 'make setup' first"; \
	fi

install-uv: ## Install uv package manager (if not installed)
	@echo "📦 Installing uv package manager..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv is already installed"; \
		uv --version; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
	fi

quick-start: ## Complete quick start (setup + run)
	@echo "🚀 Kavak AI Agent - Quick Start"
	@echo "==============================="
	make install-uv
	make setup
	@echo ""
	@echo "🎯 Next steps:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run 'make dev' to start the application"
	@echo "3. Visit http://localhost:8000/docs for API documentation"

# Project info
info: ## Show project information
	@echo "🚗 Kavak AI Agent - Project Information"
	@echo "======================================"
	@echo "Language: Spanish (Mexican)"
	@echo "Framework: FastAPI + LangChain + OpenAI"
	@echo "Purpose: AI Sales Agent for WhatsApp"
	@echo ""
	@echo "📁 Project structure:"
	@echo "  src/           - Source code"
	@echo "  src/agent/     - AI agent logic"
	@echo "  src/tools/     - Agent tools"
	@echo "  src/webhook/   - WhatsApp integration"
	@echo "  data/          - Car catalog data"
	@echo "  tests/         - Test suite"
	@echo ""
	@echo "🛠️  Key commands:"
	@echo "  make setup     - Initial setup"
	@echo "  make dev       - Start development"
	@echo "  make test      - Run tests"
	@echo "  make demo      - Test demo scenarios"
