"""
NovaCare Health - Epic EHR Mock API
Simulates patient records, appointments, and scheduling for Zendesk FDE assessment.
Features Excel-based data storage with default and working copies for demo resets.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from config import API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_ORIGINS
from data import load_data_on_startup
from routes import (
    health_router,
    identity_router,
    appointments_router,
    admin_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load data on startup."""
    print("Loading data on startup...")
    load_data_on_startup()
    print("Data loaded successfully!")
    yield
    print("Shutting down...")


# Initialize FastAPI with metadata for Swagger UI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration - allow all origins for demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Dashboard route
@app.get("/dashboard")
async def dashboard():
    """Serve the data dashboard for demos."""
    dashboard_file = static_path / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file, media_type="text/html")
    return {"error": "Dashboard not found"}

# Voice demo route
@app.get("/voice")
async def voice_demo():
    """Serve the voice interaction demo."""
    voice_file = static_path / "voice-demo.html"
    if voice_file.exists():
        return FileResponse(voice_file, media_type="text/html")
    return {"error": "Voice demo not found"}

# Register routers
app.include_router(health_router)
app.include_router(identity_router)
app.include_router(appointments_router)
app.include_router(admin_router)
