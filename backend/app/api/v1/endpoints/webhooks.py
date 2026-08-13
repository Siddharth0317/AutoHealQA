import logging
from typing import Dict, Any
from fastapi import APIRouter, status
from agents.requirements_agent import requirements_agent
from executor.playwright_runner import playwright_executor
from backend.app.models.schemas import JiraWebhookRequest, GitHubWebhookRequest
from backend.app.core.supabase import supabase_service
from backend.app.core.metrics import metrics_collector

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/jira", status_code=status.HTTP_200_OK)
async def jira_webhook_listener(payload: JiraWebhookRequest) -> Dict[str, Any]:
    """
    Jira Webhook Listener: Ingests Jira issue payloads when tickets transition to 'Ready for QA',
    auto-generates BDD test cases via Groq LLM, and triggers async Playwright execution.
    """
    logger.info(f"Received Jira webhook for issue: {payload.issue_key} - '{payload.summary}'")
    
    req_text = f"Jira Issue [{payload.issue_key}]: {payload.summary}\nDescription:\n{payload.description or ''}"
    target_url = payload.target_url or "https://example.com"

    # Step 1: Generate BDD Test Suite
    suite = await requirements_agent.analyze_requirement(requirement_text=req_text, target_url=target_url)
    await supabase_service.save_test_suite(suite.model_dump(), user_id="jira_webhook_bot")
    metrics_collector.record_generation(tokens=suite.metadata.get("total_tokens", 0))

    # Step 2: Auto-execute test suite
    run_result = await playwright_executor.execute_test_suite(test_suite=suite, base_url_override=target_url)
    await supabase_service.save_test_run(run_result.model_dump(), user_id="jira_webhook_bot")

    return {
        "status": "success",
        "jira_issue": payload.issue_key,
        "suite_id": suite.id,
        "run_id": run_result.run_id,
        "execution_status": run_result.status,
        "total_steps": run_result.total_steps,
        "steps_healed": run_result.steps_healed
    }


@router.post("/webhooks/github", status_code=status.HTTP_200_OK)
async def github_webhook_listener(payload: GitHubWebhookRequest) -> Dict[str, Any]:
    """
    GitHub Webhook Listener: Ingests GitHub PR events, auto-generates test scenarios against
    the PR preview deployment URL, and executes Playwright tests.
    """
    logger.info(f"Received GitHub PR webhook: '{payload.pr_title}' (Action: {payload.action})")

    req_text = f"GitHub Pull Request: {payload.pr_title}\nPR Body:\n{payload.pr_body or ''}"
    target_url = payload.preview_url or "https://example.com"

    suite = await requirements_agent.analyze_requirement(requirement_text=req_text, target_url=target_url)
    await supabase_service.save_test_suite(suite.model_dump(), user_id="github_webhook_bot")
    metrics_collector.record_generation(tokens=suite.metadata.get("total_tokens", 0))

    run_result = await playwright_executor.execute_test_suite(test_suite=suite, base_url_override=target_url)
    await supabase_service.save_test_run(run_result.model_dump(), user_id="github_webhook_bot")

    return {
        "status": "success",
        "pr_title": payload.pr_title,
        "suite_id": suite.id,
        "run_id": run_result.run_id,
        "execution_status": run_result.status,
        "steps_passed": run_result.steps_passed,
        "steps_healed": run_result.steps_healed
    }
