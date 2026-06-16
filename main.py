"""
NovaCare Health - Epic EHR Mock API
Simulates patient records, appointments, and scheduling for Zendesk FDE assessment.
Features Excel-based data storage with default and working copies for demo resets.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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

# CORS configuration - allow Zendesk domains only
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(identity_router)
app.include_router(appointments_router)
app.include_router(admin_router)
