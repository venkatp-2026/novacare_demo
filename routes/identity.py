"""Identity verification endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from models import IdentityVerificationRequest, IdentityVerificationResponse
from utils import verify_token, log_event
from data import get_data_manager
import logging

logger = logging.getLogger("novacare_api")
router = APIRouter(prefix="/v1", tags=["Identity"])


@router.post("/verify-identity", response_model=IdentityVerificationResponse)
def verify_patient_identity(
    request: IdentityVerificationRequest,
    token: str = Depends(verify_token)
):
    """
    Verify patient identity using patient_id and date of birth.
    Returns verified=true if DOB matches, verified=false otherwise.
    """
    logger.info(f"🔐 Identity Verification Request - Patient: {request.patient_id}, DOB: {request.dob}")

    dm = get_data_manager()
    patient_id = request.patient_id
    dob = request.dob

    # Log the verification attempt
    log_event(
        event="identity_verification",
        patient_id=patient_id,
        endpoint="/v1/verify-identity"
    )
    
    # Check if patient exists
    if patient_id not in dm.patients:
        logger.error(f"❌ Patient {patient_id} not found in system")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found in system"
        )

    patient = dm.patients[patient_id]

    # Verify DOB matches
    if patient["dob"] != dob:
        logger.warning(f"⚠️ DOB mismatch for {patient_id}. Expected: {patient['dob']}, Got: {dob}")
        return IdentityVerificationResponse(
            verified=False,
            message="Date of birth does not match our records"
        )

    logger.info(f"✅ Identity verified successfully for {patient_id} - {patient['name']}")
    return IdentityVerificationResponse(
        verified=True,
        patient_name=patient["name"],
        message="Identity verified successfully"
    )
