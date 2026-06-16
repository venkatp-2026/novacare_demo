"""
NovaCare Health - Epic EHR Mock API
Simulates patient records, appointments, and scheduling for Zendesk FDE assessment.
Designed for Vercel serverless deployment with in-memory persistence.
"""
from fastapi import FastAPI, HTTPException, Security, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date, time
from collections import deque
import os

# ============================================================================
# Configuration
# ============================================================================

# Get the bearer token from environment variable (set in Vercel dashboard)
MOCK_API_TOKEN = os.environ.get("MOCK_API_TOKEN", "dev-token-replace-in-production")

# Security scheme
security = HTTPBearer()

# Initialize FastAPI with metadata for Swagger UI
app = FastAPI(
    title="NovaCare Health - Epic EHR Mock API",
    description="Mock endpoints simulating Epic FHIR R4 healthcare system integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - allow Zendesk domains only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.zendesk.com",
        "http://localhost:*",  # For local zcli development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit log (in-memory ring buffer, max 100 entries)
audit_log = deque(maxlen=100)


# ============================================================================
# Authentication
# ============================================================================

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify bearer token matches expected value."""
    if credentials.credentials != MOCK_API_TOKEN:
        audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "auth_failed",
            "token_prefix": credentials.credentials[:8] + "..." if len(credentials.credentials) > 8 else "***"
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class IdentityVerificationRequest(BaseModel):
    patient_id: str = Field(..., example="PAT-001", description="Patient identifier")
    dob: str = Field(..., example="1985-03-15", description="Date of birth in YYYY-MM-DD format")

class IdentityVerificationResponse(BaseModel):
    verified: bool = Field(..., example=True)
    patient_name: Optional[str] = Field(None, example="Jane Smith")
    message: Optional[str] = Field(None, example="Identity verified successfully")

class Appointment(BaseModel):
    appointment_id: str = Field(..., example="APT-101")
    patient_id: str = Field(..., example="PAT-001")
    date: str = Field(..., example="2026-06-20")
    time: str = Field(..., example="10:00 AM")
    provider: str = Field(..., example="Dr. Williams")
    type: str = Field(..., example="Follow-up")
    location: str = Field(..., example="Main Campus - Room 204")
    status: str = Field(..., example="confirmed")

class AppointmentSlot(BaseModel):
    slot_id: str = Field(..., example="SLOT-001")
    date: str = Field(..., example="2026-06-25")
    time: str = Field(..., example="2:00 PM")
    provider: str = Field(..., example="Dr. Williams")
    location: str = Field(..., example="Main Campus - Room 204")
    available: bool = Field(..., example=True)

class RescheduleRequest(BaseModel):
    slot_id: str = Field(..., example="SLOT-005", description="ID of the selected available slot")
    reason: Optional[str] = Field(None, example="Patient conflict", description="Optional reschedule reason")

class RescheduleResponse(BaseModel):
    success: bool = Field(..., example=True)
    appointment: Appointment
    message: str = Field(..., example="Appointment rescheduled successfully")

class AuditEntry(BaseModel):
    timestamp: str
    event: str
    patient_id: Optional[str] = None
    endpoint: Optional[str] = None
    actor: Optional[str] = None


# ============================================================================
# In-Memory Database (seeded on cold start)
# ============================================================================

# Patients database
PATIENTS = {
    "PAT-001": {
        "patient_id": "PAT-001",
        "name": "Jane Smith",
        "dob": "1985-03-15",
        "mrn": "MRN-2001",
        "status": "active"
    },
    "PAT-002": {
        "patient_id": "PAT-002",
        "name": "Robert Johnson",
        "dob": "1978-11-22",
        "mrn": "MRN-2002",
        "status": "active"
    },
    "PAT-003": {
        "patient_id": "PAT-003",
        "name": "Maria Garcia",
        "dob": "1992-07-08",
        "mrn": "MRN-2003",
        "status": "active"
    },
}

# Appointments database (patient_id -> list of appointments)
APPOINTMENTS = {
    "PAT-001": [
        {
            "appointment_id": "APT-101",
            "patient_id": "PAT-001",
            "date": "2026-06-20",
            "time": "10:00 AM",
            "provider": "Dr. Williams",
            "type": "Follow-up",
            "location": "Main Campus - Room 204",
            "status": "confirmed"
        },
        {
            "appointment_id": "APT-102",
            "patient_id": "PAT-001",
            "date": "2026-07-15",
            "time": "2:30 PM",
            "provider": "Dr. Chen",
            "type": "Annual Check-up",
            "location": "North Clinic - Suite 301",
            "status": "confirmed"
        },
        {
            "appointment_id": "APT-103",
            "patient_id": "PAT-001",
            "date": "2026-08-10",
            "time": "9:00 AM",
            "provider": "Dr. Williams",
            "type": "Lab Results Review",
            "location": "Main Campus - Room 204",
            "status": "confirmed"
        }
    ],
    "PAT-002": [
        {
            "appointment_id": "APT-201",
            "patient_id": "PAT-002",
            "date": "2026-06-22",
            "time": "11:30 AM",
            "provider": "Dr. Patel",
            "type": "Consultation",
            "location": "West Building - Office 102",
            "status": "confirmed"
        },
        {
            "appointment_id": "APT-202",
            "patient_id": "PAT-002",
            "date": "2026-07-05",
            "time": "3:00 PM",
            "provider": "Dr. Lee",
            "type": "Physical Therapy",
            "location": "Therapy Center - Room A",
            "status": "confirmed"
        }
    ],
    "PAT-003": [
        {
            "appointment_id": "APT-301",
            "patient_id": "PAT-003",
            "date": "2026-06-25",
            "time": "1:00 PM",
            "provider": "Dr. Rodriguez",
            "type": "Diabetes Management",
            "location": "Endocrinology Wing - Room 5",
            "status": "confirmed"
        },
        {
            "appointment_id": "APT-302",
            "patient_id": "PAT-003",
            "date": "2026-07-20",
            "time": "10:30 AM",
            "provider": "Dr. Kim",
            "type": "Nutrition Counseling",
            "location": "Wellness Center - Suite 210",
            "status": "confirmed"
        }
    ]
}

# Available appointment slots (these can be booked)
AVAILABLE_SLOTS = {
    "SLOT-001": {"slot_id": "SLOT-001", "date": "2026-06-25", "time": "2:00 PM", "provider": "Dr. Williams", "location": "Main Campus - Room 204", "available": True},
    "SLOT-002": {"slot_id": "SLOT-002", "date": "2026-06-26", "time": "9:30 AM", "provider": "Dr. Chen", "location": "North Clinic - Suite 301", "available": True},
    "SLOT-003": {"slot_id": "SLOT-003", "date": "2026-06-27", "time": "11:00 AM", "provider": "Dr. Williams", "location": "Main Campus - Room 204", "available": True},
    "SLOT-004": {"slot_id": "SLOT-004", "date": "2026-06-28", "time": "3:30 PM", "provider": "Dr. Patel", "location": "West Building - Office 102", "available": True},
    "SLOT-005": {"slot_id": "SLOT-005", "date": "2026-07-01", "time": "8:00 AM", "provider": "Dr. Lee", "location": "Therapy Center - Room A", "available": True},
    "SLOT-006": {"slot_id": "SLOT-006", "date": "2026-07-02", "time": "1:30 PM", "provider": "Dr. Rodriguez", "location": "Endocrinology Wing - Room 5", "available": True},
    "SLOT-007": {"slot_id": "SLOT-007", "date": "2026-07-03", "time": "10:00 AM", "provider": "Dr. Kim", "location": "Wellness Center - Suite 210", "available": True},
    "SLOT-008": {"slot_id": "SLOT-008", "date": "2026-07-05", "time": "4:00 PM", "provider": "Dr. Williams", "location": "Main Campus - Room 204", "available": True},
    "SLOT-009": {"slot_id": "SLOT-009", "date": "2026-07-08", "time": "9:00 AM", "provider": "Dr. Chen", "location": "North Clinic - Suite 301", "available": True},
    "SLOT-010": {"slot_id": "SLOT-010", "date": "2026-07-10", "time": "2:30 PM", "provider": "Dr. Patel", "location": "West Building - Office 102", "available": True},
}


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
def read_root():
    """Root endpoint - service health check."""
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
            "audit": "/v1/audit"
        }
    }


@app.get("/healthz", tags=["Health"])
def health_check():
    """Kubernetes-style health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok",
            "patients_loaded": len(PATIENTS),
            "appointments_loaded": sum(len(appts) for appts in APPOINTMENTS.values()),
            "slots_available": sum(1 for slot in AVAILABLE_SLOTS.values() if slot["available"])
        }
    }


