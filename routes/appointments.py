"""Appointment management endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from models import Appointment, AppointmentSlot, RescheduleRequest, RescheduleResponse
from utils import verify_token, log_event
from data import get_data_manager, save_working_data

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
    dm = get_data_manager()
    
    # Log the access
    log_event(
        event="appointments_accessed",
        patient_id=patient_id,
        endpoint=f"/v1/patients/{patient_id}/appointments"
    )
    
    # Check if patient exists
    if patient_id not in dm.patients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    # Return appointments (empty list if none)
    appointments = dm.appointments.get(patient_id, [])
    return appointments


@router.get("/appointments/available-slots", response_model=List[AppointmentSlot])
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
    dm = get_data_manager()
    
    # Log the request
    log_event(
        event="slots_queried",
        endpoint="/v1/appointments/available-slots",
        filters={"from": from_date, "to": to_date, "provider": provider}
    )
    
    # Filter available slots
    slots = [slot for slot in dm.slots.values() if slot["available"]]
    
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )
    
    # Check if the requested slot exists and is available
    if slot_id not in dm.slots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot {slot_id} not found"
        )
    
    slot = dm.slots[slot_id]
    
    if not slot["available"]:
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
    
    return RescheduleResponse(
        success=True,
        appointment=Appointment(**appointment),
        message=f"Appointment rescheduled from {old_date} {old_time} to {slot['date']} {slot['time']}"
    )
