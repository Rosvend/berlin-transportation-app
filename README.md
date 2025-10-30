# Real-Time Public Transport Data Pipeline - Berlin Transport App
---
## Purpose

The purpose of this project is to build a modern, production-grade real-time data pipeline that extracts, stores, transforms, and visualizes live public transport data from Berlin's BVG system using the v6.bvg.transport.rest API. The pipeline is designed to be modular, cloud-portable (AWS-ready), and suitable for a data engineering portfolio.

---
## Scope
This project covers the end-to-end lifecycle of a real-time data pipeline:

- API data extraction
- Ingestion & caching
- Loading & transformation
- Real-time visualization
- Interactive map with live vehicle tracking

## Features

### Core Functionality
-  **Station Search**: Real-time station search with autocomplete (min. 2 characters)
- **Live Departures**: Real-time departure information with delay indicators
- **Interactive Map**: Leaflet-based map centered on Berlin
- **Vehicle Radar**: Live tracking of buses, trains, and trams (NEW!)
- **Favorites System**: Save frequently used stations with LocalStorage persistence
- **Dark Mode**: Toggle between light and dark themes
- **Search History**: Quick access to recent searches
- **Performance Optimization**: In-memory cache with 55-95% latency reduction

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **HTTP Client**: requests (sync)
- **Caching**: Custom in-memory cache with TTL
- **Data Validation**: Pydantic
- **Template Engine**: Jinja2
- **Server**: Uvicorn with hot-reload

### Frontend
- **UI Framework**: Bootstrap 5.3.0
- **Map Library**: Leaflet 1.9.4
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla ES6+

### Testing & DevOps
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Linting**: Black, Flake8, isort, ESLint
- **CI/CD**: GitHub Actions
- **Container**: Docker + Docker Compose

## Architecture

### Layered Architecture
```text
┌─────────────────────────────────┐
│ Presentation Layer              │
│ (Templates, Static Files, API)  │
├─────────────────────────────────┤
│ Application Layer               │
│ (API Routes, Controllers)       │
├─────────────────────────────────┤
│ Business Logic Layer            │
│ (Services: BVG Client, Cache)   │
├─────────────────────────────────┤
│ Data Access Layer               │
│ (Models, External APIs)         │
└─────────────────────────────────┘
```
### Repo Structure

```text
berlin-transportation-app/
├── backend/ # FastAPI backend application
│   ├── app/
│   │   ├── api/ # API endpoints
│   │   │   ├── departures.py
│   │   │   ├── stations.py
│   │   │   └── radar.py # NEW: Vehicle radar endpoint
│   │   ├── models/ # Pydantic models
│   │   │   └── transport.py
│   │   ├── services/ # Business logic
│   │   │   └── bvg_client.py
│   │   ├── utils/ # Utilities
│   │   │   ├── cache.py # In-memory cache with TTL
│   │   │   └── __init__.py
│   │   ├── static/ # Static files
│   │   │   ├── css/
│   │   │   └── js/
│   │   ├── templates/ # HTML templates
│   │   │   └── index.html
│   │   └── main.py # Application entry point
│   ├── tests/ # Pytest tests (27/27 passing)
│   │   ├── conftest.py # Shared fixtures
│   │   ├── test_api_endpoints.py
│   │   ├── test_bvg_client.py
│   │   └── test_cache.py
│   ├── requirements.txt # Python dependencies
│   ├── requirements-dev.txt # Development dependencies
│   └── setup.cfg # Test configuration
├── frontend/ # Frontend files
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js # 1000+ lines of JavaScript
│   └── index.html
├── .github/ # CI/CD workflows
│   └── workflows/
│       └── ci.yml # 4 jobs: lint & test
├── docs/ # Documentation
├── docker-compose.yml # Docker orchestration
├── TASK_PLAN.md # Task planning
└── README.md 
```

## How to Run

### Quick Start (Recommended)

### 1. Clone the Repository 
```text
```bash
git clone https://github.com/Rosvend/berlin-transportation-app.git
cd berlin-transportation-app
git checkout main
```
### 2. Install Backend Dependencies
```text
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```
### 3. Start Backend (Terminal 1)
```text
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
### 4. Start Frontend (Terminal 2)
```text
cd frontend
python -m http.server 3001
```
### 5. Access the Application
```text
Main Application: http://localhost:3001
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health
```
## Testing
```text
cd backend
python -m pytest tests/ -v
```