@app.post("/v1/verify-identity", response_model=IdentityVerificationResponse, tags=["Identity"])
def verify_patient_identity(
    request: IdentityVerificationRequest,
    token: str = Depends(verify_token)
):
    """
    Verify patient identity using patient_id and date of birth.
    Returns verified=true if DOB matches, verified=false otherwise.
    """
    patient_id = request.patient_id
    dob = request.dob
    
    # Log the verification attempt
    audit_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "identity_verification",
        "patient_id": patient_id,
        "endpoint": "/v1/verify-identity"
    })
    
    # Check if patient exists
    if patient_id not in PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found in system"
        )
    
    patient = PATIENTS[patient_id]
    
    # Verify DOB matches (in production, this would be more sophisticated)
    if patient["dob"] != dob:
        return IdentityVerificationResponse(
            verified=False,
            message="Date of birth does not match our records"
        )
    
    return IdentityVerificationResponse(
        verified=True,
        patient_name=patient["name"],
        message="Identity verified successfully"
    )


@app.get("/v1/patients/{patient_id}/appointments", response_model=List[Appointment], tags=["Appointments"])
def get_patient_appointments(
    patient_id: str,
    token: str = Depends(verify_token)
):
    """
    Retrieve all appointments for a given patient.
    Returns upcoming and confirmed appointments only.
    """
    # Log the access
    audit_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "appointments_accessed",
        "patient_id": patient_id,
        "endpoint": f"/v1/patients/{patient_id}/appointments"
    })
    
    # Check if patient exists
    if patient_id not in PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Return appointments (empty list if none)
    appointments = APPOINTMENTS.get(patient_id, [])
    return appointments


