import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from backend.app.core.supabase import supabase_service
from backend.app.core.auth import get_current_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", status_code=status.HTTP_200_OK)
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserContext = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Lists past test runs and self-healing events saved in Supabase / memory store.
    """
    runs = await supabase_service.get_run_history(limit=limit)
    healed_logs = await supabase_service.get_self_healing_logs(limit=limit)

    return {
        "total_runs": len(runs),
        "user_role": current_user.role,
        "runs": runs,
        "recent_healed_logs": healed_logs
    }
