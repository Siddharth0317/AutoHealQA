import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.config import settings
from backend.app.core.auth import require_admin_role, UserContext
from backend.app.core.metrics import metrics_collector, SystemMetricsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


class PasscodeVerifyRequest(BaseModel):
    passcode: str = Field(..., description="Admin security passcode")


@router.post("/admin/verify-passcode", status_code=status.HTTP_200_OK)
async def verify_admin_passcode(payload: PasscodeVerifyRequest) -> Dict[str, Any]:
    """
    Verifies Admin Security Passcode.
    """
    if payload.passcode == settings.ADMIN_PASSCODE:
        return {
            "status": "authenticated",
            "message": "Admin access granted.",
            "admin_passcode": payload.passcode
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin passcode."
    )


@router.get("/admin/metrics", response_model=SystemMetricsResponse, status_code=status.HTTP_200_OK)
async def get_admin_metrics(
    admin_user: UserContext = Depends(require_admin_role)
) -> SystemMetricsResponse:
    """
    Admin-only endpoint providing system performance metrics, LLM token statistics,
    self-healing success rates, and API call logs.
    """
    logger.info(f"Admin metrics requested by: {admin_user.email}")
    return metrics_collector.get_metrics_summary()
