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
    Lists past test runs for the authenticated user (or all runs if admin).
    """
    target_user_id = None if current_user.role == "admin" else current_user.user_id
    runs = await supabase_service.get_run_history(limit=limit, user_id=target_user_id)
    healed_logs = await supabase_service.get_self_healing_logs(limit=limit)

    return {
        "total_runs": len(runs),
        "user_role": current_user.role,
        "user_id": current_user.user_id,
        "runs": runs,
        "recent_healed_logs": healed_logs
    }


@router.delete("/history/clear", status_code=status.HTTP_200_OK)
async def clear_history(
    current_user: UserContext = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clears historic runs for the current user (or all if admin).
    """
    target_user_id = None if current_user.role == "admin" else current_user.user_id
    await supabase_service.clear_history(user_id=target_user_id)
    return {"message": "Execution history successfully cleared.", "total_runs": 0}
