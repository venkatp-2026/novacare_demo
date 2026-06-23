"""Admin and testing endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List
from datetime import datetime
from ..models import AuditEntry
from ..utils import verify_token, audit_log, log_event
from ..data import get_data_manager, save_working_data

router = APIRouter(prefix="/v1", tags=["Admin"])


@router.get("/audit", response_model=List[AuditEntry])
def get_audit_log(
    token: str = Depends(verify_token),
    limit: int = Query(50, description="Number of recent entries to return", le=100)
):
    """
    Retrieve audit log entries (HIPAA compliance requirement).
    Returns most recent entries first.
    """
    # Return last N entries in reverse chronological order
    entries = list(audit_log)[-limit:]
    entries.reverse()
    return entries


@router.post("/admin/reset")
def reset_database(token: str = Depends(verify_token)):
    """
    Reset the in-memory database to initial seed state.
    Reloads data from working copy.
    """
    dm = get_data_manager()
    
    # Reload from working copy
    dm.load_from_working_copy()
    
    log_event(
        event="database_reset",
        endpoint="/v1/admin/reset"
    )
    
    return {
        "status": "success",
        "message": "Database reloaded from working copy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/data/refresh")
def refresh_data(token: str = Depends(verify_token)):
    """
    Refresh working data from default copy.
    Resets all demo modifications back to default state.
    """
    dm = get_data_manager()
    
    try:
        dm.refresh_from_default()
        
        log_event(
            event="data_refreshed",
            endpoint="/data/refresh"
        )
        
        return {
            "status": "success",
            "message": "Working data refreshed from default copy",
            "timestamp": datetime.utcnow().isoformat(),
            "stats": {
                "patients": len(dm.patients),
                "appointments": sum(len(appts) for appts in dm.appointments.values()),
                "slots": len(dm.slots)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh data: {str(e)}"
        )


# Error simulation endpoints (for testing Action Flow error branches)
@router.get("/simulate/timeout", tags=["Testing"])
def simulate_timeout(token: str = Depends(verify_token)):
    """Simulate a slow/timeout response (for Action Flow testing)."""
    import time
    time.sleep(30)  # Will likely timeout
    return {"message": "This should have timed out"}


@router.get("/simulate/503", tags=["Testing"])
def simulate_service_unavailable(token: str = Depends(verify_token)):
    """Simulate service unavailable error (for Action Flow error branch testing)."""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Epic EHR system temporarily unavailable. Please try again in a few minutes.",
        headers={"Retry-After": "60"}
    )


@router.get("/simulate/429", tags=["Testing"])
def simulate_rate_limit(token: str = Depends(verify_token)):
    """Simulate rate limit exceeded (for Action Flow retry logic testing)."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded: 100 requests per second",
        headers={"Retry-After": "5"}
    )
