"""Patient lookup endpoints - Name + DOB based search"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import re

from config import MOCK_API_TOKEN
from data import get_data_manager

import logging

logger = logging.getLogger("novacare_api")

router = APIRouter(prefix="/v1/patients", tags=["Patients"])


class PatientLookupRequest(BaseModel):
    """Request model for patient lookup by name and DOB"""
    name: str
    dob: str  # Can be MM/DD/YYYY or Month Day, Year or YYYY-MM-DD


class PatientLookupResponse(BaseModel):
    """Response model for patient lookup"""
    found: bool
    patient_id: Optional[str] = None
    name: Optional[str] = None
    multiple_matches: bool = False
    message: Optional[str] = None


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse various date formats to ISO format (YYYY-MM-DD)
    Accepts:
    - MM/DD/YYYY (e.g., 03/15/1985 or 3/15/1985)
    - Month Day, Year (e.g., March 15, 1985)
    - YYYY-MM-DD (e.g., 1985-03-15)
    """
    date_str = date_str.strip()

    # Try ISO format first (YYYY-MM-DD)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # Try MM/DD/YYYY or M/D/YYYY
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if match:
        month, day, year = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Try Month Day, Year (e.g., March 15, 1985)
    try:
        # Handle various formats with month names
        for fmt in ["%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
    except Exception:
        pass

    return None


def normalize_name(name: str) -> str:
    """Normalize name for comparison (lowercase, remove extra spaces, remove punctuation)"""
    # Remove punctuation, convert to lowercase, normalize spaces
    name = re.sub(r'[^\w\s]', '', name.lower())
    name = ' '.join(name.split())  # Normalize whitespace
    return name


def names_match(input_name: str, patient_name: str) -> bool:
    """
    Check if names match with flexible matching:
    - Exact match after normalization
    - First name + Last name match (ignore middle names/initials)
    """
    input_norm = normalize_name(input_name)
    patient_norm = normalize_name(patient_name)

    # Exact match
    if input_norm == patient_norm:
        return True

    # First + Last name match (ignore middle)
    input_parts = input_norm.split()
    patient_parts = patient_norm.split()

    if len(input_parts) >= 2 and len(patient_parts) >= 2:
        # Match first and last name
        input_first, input_last = input_parts[0], input_parts[-1]
        patient_first, patient_last = patient_parts[0], patient_parts[-1]

        if input_first == patient_first and input_last == patient_last:
            return True

    return False


def verify_bearer_token(authorization: Optional[str] = Header(None)):
    """Verify the Bearer token from the Authorization header."""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer <token>")

    token = authorization.replace("Bearer ", "")
    if token != MOCK_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")


@router.post("/lookup", response_model=PatientLookupResponse)
async def lookup_patient(
    request: PatientLookupRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Look up patient by name and date of birth

    Returns patient_id if exactly one match found
    Returns multiple_matches: true if multiple patients match
    Returns found: false if no matches

    Name matching is flexible (handles middle names, punctuation)
    DOB matching is strict (must be exact date match)
    """
    # Verify authentication
    verify_bearer_token(authorization)

    # Parse DOB to standard format
    parsed_dob = parse_date(request.dob)
    if not parsed_dob:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Please use MM/DD/YYYY, Month Day Year, or YYYY-MM-DD. You provided: {request.dob}"
        )

    # Get data manager
    dm = get_data_manager()

    # Search for matching patients
    matches = []
    for patient_id, patient_data in dm.patients.items():
        # DOB must match exactly
        if patient_data.get("dob") != parsed_dob:
            continue

        # Name must match (flexible)
        if names_match(request.name, patient_data.get("name", "")):
            matches.append({
                "patient_id": patient_id,
                "name": patient_data.get("name"),
                "dob": patient_data.get("dob"),
                "email": patient_data.get("email")
            })

    # Handle results
    if len(matches) == 0:
        return PatientLookupResponse(
            found=False,
            multiple_matches=False,
            message=f"No patient found with name '{request.name}' and date of birth {parsed_dob}"
        )

    elif len(matches) == 1:
        return PatientLookupResponse(
            found=True,
            patient_id=matches[0]["patient_id"],
            name=matches[0]["name"],
            multiple_matches=False,
            message=f"Patient found: {matches[0]['name']} ({matches[0]['patient_id']})"
        )

    else:
        # Multiple matches - security concern, must escalate
        return PatientLookupResponse(
            found=True,
            patient_id=None,
            multiple_matches=True,
            message=f"Multiple patients found with name '{request.name}' and date of birth {parsed_dob}. Additional verification required."
        )


@router.get("/{patient_id}")
async def get_patient(
    patient_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get patient details by patient ID"""
    verify_bearer_token(authorization)

    dm = get_data_manager()

    if patient_id not in dm.patients:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    return dm.patients[patient_id]
