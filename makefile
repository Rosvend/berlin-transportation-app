# Berlin Transport Data Pipeline - Makefile
# Convenience commands for managing the development environment

.PHONY: help setup up down logs clean test lint format init-airflow create-buckets

# Default target
help:
	@echo "Available commands:"
	@echo "  setup          - Initial project setup (copy .env, create directories)"
	@echo "  up             - Start all services"
	@echo "  down           - Stop all services"
	@echo "  logs           - Show logs from all services"
	@echo "  logs-airflow   - Show only Airflow logs"
	@echo "  logs-minio     - Show only MinIO logs"
	@echo "  clean          - Clean up containers and volumes"
	@echo "  clean-all      - Clean everything (including images)"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  init-airflow   - Initialize Airflow (run after first startup)"
	@echo "  create-buckets - Create MinIO buckets"
	@echo "  airflow-shell  - Get shell access to Airflow container"
	@echo "  reset          - Complete reset (down, clean, up)"

# Initial project setup
setup:
	@echo "Setting up project..."
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "✅ Created .env file from template. Please update with your values."; \
	else \
		echo "⚠️  .env file already exists."; \
	fi
	@mkdir -p data/raw data/staging data/processed
	@mkdir -p logs
	@mkdir -p docker
	@echo "✅ Created necessary directories"

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up --build -d
	@echo "✅ Services started. Access:"
	@echo "   - Airflow UI: http://localhost:8080 (admin/admin)"
	@echo "   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)"
	@echo "   - Streamlit Dashboard: http://localhost:8501"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

logs-airflow:
	docker-compose logs -f airflow-webserver airflow-scheduler airflow-worker

logs-minio:
	docker-compose logs -f minio

# Clean up
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f

clean-all: clean
	@echo "Removing all images..."
	docker-compose down --rmi all
	docker system prune -af

# Testing
test:
	@echo "Running tests..."
	docker-compose exec airflow-webserver python -m pytest tests/ -v

# Code quality
lint:
	@echo "Running linting..."
	docker-compose exec airflow-webserver flake8 dags/ extract/ --max-line-length=88

format:
	@echo "Formatting code..."
	docker-compose exec airflow-webserver black dags/ extract/

# Initialize Airflow (run after first startup)
init-airflow:
	@echo "Initializing Airflow..."
	docker-compose exec airflow-webserver airflow db init
	docker-compose exec airflow-webserver airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@bvg-pipeline.com \
		--password admin

# Create MinIO buckets
create-buckets:
	@echo "Creating MinIO buckets..."
	@docker-compose exec airflow-webserver python /opt/airflow/scripts/setup_minio.py

# Create MinIO buckets
create-directories:
	@echo "Creating project directories..."
	@mkdir -p airflow/dags airflow/docker
	@mkdir -p extract tests notebooks dashboards
	@mkdir -p data/raw data/staging data/mart
	@mkdir -p dbt/models/staging dbt/models/marts
	@mkdir -p config logs
	@echo "✅ Project directories created"

# Get shell access to Airflow container
airflow-shell:
	docker-compose exec airflow-webserver bash

# Complete reset
reset: down clean up
	@echo "Waiting for services to start..."
	@sleep 10
	@make init-airflow
	@make create-buckets
	@echo "✅ Complete reset finished"

# Development helpers
dev-install:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-streamlit.txt
	pre-commit install

# Check service health
health:
	@echo "Checking service health..."
	@echo "Airflow Webserver:"
	@curl -f http://localhost:8080/health || echo "❌ Airflow not healthy"
	@echo ""
	@echo "MinIO:"
	@curl -f http://localhost:9000/minio/health/live || echo "❌ MinIO not healthy"
	@echo ""
	@echo "Streamlit:"
	@curl -f http://localhost:8501/_stcore/health || echo "❌ Streamlit not healthy"

# Database operations
db-reset:
	@echo "Resetting Airflow database..."
	docker-compose exec airflow-webserver airflow db reset --yes
	@make init-airflow

# Show running services
status:
	@echo "Service Status:"
	docker-compose ps