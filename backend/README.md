# Berlin Transport Live - Backend

Real-time Berlin public transport information system built with FastAPI, showcasing departure times, delays, and network status.

## Architecture

This project follows a **Layered Architecture**:

```
backend/
├── app/
│   ├── api/              # API endpoints (Controllers)
│   │   ├── stations.py   # Station search & info
│   │   └── departures.py # Departure information
│   ├── models/           # Pydantic models (Data Transfer Objects)
│   │   └── transport.py  # Transport domain models
│   ├── services/         # Business logic layer
│   │   ├── bvg_client.py    # BVG API client
│   │   └── cache_service.py # Redis caching
│   ├── static/           # Frontend assets
│   │   ├── css/
│   │   └── js/
│   ├── templates/        # Jinja2 HTML templates
│   ├── utils/            # Utilities
│   │   └── logging_utils.py
│   ├── config.py         # Configuration management
│   ├── exceptions.py     # Custom exceptions
│   └── main.py           # Application entry point
```

## Features

- **Real-time Departures**: Live departure times with delay information
- **Station Search**: Search and discover transport stations
- **Featured Hubs**: Quick access to major transport hubs
- **Interactive Map**: Leaflet-based station mapping
- **Redis Caching**: Optimized API responses with TTL-based caching
- **Auto-refresh**: Live data updates every 30 seconds
- **RESTful API**: Well-documented API with OpenAPI/Swagger

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Redis (or use Docker Compose)
- UV package manager (optional, recommended)

### Local Development

1. **Clone and navigate to project**
   ```bash
   cd berlin-transportation-app
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   uv pip install -r pyproject.toml
   ```

4. **Start Redis** (if not using Docker)
   ```bash
   redis-server
   ```

5. **Run the application**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

### Using Docker Compose

1. **Start services**
   ```bash
   # Start only backend and Redis
   docker-compose up -d backend redis

   # Or with Airflow (for ETL pipeline)
   docker-compose --profile airflow up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f backend
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## API Endpoints

### Stations

- `GET /api/stations/search?q={query}` - Search stations
- `GET /api/stations/featured` - Get featured transport hubs
- `GET /api/stations/{station_id}` - Get station information

### Departures

- `GET /api/departures/{station_id}?duration={minutes}` - Get live departures

### System

- `GET /api/health` - Health check
- `GET /api/info` - API information
- `GET /docs` - Interactive API documentation (Swagger UI)

## Configuration

Configuration is managed through environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "Berlin Transport Live" |
| `ENVIRONMENT` | Environment (development/production) | "development" |
| `DEBUG` | Debug mode | true |
| `BVG_API_BASE_URL` | BVG API endpoint | https://v6.bvg.transport.rest |
| `REDIS_HOST` | Redis hostname | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `CACHE_TTL` | Cache TTL in seconds | 300 |
| `LOG_LEVEL` | Logging level | INFO |
```