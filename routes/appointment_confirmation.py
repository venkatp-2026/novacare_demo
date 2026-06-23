"""Appointment confirmation endpoints for email-triggered workflows"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..config import MOCK_API_TOKEN
from ..data import get_data_manager


router = APIRouter(prefix="/v1/appointments", tags=["Appointment Confirmation"])


class AppointmentLookupRequest(BaseModel):
    """Request to lookup appointment by ID and email"""
    appointment_id: str
    patient_email: str


class CancellationPolicyResponse(BaseModel):
    """Response for cancellation policy check"""
    appointment_id: str
    hours_until_appointment: float
    within_policy: bool
    cancellation_fee: float
    policy_hours: int
    message: str


class ConfirmAppointmentResponse(BaseModel):
    """Response for appointment confirmation"""
    appointment_id: str
    confirmed: bool
    confirmation_sent: bool
    message: str


class CancelAppointmentResponse(BaseModel):
    """Response for appointment cancellation"""
    appointment_id: str
    status: str
    cancellation_fee: float
    cancelled_at: str
    message: str


def verify_bearer_token(authorization: Optional[str] = Header(None)):
    """Verify the Bearer token from the Authorization header."""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.replace("Bearer ", "")
    if token != MOCK_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")


@router.get("/lookup")
async def lookup_appointment_by_email(
    appointment_id: str,
    patient_email: str,
    authorization: Optional[str] = Header(None)
):
    """
    Look up appointment by appointment ID and patient email

    Used for low-security operations like confirming appointment reminders
    No DOB required since email verification is sufficient for non-sensitive operations
    """
    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Find the appointment across all patients
    for patient_id, appointments in dm.appointments.items():
        for appointment in appointments:
            if appointment.get("appointment_id") == appointment_id:
                # Check if patient email matches
                patient = dm.patients.get(patient_id, {})
                if patient.get("email", "").lower() == patient_email.lower():
                    # Return appointment with patient info
                    return {
                        **appointment,
                        "patient_name": patient.get("name"),
                        "patient_email": patient.get("email")
                    }

    # Not found or email doesn't match
    raise HTTPException(
        status_code=404,
        detail=f"Appointment {appointment_id} not found for email {patient_email}"
    )


@router.post("/{appointment_id}/confirm", response_model=ConfirmAppointmentResponse)
async def confirm_appointment(
    appointment_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Confirm an appointment

    Marks appointment as confirmed and sends confirmation
    """
    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Find and update the appointment
    found = False
    for patient_id, appointments in dm.appointments.items():
        for appointment in appointments:
            if appointment.get("appointment_id") == appointment_id:
                # Update status
                appointment["status"] = "confirmed"
                found = True
                break
        if found:
            break

    if not found:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")

    return ConfirmAppointmentResponse(
        appointment_id=appointment_id,
        confirmed=True,
        confirmation_sent=True,
        message=f"Appointment {appointment_id} has been confirmed"
    )


@router.get("/{appointment_id}/cancellation-policy", response_model=CancellationPolicyResponse)
async def check_cancellation_policy(
    appointment_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Check cancellation policy for an appointment

    Returns whether cancellation is within policy (24 hours notice)
    and any applicable fees
    """
    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Find the appointment
    appointment = None
    for patient_id, appointments in dm.appointments.items():
        for appt in appointments:
            if appt.get("appointment_id") == appointment_id:
                appointment = appt
                break
        if appointment:
            break

    if not appointment:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")

    # Parse appointment date/time
    appt_date_str = appointment.get("date")
    appt_time_str = appointment.get("time", "12:00 PM")

    # Mock calculation: assume appointment is 3 days from now for demo
    # In production, this would parse the actual date/time
    hours_until = 72  # 3 days

    # Policy: must cancel 24 hours in advance
    policy_hours = 24
    within_policy = hours_until >= policy_hours
    cancellation_fee = 0.00 if within_policy else 50.00

    message = "No cancellation fee applies" if within_policy else f"${cancellation_fee} cancellation fee applies (less than {policy_hours} hours notice)"

    return CancellationPolicyResponse(
        appointment_id=appointment_id,
        hours_until_appointment=hours_until,
        within_policy=within_policy,
        cancellation_fee=cancellation_fee,
        policy_hours=policy_hours,
        message=message
    )


@router.post("/{appointment_id}/cancel", response_model=CancelAppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Cancel an appointment

    Updates appointment status to cancelled
    """
    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Find and update the appointment
    found = False
    for patient_id, appointments in dm.appointments.items():
        for appointment in appointments:
            if appointment.get("appointment_id") == appointment_id:
                # Update status
                appointment["status"] = "cancelled"
                found = True
                break
        if found:
            break

    if not found:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")

    # Check cancellation policy for fee
    policy_check = await check_cancellation_policy(appointment_id, authorization)

    return CancelAppointmentResponse(
        appointment_id=appointment_id,
        status="cancelled",
        cancellation_fee=policy_check.cancellation_fee,
        cancelled_at=datetime.now().isoformat(),
        message=f"Appointment {appointment_id} has been cancelled. {policy_check.message}"
    )
