"""Appointment management endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from models import Appointment, AppointmentSlot, RescheduleRequest, RescheduleResponse
from utils import verify_token, log_event
from data import get_data_manager, save_working_data
import logging

logger = logging.getLogger("novacare_api")
router = APIRouter(prefix="/v1", tags=["Appointments"])


@router.get("/patients/{patient_id}/appointments", response_model=List[Appointment])
def get_patient_appointments(
    patient_id: str,
    token: str = Depends(verify_token)
):
    """
    Retrieve all appointments for a given patient.
    Returns upcoming and confirmed appointments only.
    """
    logger.info(f"📅 Get Appointments Request - Patient: {patient_id}")

    dm = get_data_manager()

    # Log the access
    log_event(
        event="appointments_accessed",
        patient_id=patient_id,
        endpoint=f"/v1/patients/{patient_id}/appointments"
    )

    # Check if patient exists
    if patient_id not in dm.patients:
        logger.error(f"❌ Patient {patient_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )

    # Return appointments (empty list if none)
    appointments = dm.appointments.get(patient_id, [])
    logger.info(f"✅ Found {len(appointments)} appointments for {patient_id}")
    return appointments


@router.get("/appointments/available-slots", response_model=List[AppointmentSlot])
def get_available_slots(
    from_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    time_of_day: Optional[str] = Query(None, description="Filter by time of day: morning (6am-12pm), afternoon (12pm-5pm), evening (5pm-9pm)"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    token: str = Depends(verify_token)
):
    """
    Retrieve available appointment slots.
    Optionally filter by date range, time of day, and provider.

    Time of day options:
    - morning: 6:00 AM - 12:00 PM
    - afternoon: 12:00 PM - 5:00 PM
    - evening: 5:00 PM - 9:00 PM
    """
    logger.info(f"🕐 Get Available Slots - Filters: from={from_date}, to={to_date}, time={time_of_day}, provider={provider}")

    dm = get_data_manager()

    # Log the request
    log_event(
        event="slots_queried",
        endpoint="/v1/appointments/available-slots",
        filters={"from": from_date, "to": to_date, "time_of_day": time_of_day, "provider": provider}
    )

    # Filter available slots
    slots = [slot for slot in dm.slots.values() if slot["available"]]
    logger.info(f"Found {len(slots)} available slots before filtering")

    # Apply date filters if provided
    if from_date:
        slots = [s for s in slots if s["date"] >= from_date]
    if to_date:
        slots = [s for s in slots if s["date"] <= to_date]

    # Apply time of day filter if provided
    if time_of_day:
        def matches_time_of_day(slot_time: str, period: str) -> bool:
            """Check if slot time matches the requested time of day period."""
            # Parse time like "2:00 PM" or "9:30 AM"
            time_str = slot_time.strip().upper()

            # Extract hour
            try:
                time_part = time_str.split(':')[0]
                hour = int(time_part)

                # Adjust for PM (except 12 PM)
                if 'PM' in time_str and hour != 12:
                    hour += 12
                # Adjust for 12 AM (midnight)
                elif 'AM' in time_str and hour == 12:
                    hour = 0

                # Check against time periods
                if period.lower() == 'morning':
                    return 6 <= hour < 12
                elif period.lower() == 'afternoon':
                    return 12 <= hour < 17  # 12pm - 5pm
                elif period.lower() == 'evening':
                    return 17 <= hour < 21  # 5pm - 9pm
                else:
                    return True  # Unknown period, include all

            except (ValueError, IndexError):
                return True  # Can't parse, include by default

        slots = [s for s in slots if matches_time_of_day(s["time"], time_of_day)]

    # Apply provider filter if provided
    if provider:
        slots = [s for s in slots if provider.lower() in s["provider"].lower()]

    # Sort by date and time
    slots.sort(key=lambda x: (x["date"], x["time"]))

    logger.info(f"✅ Returning {len(slots)} slots after filtering")
    return slots


@router.put("/appointments/{appointment_id}", response_model=RescheduleResponse)
def reschedule_appointment(
    appointment_id: str,
    request: RescheduleRequest,
    token: str = Depends(verify_token)
):
    """
    Reschedule an existing appointment to a new date and time.

    SIMPLIFIED FOR DEMO: No slot_id needed! Just provide:
    - new_date (YYYY-MM-DD format)
    - new_time (e.g., "2:00 PM")
    - provider (optional, keeps current provider if not specified)

    The appointment will be updated and displayed in the dashboard.
    """
    logger.info(f"🔄 Reschedule Request - Appointment: {appointment_id}, New: {request.new_date} {request.new_time}")

    dm = get_data_manager()

    # Find the appointment across all patients
    appointment = None
    patient_id = None
    for pid, appts in dm.appointments.items():
        for appt in appts:
            if appt["appointment_id"] == appointment_id:
                appointment = appt
                patient_id = pid
                break
        if appointment:
            break

    if not appointment:
        logger.error(f"❌ Appointment {appointment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )

    # Store old values for logging
    old_date = appointment["date"]
    old_time = appointment["time"]
    old_provider = appointment["provider"]

    # Update appointment with new values
    appointment["date"] = request.new_date
    appointment["time"] = request.new_time

    # Update provider if specified, otherwise keep current
    if request.provider:
        appointment["provider"] = request.provider
        logger.info(f"📍 Provider changed from {old_provider} to {request.provider}")
    else:
        logger.info(f"📍 Keeping current provider: {old_provider}")

    appointment["status"] = "confirmed"

    # Save changes to Excel
    save_working_data()

    # Log the reschedule
    log_event(
        event="appointment_rescheduled",
        patient_id=patient_id,
        appointment_id=appointment_id,
        endpoint=f"/v1/appointments/{appointment_id}",
        changes={
            "old": f"{old_date} {old_time}",
            "new": f"{request.new_date} {request.new_time}",
            "reason": request.reason
        }
    )

    logger.info(f"✅ Appointment {appointment_id} rescheduled: {old_date} {old_time} → {request.new_date} {request.new_time}")

    return RescheduleResponse(
        success=True,
        appointment=Appointment(**appointment),
        message=f"Appointment rescheduled from {old_date} {old_time} to {request.new_date} {request.new_time}"
    )
