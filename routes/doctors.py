"""Doctor lookup and appointment management endpoints."""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from models import (
    DoctorLookupRequest,
    DoctorLookupResponse,
    DoctorAppointment,
    CancelAppointmentsRequest,
    CancelAppointmentsResponse
)
from config import MOCK_API_TOKEN
from data import get_data_manager, save_working_data
import logging

logger = logging.getLogger("novacare_api")
router = APIRouter(prefix="/v1/doctors", tags=["Doctors"])


def verify_bearer_token(authorization: Optional[str] = Header(None)):
    """Verify the Bearer token from the Authorization header."""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer <token>")

    token = authorization.replace("Bearer ", "")
    if token != MOCK_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")


@router.post("/lookup", response_model=DoctorLookupResponse)
async def lookup_doctor(
    request: DoctorLookupRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Look up doctor by full name and date of birth.

    Returns complete doctor information if match found.
    """
    logger.info(f"🩺 Doctor Lookup - Name: {request.name}, DOB: {request.dob}")

    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Search for matching doctor
    for doctor_id, doctor_data in dm.doctors.items():
        if doctor_data.get("name").lower() == request.name.lower() and doctor_data.get("dob") == request.dob:
            logger.info(f"✅ Doctor found: {doctor_data['name']} ({doctor_id})")
            return DoctorLookupResponse(
                found=True,
                doctor_id=doctor_id,
                name=doctor_data.get("name"),
                specialty=doctor_data.get("specialty"),
                languages=doctor_data.get("languages"),
                email=doctor_data.get("email"),
                phone=doctor_data.get("phone"),
                npi=doctor_data.get("npi"),
                license=doctor_data.get("license"),
                location=doctor_data.get("location"),
                message=f"Doctor found: {doctor_data['name']} ({doctor_id})"
            )

    logger.warning(f"⚠️ No doctor found: {request.name} / {request.dob}")
    return DoctorLookupResponse(
        found=False,
        message=f"No doctor found with name '{request.name}' and date of birth {request.dob}"
    )


@router.get("/{doctor_id}/appointments", response_model=List[DoctorAppointment])
async def get_doctor_appointments(
    doctor_id: str,
    from_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    authorization: Optional[str] = Header(None)
):
    """
    Get all appointments for a specific doctor with optional date range filtering.

    Query Parameters:
    - from_date: Start date (YYYY-MM-DD) - optional
    - to_date: End date (YYYY-MM-DD) - optional
    """
    logger.info(f"📅 Get Doctor Appointments - Doctor: {doctor_id}, Range: {from_date} to {to_date}")

    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Check if doctor exists
    if doctor_id not in dm.doctors:
        logger.error(f"❌ Doctor {doctor_id} not found")
        raise HTTPException(status_code=404, detail=f"Doctor {doctor_id} not found")

    # Get doctor's appointments
    appointments = dm.doctor_appointments.get(doctor_id, [])

    # Apply date filters if provided
    if from_date:
        appointments = [apt for apt in appointments if apt.get("date") >= from_date]
    if to_date:
        appointments = [apt for apt in appointments if apt.get("date") <= to_date]

    logger.info(f"✅ Found {len(appointments)} appointments for {doctor_id}")

    return [DoctorAppointment(**apt) for apt in appointments]


@router.delete("/{doctor_id}/appointments", response_model=CancelAppointmentsResponse)
async def cancel_doctor_appointments(
    doctor_id: str,
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    authorization: Optional[str] = Header(None)
):
    """
    Cancel all appointments for a doctor within a date range.

    Marks appointments as "cancelled" (does not delete them).

    Query Parameters:
    - from_date: Start date (YYYY-MM-DD) - required
    - to_date: End date (YYYY-MM-DD) - required
    """
    logger.info(f"🚫 Cancel Doctor Appointments - Doctor: {doctor_id}, Range: {from_date} to {to_date}")

    verify_bearer_token(authorization)

    dm = get_data_manager()

    # Check if doctor exists
    if doctor_id not in dm.doctors:
        logger.error(f"❌ Doctor {doctor_id} not found")
        raise HTTPException(status_code=404, detail=f"Doctor {doctor_id} not found")

    # Get doctor's appointments
    appointments = dm.doctor_appointments.get(doctor_id, [])

    # Find and cancel appointments in the date range
    cancelled_count = 0
    for apt in appointments:
        if from_date <= apt.get("date") <= to_date and apt.get("status") != "cancelled":
            apt["status"] = "cancelled"
            cancelled_count += 1
            logger.info(f"🚫 Cancelled appointment {apt['appointment_id']} on {apt['date']}")

    # Save changes
    save_working_data()

    logger.info(f"✅ Cancelled {cancelled_count} appointments for {doctor_id}")

    return CancelAppointmentsResponse(
        success=True,
        cancelled_count=cancelled_count,
        message=f"Successfully cancelled {cancelled_count} appointment(s) for {doctor_id} between {from_date} and {to_date}"
    )
