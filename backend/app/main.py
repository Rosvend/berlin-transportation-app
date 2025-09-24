"""
FastAPI Web Application for Berlin Transport
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Import your API routers
from app.api import stations, departures

# Create FastAPI instance
app = FastAPI(
    title="Berlin Transport Live",
    description="Real-time Berlin public transport information",
    version="1.0.0"
)

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
app.include_router(stations.router, prefix="/api", tags=["stations"])
app.include_router(departures.router, prefix="/api", tags=["departures"])

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
