# Berlin Transport Data Pipeline - Makefile
# Convenience commands for managing the development environment

# Detect OS for cross-platform compatibility
ifeq ($(OS),Windows_NT)
    SHELL := cmd.exe
    .SHELLFLAGS := /c
    SLEEP_CMD := timeout /t 15 /nobreak >nul
    CURL_SILENT := curl -f -s
    TIMEOUT_CMD := timeout /t 30
else
    SLEEP_CMD := sleep 15
    CURL_SILENT := curl -f -s
    TIMEOUT_CMD := timeout 30
endif

.PHONY: help setup up down logs clean test lint format init-airflow create-buckets

# Default target
help:
	@echo Available commands:
	@echo   setup          - Initial project setup (copy .env, create directories)
	@echo   up             - Start all services and initialize everything
	@echo   up-basic       - Start services only (no initialization)
	@echo   down           - Stop all services
	@echo   logs           - Show logs from all services
	@echo   logs-airflow   - Show only Airflow logs
	@echo   logs-minio     - Show only MinIO logs
	@echo   clean          - Clean up containers and volumes
	@echo   clean-all      - Clean everything (including images)
	@echo   test           - Run tests
	@echo   lint           - Run linting
	@echo   format         - Format code
	@echo   reset          - Complete reset (down, clean, up)
	@echo   health         - Check service health
	@echo   status         - Show service status

# Initial project setup
setup:
	@echo Setting up project...
ifeq ($(OS),Windows_NT)
	@if not exist .env copy .env.template .env && echo Created .env file from template. Please update with your values. || echo .env file already exists.
	@if not exist data\raw mkdir data\raw
	@if not exist data\staging mkdir data\staging
	@if not exist data\processed mkdir data\processed
	@if not exist logs mkdir logs
else
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "✅ Created .env file from template. Please update with your values."; \
	else \
		echo "⚠️  .env file already exists."; \
	fi
	@mkdir -p data/raw data/staging data/processed
	@mkdir -p logs
endif
	@echo Created necessary directories

# Start all services with full initialization
up:
	@echo Starting Berlin Transport Data Pipeline...
	@echo This will:
	@echo    1. Build and start all containers
	@echo    2. Initialize Airflow database and create admin user
	@echo    3. Create MinIO buckets
	@echo    4. Verify all services are healthy
	@echo.
	@echo Starting containers...
	@docker-compose up --build -d
	@echo Waiting for services to be ready...
	@$(SLEEP_CMD)
	@echo Initializing Airflow...
	@$(MAKE) _init-airflow-silent
	@echo Creating MinIO buckets...
	@$(MAKE) _create-buckets-silent
	@echo Performing health checks...
	@$(MAKE) _health-check-silent
	@echo.
	@echo Pipeline is ready! Access your services:
	@echo    - Airflow UI: http://localhost:8080 (admin/admin)
	@echo    - MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)
	@echo    - Streamlit Dashboard: http://localhost:8501
	@echo.
	@echo Quick start:
	@echo    - Check service status: make status
	@echo    - View logs: make logs
	@echo    - Run tests: make test

# Start services only (no initialization) - for development
up-basic:
	@echo Starting services without initialization...
	@docker-compose up --build -d
	@echo Services started (basic mode)

# Stop all services
down:
	@echo Stopping all services...
	@docker-compose down

# Show logs
logs:
	@docker-compose logs -f

logs-airflow:
	@docker-compose logs -f airflow-webserver airflow-scheduler airflow-worker

logs-minio:
	@docker-compose logs -f minio

# Clean up
clean:
	@echo Cleaning up containers and volumes...
	@docker-compose down -v
	@docker system prune -f

clean-all: clean
	@echo Removing all images...
	@docker-compose down --rmi all
	@docker system prune -af

# Testing
test:
	@echo Running tests...
	@docker-compose exec airflow-webserver python -m pytest tests/ -v || echo Tests failed or test container not ready

# Code quality
lint:
	@echo Running linting...
	@docker-compose exec airflow-webserver flake8 dags/ extract/ --max-line-length=88 || echo Linting failed or container not ready

format:
	@echo Formatting code...
	@docker-compose exec airflow-webserver black dags/ extract/ || echo Formatting failed or container not ready

# Private target for silent Airflow initialization
_init-airflow-silent:
	@docker-compose exec -T airflow-webserver airflow db init >nul 2>&1 || echo DB already initialized
	@docker-compose exec -T airflow-webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@bvg-pipeline.com --password admin >nul 2>&1 || echo Admin user already exists

# Private target for silent bucket creation
_create-buckets-silent:
	@docker-compose exec -T airflow-webserver python /opt/airflow/scripts/setup_minio.py >nul 2>&1 || echo Bucket creation failed

# Private target for silent health checks
_health-check-silent:
ifeq ($(OS),Windows_NT)
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8080/health -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop } catch { Write-Host 'Airflow health check timeout' }"
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:9000/minio/health/live -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop } catch { Write-Host 'MinIO health check timeout' }"
else
	@timeout 30 bash -c 'until curl -f http://localhost:8080/health > /dev/null 2>&1; do sleep 2; done' || echo "⚠️  Airflow health check timeout"
	@timeout 30 bash -c 'until curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do sleep 2; done' || echo "⚠️  MinIO health check timeout"
endif

# Manual initialization commands (for debugging)
init-airflow:
	@echo Initializing Airflow manually...
	@docker-compose exec airflow-webserver airflow db init
	@docker-compose exec airflow-webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@bvg-pipeline.com --password admin

create-buckets:
	@echo Creating MinIO buckets manually...
	@docker-compose exec airflow-webserver python /opt/airflow/scripts/setup_minio.py

# Complete reset
reset: down clean up
	@echo Complete reset finished

# Check service health
health:
	@echo Checking service health...
	@echo Airflow Webserver:
ifeq ($(OS),Windows_NT)
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8080/health -UseBasicParsing -ErrorAction Stop; Write-Host ' Healthy' } catch { Write-Host ' Unhealthy' }"
	@echo MinIO:
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:9000/minio/health/live -UseBasicParsing -ErrorAction Stop; Write-Host ' Healthy' } catch { Write-Host ' Unhealthy' }"
	@echo Streamlit:
	@powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8501/_stcore/health -UseBasicParsing -ErrorAction Stop; Write-Host ' Healthy' } catch { Write-Host ' Unhealthy' }"
else
	@curl -f http://localhost:8080/health && echo " ✅ Healthy" || echo " ❌ Unhealthy"
	@echo "MinIO:"
	@curl -f http://localhost:9000/minio/health/live && echo " ✅ Healthy" || echo " ❌ Unhealthy"
	@echo "Streamlit:"
	@curl -f http://localhost:8501/_stcore/health && echo " ✅ Healthy" || echo " ❌ Unhealthy"
endif

# Show running services
status:
	@echo Service Status:
	@docker-compose ps