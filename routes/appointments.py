"""Appointment management endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from datetime import datetime, timedelta
from models import Appointment, AppointmentSlot, RescheduleRequest, RescheduleResponse, TomorrowAppointment
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
    Reschedule an existing appointment to a new slot.
    Validates slot availability and updates both the appointment and slot status.
    """
    logger.info(f"🔄 Reschedule Request - Appointment: {appointment_id}, New Slot: {request.slot_id}")

    dm = get_data_manager()
    slot_id = request.slot_id

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
    
    # Check if the requested slot exists and is available
    if slot_id not in dm.slots:
        logger.error(f"❌ Slot {slot_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot {slot_id} not found"
        )

    slot = dm.slots[slot_id]
    logger.info(f"📍 Slot found: {slot['date']} {slot['time']} with {slot['provider']}")

    if not slot["available"]:
        logger.warning(f"⚠️ Slot {slot_id} is no longer available")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slot {slot_id} is no longer available. Please select another slot."
        )
    
    # Perform the reschedule
    old_date = appointment["date"]
    old_time = appointment["time"]
    
    appointment["date"] = slot["date"]
    appointment["time"] = slot["time"]
    appointment["provider"] = slot["provider"]
    appointment["location"] = slot["location"]
    appointment["status"] = "confirmed"
    
    # Mark the slot as unavailable
    slot["available"] = False
    
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
            "new": f"{slot['date']} {slot['time']}"
        }
    )

    logger.info(f"✅ Appointment {appointment_id} rescheduled: {old_date} {old_time} → {slot['date']} {slot['time']}")

    return RescheduleResponse(
        success=True,
        appointment=Appointment(**appointment),
        message=f"Appointment rescheduled from {old_date} {old_time} to {slot['date']} {slot['time']}"
    )


@router.get("/appointments/tomorrow", response_model=List[TomorrowAppointment])
def get_tomorrow_appointments(
    token: str = Depends(verify_token)
):
    """
    Get all appointments scheduled for tomorrow (next day).

    Returns appointment details with patient information for reminder purposes:
    - Appointment ID, date, time
    - Provider name
    - Patient name and email
    - Location

    For demo: Returns appointments on 2026-06-25
    """
    logger.info("📅 Get Tomorrow's Appointments Request")

    dm = get_data_manager()

    # For demo purposes, use 2026-06-25 as "tomorrow"
    tomorrow_date = "2026-06-25"

    # Find all appointments for tomorrow
    tomorrow_appointments = []

    for patient_id, appointments in dm.appointments.items():
        patient = dm.patients.get(patient_id)
        if not patient:
            continue

        for apt in appointments:
            if apt.get("date") == tomorrow_date:
                tomorrow_appointments.append(
                    TomorrowAppointment(
                        appointment_id=apt["appointment_id"],
                        patient_id=patient_id,
                        patient_name=patient["name"],
                        patient_email=patient["email"],
                        date=apt["date"],
                        time=apt["time"],
                        provider=apt["provider"],
                        location=apt["location"],
                        type=apt["type"]
                    )
                )

    logger.info(f"✅ Found {len(tomorrow_appointments)} appointments for tomorrow ({tomorrow_date})")

    # Log the request
    log_event(
        event="tomorrow_appointments_accessed",
        endpoint="/v1/appointments/tomorrow"
    )

    return tomorrow_appointments
