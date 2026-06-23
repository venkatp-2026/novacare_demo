"""API route modules."""
from .identity import router as identity_router
from .appointments import router as appointments_router
from .admin import router as admin_router
from .health import router as health_router
from .patients import router as patients_router
from .insurance import router as insurance_router
from .appointment_confirmation import router as appointment_confirmation_router
from .doctors import router as doctors_router

__all__ = [
    "identity_router",
    "appointments_router",
    "admin_router",
    "health_router",
    "patients_router",
    "insurance_router",
    "appointment_confirmation_router",
    "doctors_router"
]