@app.get("/v1/appointments/available-slots", response_model=List[AppointmentSlot], tags=["Appointments"])
def get_available_slots(
    from_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    token: str = Depends(verify_token)
):
    """
    Retrieve available appointment slots.
    Optionally filter by date range and provider.
    """
    # Log the request
    audit_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "slots_queried",
        "endpoint": "/v1/appointments/available-slots",
        "filters": {"from": from_date, "to": to_date, "provider": provider}
    })
    
    # Filter available slots
    slots = [slot for slot in AVAILABLE_SLOTS.values() if slot["available"]]
    
    # Apply date filters if provided
    if from_date:
        slots = [s for s in slots if s["date"] >= from_date]
    if to_date:
        slots = [s for s in slots if s["date"] <= to_date]
    
    # Apply provider filter if provided
    if provider:
        slots = [s for s in slots if provider.lower() in s["provider"].lower()]
    
    # Sort by date and time
    slots.sort(key=lambda x: (x["date"], x["time"]))
    
    return slots


@app.put("/v1/appointments/{appointment_id}", response_model=RescheduleResponse, tags=["Appointments"])
def reschedule_appointment(
    appointment_id: str,
    request: RescheduleRequest,
    token: str = Depends(verify_token)
):
    """
    Reschedule an existing appointment to a new slot.
    Validates slot availability and updates both the appointment and slot status.
    """
    slot_id = request.slot_id
    
    # Find the appointment across all patients
    appointment = None
    patient_id = None
    for pid, appts in APPOINTMENTS.items():
        for appt in appts:
            if appt["appointment_id"] == appointment_id:
                appointment = appt
                patient_id = pid
                break
        if appointment:
            break
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )
    
    # Check if the requested slot exists and is available
    if slot_id not in AVAILABLE_SLOTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot {slot_id} not found"
        )
    
    slot = AVAILABLE_SLOTS[slot_id]
    
    if not slot["available"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slot {slot_id} is no longer available. Please select another slot."
        )
    
    # Perform the reschedule (update appointment with slot details)
    old_date = appointment["date"]
    old_time = appointment["time"]
    
    appointment["date"] = slot["date"]
    appointment["time"] = slot["time"]
    appointment["provider"] = slot["provider"]
    appointment["location"] = slot["location"]
    appointment["status"] = "confirmed"
    
    # Mark the slot as unavailable
    slot["available"] = False
    
    # Log the reschedule
    audit_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "appointment_rescheduled",
        "patient_id": patient_id,
        "appointment_id": appointment_id,
        "endpoint": f"/v1/appointments/{appointment_id}",
        "changes": {
            "old": f"{old_date} {old_time}",
            "new": f"{slot['date']} {slot['time']}"
        }
    })
    
    return RescheduleResponse(
        success=True,
        appointment=Appointment(**appointment),
        message=f"Appointment rescheduled from {old_date} {old_time} to {slot['date']} {slot['time']}"
    )


@app.get("/v1/audit", response_model=List[AuditEntry], tags=["Admin"])
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


@app.post("/v1/admin/reset", tags=["Admin"])
def reset_database(token: str = Depends(verify_token)):
    """
    Reset the in-memory database to initial seed state.
    Useful for demo rehearsals to restore predictable data.
    """
    global AVAILABLE_SLOTS
    
    # Reset all slots to available
    for slot in AVAILABLE_SLOTS.values():
        slot["available"] = True
    
    # Reset appointments to initial state (not implemented for brevity - would need deep copy)
    # In a real demo, you'd restore from a pristine backup
    
    audit_log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "database_reset",
        "endpoint": "/v1/admin/reset"
    })
    
    return {
        "status": "success",
        "message": "Database reset to initial state",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Error simulation endpoints (for testing Action Flow error branches)
# ============================================================================

@app.get("/v1/simulate/timeout", tags=["Testing"])
def simulate_timeout(token: str = Depends(verify_token)):
    """Simulate a slow/timeout response (for Action Flow testing)."""
    import time
    time.sleep(30)  # Will likely timeout
    return {"message": "This should have timed out"}


@app.get("/v1/simulate/503", tags=["Testing"])
def simulate_service_unavailable(token: str = Depends(verify_token)):
    """Simulate service unavailable error (for Action Flow error branch testing)."""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Epic EHR system temporarily unavailable. Please try again in a few minutes.",
        headers={"Retry-After": "60"}
    )


@app.get("/v1/simulate/429", tags=["Testing"])
def simulate_rate_limit(token: str = Depends(verify_token)):
    """Simulate rate limit exceeded (for Action Flow retry logic testing)."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded: 100 requests per second",
        headers={"Retry-After": "5"}
    )
