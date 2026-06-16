"""
NovaCare Health - Epic EHR Mock API
Simulates patient records, appointments, and scheduling for Zendesk FDE assessment.
Features Excel-based data storage with default and working copies for demo resets.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Static file path
static_path = Path(__file__).parent / "static"

# Static file routes
@app.get("/")
async def root():
    """Root redirects to dashboard."""
    return FileResponse(static_path / "dashboard.html", media_type="text/html")

@app.get("/dashboard")
async def dashboard():
    """Serve dashboard."""
    return FileResponse(static_path / "dashboard.html", media_type="text/html")

@app.get("/dashboard.html")
async def dashboard_html():
    """Serve dashboard."""
    return FileResponse(static_path / "dashboard.html", media_type="text/html")

@app.get("/dashboard.js")
async def dashboard_js():
    """Serve dashboard JS."""
    return FileResponse(static_path / "dashboard.js", media_type="application/javascript")

@app.get("/dashboard.css")
async def dashboard_css():
    """Serve dashboard CSS."""
    return FileResponse(static_path / "dashboard.css", media_type="text/css")

@app.get("/voice")
async def voice():
    """Serve voice demo."""
    return FileResponse(static_path / "voice-demo.html", media_type="text/html")

# Register routers
app.include_router(health_router)
app.include_router(identity_router)
app.include_router(appointments_router)
app.include_router(admin_router)
