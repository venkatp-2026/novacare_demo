"""
NovaCare Health - Epic EHR Mock API
Simulates patient records, appointments, and scheduling for Zendesk FDE assessment.
Features Excel-based data storage with default and working copies for demo resets.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from config import API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_ORIGINS, MOCK_API_TOKEN
from data import load_data_on_startup
from routes import (
    health_router,
    identity_router,
    appointments_router,
    admin_router,
    patients_router,
    insurance_router,
    appointment_confirmation_router
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

# Configuration endpoint - serves API token to frontend
@app.get("/api/config")
async def get_config():
    """
    Provide frontend configuration including API token.
    This endpoint is public as it's needed for client authentication.
    """
    return JSONResponse({
        "apiToken": MOCK_API_TOKEN,
        "apiBaseUrl": "/v1",
        "environment": "production"
    })

# Register routers
app.include_router(health_router)
app.include_router(identity_router)
app.include_router(appointments_router)
app.include_router(admin_router)
app.include_router(patients_router)
app.include_router(insurance_router)
app.include_router(appointment_confirmation_router)

# Mount static files (must be last so API routes take precedence)
static_path = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
