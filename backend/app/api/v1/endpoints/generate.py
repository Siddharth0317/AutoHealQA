import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from agents.requirements_agent import requirements_agent
from backend.app.models.schemas import GenerateTestRequest
from backend.app.models.bdd import TestSuiteResponse
from backend.app.core.supabase import supabase_service
from backend.app.core.auth import get_current_user, UserContext
from backend.app.core.metrics import metrics_collector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-tests", response_model=TestSuiteResponse, status_code=status.HTTP_200_OK)
async def generate_tests(
    payload: GenerateTestRequest,
    current_user: UserContext = Depends(get_current_user)
) -> TestSuiteResponse:
    """
    Parses natural language requirements or Jira stories into structured Gherkin BDD test cases.
    """
    start_time = time.time()
    try:
        suite: TestSuiteResponse = await requirements_agent.analyze_requirement(
            requirement_text=payload.requirement_text,
            target_url=payload.target_url
        )

        # Save generated test suite to database
        await supabase_service.save_test_suite(suite.model_dump(), user_id=current_user.user_id)

        # Record metrics
        tokens = suite.metadata.get("total_tokens", 0)
        metrics_collector.record_generation(tokens=tokens)

        duration = int((time.time() - start_time) * 1000)
        metrics_collector.record_api_call(
            endpoint="/api/v1/generate-tests",
            method="POST",
            status_code=200,
            duration_ms=duration,
            role=current_user.role
        )

        return suite
    except Exception as e:
        logger.error(f"Error generating test suite: {e}")
        duration = int((time.time() - start_time) * 1000)
        metrics_collector.record_api_call(
            endpoint="/api/v1/generate-tests",
            method="POST",
            status_code=500,
            duration_ms=duration,
            role=current_user.role
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test cases: {str(e)}"
        )
