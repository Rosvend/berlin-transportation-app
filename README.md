# Real-Time Public Transport Data Pipeline

---

## Purpose

The purpose of this project is to build a modern, production-grade real-time data pipeline that extracts, stores, transforms, and visualizes live public transport data from Berlin’s BVG system using the [v6.bvg.transport.rest](https://v6.bvg.transport.rest) API. The pipeline is designed to be modular, cloud-portable (AWS-ready), and suitable for a data engineering portfolio.

---

## Scope

This project covers the **end-to-end lifecycle** of a real-time data pipeline:
- API data extraction
- Ingestion
- Loading
- Transformation
- Map visualization

---

## Tech stack

- **Backend Framework**: FastAPI 0.104
- **Python Version**: 3.12
- **HTTP Client**: httpx (async)
- **Caching**: Redis 7
- **Data Validation**: Pydantic 2.0
- **Template Engine**: Jinja2
- **Frontend**: Vanilla JS + Leaflet
- **Container**: Docker + Docker Compose
- **Package Manager**: UV / pip
- **Testing**: pytest + pytest-asyncio


### Layered Architecture

```
┌─────────────────────────────────┐
│     Presentation Layer          │
│  (Templates, Static Files, API) │
├─────────────────────────────────┤
│     Application Layer           │
│    (API Routes, Controllers)    │
├─────────────────────────────────┤
│     Business Logic Layer        │
│  (Services: BVG Client, Cache)  │
├─────────────────────────────────┤
│     Data Access Layer           │
│   (Models, External APIs)       │
└─────────────────────────────────┘
```
---

## Repo Structure

```bash
berlin-transport-pipeline/
├── airflow/                  # Airflow DAGs and configurations
│   ├── dags/
│   │   ├── __init__.py
│   │   └── ingest_departure.py
│   └── .gitkeep
├── config/                   # Configuration files
│   └── config.yaml
├── docker/                   # Dockerfiles and initialization scripts
│   ├── dockerfile.airflow
│   └── init-airflow.sh
├── etl/
│   ├── extract/
│   │   ├── __init__.py           # API data fetch logic
│   ├── __init__.py
│   ├── departures.py
│   └── utils.py
├── scripts/                  # Manual tests, utilities
│   ├── bucket_creation.sh
│   └── setup.sh
├── tests/                    # Pytest unit + integration tests
│   ├── __init__.py
│   └── test_departures.py
├── transform/                # Transformation logic
├── docker-compose.yml        # Orchestration of local stack
├── makefile                  # Makefile for convenience commands
├── .env                      # Secrets + credentials
├── README.md                 # Project documentation
├── .gitignore                # Git ignore file
```

## How to run

### For Windows

### Option 1: Using the Startup Script (Recommended)

```bash
# Make sure you're in the project root
cd berlin-transportation-app

# Run the dev startup script
uv run ./start-dev.sh
```

This will:
- Check/create `.env` file
- Start Redis if needed
- Install dependencies
- Launch the FastAPI application

### Option 2: Using Docker Compose

```bash
# Start backend and Redis
docker-compose up -d backend redis

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Option 3: Manual Setup

```bash
# 1. Create .env file
cp .env.example .env

# 2. Start Redis
docker-compose up -d redis
# OR use local Redis:
# redis-server

# 3. Install dependencies
pip install -r pyproject.toml

# 4. Run application
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### For Linux/Mac
```bash

# Run the makefile script
make up
```

## 🌐 Access Points

Once running, access:

- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health