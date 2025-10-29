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

# Import your API routers
from app.api import stations, departures, radar
from app.utils import get_cache_stats, clear_cache, cleanup_cache

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

# Enable CORS so the frontend (served on another port) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
app.include_router(stations.router, prefix="/api", tags=["stations"])
app.include_router(departures.router, prefix="/api", tags=["departures"])
app.include_router(radar.router, prefix="/api", tags=["radar"])


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


@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    stats = get_cache_stats()
    return {
        "cache": stats,
        "description": "Cache statistics for BVG API requests"
    }

@app.post("/api/cache/clear")
async def clear_cache_endpoint():
    """Clear all cached data"""
    clear_cache()
    return {"message": "Cache cleared successfully"}

@app.post("/api/cache/cleanup")
async def cleanup_cache_endpoint():
    """Remove expired cache entries"""
    removed = cleanup_cache()
    return {"message": f"Removed {removed} expired entries"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1
    )