.PHONY: help install dev docker-up docker-down docker-logs clean test format lint

# Default target
help:
	@echo "Berlin Transport Backend - Available Commands"
	@echo "=============================================="
	@echo "make install     - Install dependencies"
	@echo "make dev         - Run development server"
	@echo "make docker-up   - Start services with Docker"
	@echo "make docker-down - Stop Docker services"
	@echo "make docker-logs - View Docker logs"
	@echo "make test        - Run tests"
	@echo "make format      - Format code with black"
	@echo "make lint        - Lint code with flake8"
	@echo "make clean       - Clean cache and temp files"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using uv..."; \
		uv sync; \
	else \
		echo "Using pip..."; \
		pip install -e .; \
	fi
	@echo "✅ Dependencies installed"

# Run development server
dev:
	@echo "Starting development server..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@if command -v uv >/dev/null 2>&1; then \
		cd backend && uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	fi

# Start Docker services
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d backend redis
	@echo "✅ Services started"
	@echo "Access at: http://localhost:8000"

# Stop Docker services
docker-down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped"

# View Docker logs
docker-logs:
	docker-compose logs -f backend

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v
	@echo "✅ Tests complete"

# Format code
format:
	@echo "Formatting code with black..."
	black backend/
	@echo "✅ Code formatted"

# Lint code
lint:
	@echo "Linting code with flake8..."
	flake8 backend/ --max-line-length=100 --exclude=__pycache__,.venv
	@echo "✅ Linting complete"

# Clean cache files
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"
