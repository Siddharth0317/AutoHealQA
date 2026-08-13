import pytest
from agents.groq_client import groq_client
from agents.requirements_agent import requirements_agent
from agents.self_healing_agent import self_healing_agent, HealedSelectorResponse
from backend.app.models.bdd import TestSuiteResponse


@pytest.mark.asyncio
async def test_groq_client_mock_completion():
    res = await groq_client.generate_chat_completion(
        system_prompt="Test system prompt",
        user_prompt="Test user prompt",
        json_mode=True
    )
    assert res is not None
    assert "model_used" in res
    assert res["execution_time_ms"] >= 0


@pytest.mark.asyncio
async def test_requirements_agent_analysis():
    req_text = "As a user, I want to login with email testuser@example.com and password Password123 so I can see my dashboard."
    suite: TestSuiteResponse = await requirements_agent.analyze_requirement(
        requirement_text=req_text,
        target_url="https://example.com"
    )
    assert suite.id.startswith("suite-")
    assert len(suite.scenarios) > 0
    first_scenario = suite.scenarios[0]
    assert len(first_scenario.test_steps) > 0
    assert first_scenario.test_steps[0].action in ["navigate", "wait_for_selector", "fill"]


@pytest.mark.asyncio
async def test_self_healing_agent_repair():
    failed_sel = "#non-existent-login-button"
    target_desc = "Click Submit Login button"
    action = "click"
    error_msg = "Timeout 4000ms waiting for locator('#non-existent-login-button')"
    dom_context = {
        "url": "https://example.com/login",
        "title": "Login Page",
        "interactables": [
            {"tag": "button", "type": "submit", "text": "Log In", "dataTestId": "login-submit-btn"}
        ],
        "dom_snippet": "<form><button data-testid='login-submit-btn' type='submit'>Log In</button></form>"
    }

    healed: HealedSelectorResponse = await self_healing_agent.heal_selector(
        failed_selector=failed_sel,
        target_description=target_desc,
        action=action,
        error_message=error_msg,
        dom_context=dom_context
    )
    assert healed.original_selector == failed_sel
    assert healed.healed_selector is not None
    assert len(healed.healed_selector) > 0
    assert healed.confidence_score > 0.0
