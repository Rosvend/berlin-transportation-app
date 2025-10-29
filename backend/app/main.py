"""
FastAPI Web Application for Berlin Transport
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Import your API routers
from app.api import stations, departures, radar
from app.utils import get_cache_stats, clear_cache, cleanup_cache

# Create FastAPI instance
app = FastAPI(
    title="Berlin Transport Live",
    description="Real-time Berlin public transport information",
    version="1.0.0"
)

# Enable CORS so the frontend (served on another port) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo deployment
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

# Web routes (HTML pages)
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Homepage with station search"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/station/{station_id}", response_class=HTMLResponse)
async def station_page(request: Request, station_id: str):
    """Station details page with live departures"""
    return templates.TemplateResponse(
        "station.html", 
        {"request": request, "station_id": station_id}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "berlin-transport-web"}

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
