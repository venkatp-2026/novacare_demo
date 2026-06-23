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


class TomorrowAppointment(BaseModel):
    """Tomorrow's appointment details for reminders"""
    appointment_id: str = Field(..., example="APT-100")
    patient_id: str = Field(..., example="PAT-001")
    patient_name: str = Field(..., example="Jane Smith")
    patient_email: str = Field(..., example="jane.smith@email.com")
    date: str = Field(..., example="2026-06-25")
    time: str = Field(..., example="11:00 AM")
    provider: str = Field(..., example="Dr. Williams")
    location: str = Field(..., example="Main Campus - Room 204")
    type: str = Field(..., example="Routine Check-up")


class DoctorLookupRequest(BaseModel):
    """Request model for doctor lookup by name and DOB"""
    name: str = Field(..., example="Dr. Sarah Williams", description="Doctor's full name")
    dob: str = Field(..., example="1978-04-15", description="Date of birth in YYYY-MM-DD format")


class DoctorLookupResponse(BaseModel):
    """Response model for doctor lookup"""
    found: bool
    doctor_id: Optional[str] = None
    name: Optional[str] = None
    specialty: Optional[str] = None
    languages: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    npi: Optional[str] = None
    license: Optional[str] = None
    location: Optional[str] = None
    message: Optional[str] = None


class DoctorAppointment(BaseModel):
    """Doctor's appointment details"""
    appointment_id: str = Field(..., example="APT-101")
    doctor_id: str = Field(..., example="DOC-001")
    patient_id: str = Field(..., example="PAT-001")
    patient_name: str = Field(..., example="Jane Smith")
    date: str = Field(..., example="2026-06-20")
    time: str = Field(..., example="10:00 AM")
    type: str = Field(..., example="Follow-up")
    location: str = Field(..., example="Main Campus - Room 204")
    status: str = Field(..., example="confirmed")


class CancelAppointmentsRequest(BaseModel):
    """Request to cancel doctor's appointments in a date range"""
    from_date: str = Field(..., example="2026-06-20", description="Start date (YYYY-MM-DD)")
    to_date: str = Field(..., example="2026-06-30", description="End date (YYYY-MM-DD)")


class CancelAppointmentsResponse(BaseModel):
    """Response for appointment cancellation"""
    success: bool
    cancelled_count: int
    message: str
