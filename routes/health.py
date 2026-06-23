"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime
from data import get_data_manager

router = APIRouter(tags=["Health"])


@router.get("/api")
def api_info():
    """API information endpoint."""
    return {
        "service": "NovaCare Health - Epic EHR Mock API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/healthz",
            "verify": "/v1/verify-identity",
            "appointments": "/v1/patients/{patient_id}/appointments",
            "slots": "/v1/appointments/available-slots",
            "reschedule": "/v1/appointments/{appointment_id}",
            "audit": "/v1/audit",
            "refresh": "/data/refresh"
        }
    }


@router.get("/healthz")
def health_check():
    """Kubernetes-style health check endpoint."""
    dm = get_data_manager()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok",
            "patients_loaded": len(dm.patients),
            "appointments_loaded": sum(len(appts) for appts in dm.appointments.values()),
            "slots_available": sum(1 for slot in dm.slots.values() if slot["available"])
        }
    }
