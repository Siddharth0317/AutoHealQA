import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.core.supabase import supabase_service
from backend.app.core.auth import get_current_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/test-runs/{run_id}", status_code=status.HTTP_200_OK)
async def get_test_run(
    run_id: str,
    current_user: UserContext = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieves complete execution details, logs, screenshots, trace URLs, and self-healing logs for a run.
    """
    run_record = await supabase_service.get_test_run_by_id(run_id)
    if not run_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test run with ID '{run_id}' not found."
        )
    return run_record
