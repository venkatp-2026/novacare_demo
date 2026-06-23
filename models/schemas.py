"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional


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
    new_date: str = Field(..., example="2026-07-15", description="New appointment date (YYYY-MM-DD)")
    new_time: str = Field(..., example="2:00 PM", description="New appointment time (e.g., '2:00 PM')")
    provider: Optional[str] = Field(None, example="Dr. Williams", description="Provider name (optional, keeps current if not specified)")
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
