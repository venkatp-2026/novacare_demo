"""API route modules."""
from .identity import router as identity_router
from .appointments import router as appointments_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    "identity_router",
    "appointments_router",
    "admin_router",
    "health_router"
]
