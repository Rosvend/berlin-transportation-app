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

- **Backend Framework**: FastAPI
- **Python Version**: 3.12
- **HTTP Client**: requests (sync)
- **Caching**: Redis 7 (with in-memory fallback)
- **Data Validation**: Pydantic
- **Template Engine**: Jinja2
- **Frontend**: Vanilla JS + Leaflet
- **Container**: Docker + Docker Compose
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
berlin-transportation-app/
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic (BVG client)
│   │   ├── utils/           # Utilities (cache)
│   │   ├── static/          # Static files (CSS, JS)
│   │   ├── templates/       # HTML templates
│   │   └── main.py          # Application entry point
│   ├── tests/               # Pytest tests
│   └── requirements.txt     # Python dependencies
├── frontend/                # Frontend files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript
│   └── index.html           # Main HTML
├── docker/                  # Docker configurations
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── .github/                 # CI/CD workflows
│   └── workflows/
├── docker-compose.yml       # Docker orchestration
├── start.sh                 # Single-command startup script
├── test_latency.py          # Latency testing
├── test_cache_performance.py # Cache performance testing
└── README.md                # This file
```

## How to run

### Quick Start (Recommended)

Start both frontend and backend with one command:

```bash
./start.sh
```

This script will:
- Check/create `.env` file
- Start Redis container (if Docker is available)
- Activate virtual environment
- Install dependencies
- Run all tests
- Launch backend API (http://localhost:8000)
- Launch frontend server (http://localhost:3000)

Access the app at: **http://localhost:3000**

### Alternative: Using Docker Compose

```bash
# Start all services (frontend, backend, redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Access Points

Once running, access:

- **Main Application**: http://localhost:3000 (Frontend + Backend)
- **API Documentation**: http://localhost:8000/docs
- **API Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## Testing

### Run All Tests

```bash
cd backend
source ../venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pytest tests/ -v
```

### Test Latency

To verify the application meets latency requirements (< 1 second):

```bash
# In a separate terminal, while the app is running
python test_latency.py
```

This will test various endpoints and report average response times.

### Redis Integration

The application supports Redis caching for improved performance:
- If Redis is available (via Docker): Automatic connection with persistent cache
- If Redis is not available: Fallback to in-memory cache

Check cache status:
```bash
curl http://localhost:8000/api/cache/stats