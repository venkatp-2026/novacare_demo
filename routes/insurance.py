"""Insurance verification endpoints"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from ..config import MOCK_API_TOKEN
from ..data import get_data_manager


router = APIRouter(prefix="/v1/insurance", tags=["Insurance"])


class InsuranceVerificationRequest(BaseModel):
    """Request model for insurance verification"""
    patient_id: str


class InsuranceVerificationResponse(BaseModel):
    """Response model for insurance verification"""
    patient_id: str
    verified: bool
    status: str  # active, expired, pending
    plan_name: str
    member_id: str
    coverage_percentage: int
    copay: float
    deductible_remaining: float
    effective_date: str
    expiration_date: str
    requires_referral: bool
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


@router.post("/verify-coverage", response_model=InsuranceVerificationResponse)
async def verify_insurance_coverage(
    request: InsuranceVerificationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Verify insurance coverage for a patient

    Returns current insurance status, plan details, copay, and deductible information
    """
    # Verify authentication
    verify_bearer_token(authorization)

    # Get data manager
    dm = get_data_manager()

    # Check if patient exists
    if request.patient_id not in dm.patients:
        raise HTTPException(status_code=404, detail=f"Patient {request.patient_id} not found")

    patient = dm.patients[request.patient_id]

    # Mock insurance data based on patient's insurance plan
    insurance_data = {
        "Blue Cross PPO": {
            "status": "active",
            "coverage_percentage": 80,
            "copay": 25.00,
            "deductible_remaining": 1500.00,
            "requires_referral": False
        },
        "Aetna HMO": {
            "status": "active",
            "coverage_percentage": 90,
            "copay": 15.00,
            "deductible_remaining": 500.00,
            "requires_referral": True
        },
        "Cigna PPO": {
            "status": "active",
            "coverage_percentage": 75,
            "copay": 30.00,
            "deductible_remaining": 2000.00,
            "requires_referral": False
        },
        "United Healthcare": {
            "status": "active",
            "coverage_percentage": 85,
            "copay": 20.00,
            "deductible_remaining": 1200.00,
            "requires_referral": False
        },
        "Kaiser Permanente": {
            "status": "active",
            "coverage_percentage": 100,
            "copay": 10.00,
            "deductible_remaining": 0.00,
            "requires_referral": True
        }
    }

    plan_name = patient.get("insurance_plan", "Unknown")
    plan_details = insurance_data.get(plan_name, {
        "status": "pending",
        "coverage_percentage": 0,
        "copay": 0.00,
        "deductible_remaining": 0.00,
        "requires_referral": False
    })

    # Calculate dates
    current_year = datetime.now().year
    effective_date = f"{current_year}-01-01"
    expiration_date = f"{current_year}-12-31"

    return InsuranceVerificationResponse(
        patient_id=request.patient_id,
        verified=plan_details["status"] == "active",
        status=plan_details["status"],
        plan_name=plan_name,
        member_id=patient.get("insurance_member_id", "N/A"),
        coverage_percentage=plan_details["coverage_percentage"],
        copay=plan_details["copay"],
        deductible_remaining=plan_details["deductible_remaining"],
        effective_date=effective_date,
        expiration_date=expiration_date,
        requires_referral=plan_details["requires_referral"],
        message=f"Insurance verified: {plan_name} is active with {plan_details['coverage_percentage']}% coverage"
    )
