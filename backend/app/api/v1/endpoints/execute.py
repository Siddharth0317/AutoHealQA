import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from executor.playwright_runner import PlaywrightTestExecutor, TestRunResult
from backend.app.models.schemas import ExecuteTestRequest
from backend.app.core.supabase import supabase_service
from backend.app.core.auth import get_current_user, UserContext
from backend.app.core.metrics import metrics_collector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/execute-tests", response_model=TestRunResult, status_code=status.HTTP_200_OK)
async def execute_tests(
    payload: ExecuteTestRequest,
    current_user: UserContext = Depends(get_current_user)
) -> TestRunResult:
    """
    Triggers async Playwright test execution engine against target application.
    Auto-heals failing selectors and returns real-time execution logs and screenshots.
    """
    start_time = time.time()
    try:
        executor = PlaywrightTestExecutor(headless=payload.headless)

        run_result: TestRunResult = await executor.execute_test_suite(
            test_suite=payload.test_suite,
            base_url_override=payload.target_url_override
        )

        # Save run result in database
        await supabase_service.save_test_run(run_result.model_dump(), user_id=current_user.user_id)

        # Record system metrics
        metrics_collector.record_execution(
            steps=run_result.total_steps,
            healed=run_result.steps_healed,
            duration_ms=run_result.duration_ms
        )

        duration = int((time.time() - start_time) * 1000)
        metrics_collector.record_api_call(
            endpoint="/api/v1/execute-tests",
            method="POST",
            status_code=200,
            duration_ms=duration,
            role=current_user.role
        )

        return run_result
    except Exception as e:
        logger.error(f"Error executing test suite: {e}")
        duration = int((time.time() - start_time) * 1000)
        metrics_collector.record_api_call(
            endpoint="/api/v1/execute-tests",
            method="POST",
            status_code=500,
            duration_ms=duration,
            role=current_user.role
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution failed: {str(e)}"
        )
