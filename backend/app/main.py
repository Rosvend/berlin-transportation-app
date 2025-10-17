"""
FastAPI Application for Berlin Transport Live
Real-time Berlin public transport information with caching
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.services.bvg_client import initialize_bvg_client, shutdown_bvg_client
from app.services.cache_service import initialize_cache_service, shutdown_cache_service
from app.api import stations, departures

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize BVG client
    initialize_bvg_client(settings.bvg_api_base_url)
    logger.info("BVG client initialized")
    
    # Initialize cache service
    try:
        await initialize_cache_service(settings.redis_url, settings.cache_ttl)
        logger.info("Cache service initialized")
    except Exception as e:
        logger.warning(f"Cache service initialization failed: {e}. Running without cache.")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await shutdown_bvg_client()
    await shutdown_cache_service()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Real-time Berlin public transport information with live departures and delays",
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")
except RuntimeError as e:
    logger.warning(f"Static files/templates not mounted: {e}")
    templates = None

# Include API routers
app.include_router(stations.router, prefix="/api", tags=["stations"])
app.include_router(departures.router, prefix="/api", tags=["departures"])


# Web routes
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Homepage with station search"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse(
        "<h1>Berlin Transport Live</h1>"
        "<p>API is running. Visit /docs for API documentation.</p>"
    )


@app.get("/station/{station_id}", response_class=HTMLResponse)
async def station_page(request: Request, station_id: str):
    """Station details page with live departures"""
    if templates:
        return templates.TemplateResponse(
            "station.html", 
            {"request": request, "station_id": station_id}
        )
    return HTMLResponse(
        f"<h1>Station {station_id}</h1>"
        f"<p>Visit /api/departures/{station_id} for departure data.</p>"
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "bvg_api": settings.bvg_api_base_url
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "stations_search": "/api/stations/search?q={query}",
            "stations_featured": "/api/stations/featured",
            "station_info": "/api/stations/{station_id}",
            "departures": "/api/departures/{station_id}?duration={minutes}",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1
    )