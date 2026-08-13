import logging
import uuid
from typing import Dict, Any, Optional
from agents.groq_client import groq_client
from backend.app.models.bdd import TestSuiteResponse, BDDScenario, TestStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a Senior QA Automation Architect and BDD Specialist.
Your task is to analyze plain English software requirements, user stories, or Jira tickets and generate:
1. Structured Gherkin BDD Scenarios (Given / When / Then).
2. Step-by-step executable Playwright automation test steps.
3. Edge cases and boundary condition validations.

You MUST respond strictly with a valid JSON object following this exact JSON structure:
{
  "title": "Short title of the test suite",
  "summary": "Executive summary of test coverage",
  "target_url": "Target URL mentioned in requirement or default e.g. https://example.com",
  "prerequisites": ["User account exists", "Browser open"],
  "scenarios": [
    {
      "id": "SC-001",
      "title": "Successful Login Scenario",
      "gherkin_text": "Feature: User Authentication\\n  Scenario: Successful Login\\n    Given User is on the login page\\n    When User enters valid credentials\\n    Then User should be redirected to the dashboard",
      "given": ["User is on the login page"],
      "when": ["User enters valid credentials", "Clicks login button"],
      "then": ["User should see dashboard welcome message"],
      "test_steps": [
        {
          "step_number": 1,
          "action": "navigate",
          "target_description": "Navigate to login page",
          "selector_hint": null,
          "input_value": "https://example.com/login",
          "expected_outcome": "Login page loads successfully"
        },
        {
          "step_number": 2,
          "action": "fill",
          "target_description": "Enter username input",
          "selector_hint": "input[name='username'], #username, [data-testid='username']",
          "input_value": "testuser@example.com",
          "expected_outcome": "Username filled"
        },
        {
          "step_number": 3,
          "action": "fill",
          "target_description": "Enter password input",
          "selector_hint": "input[name='password'], #password, [data-testid='password']",
          "input_value": "Password123!",
          "expected_outcome": "Password filled"
        },
        {
          "step_number": 4,
          "action": "click",
          "target_description": "Click Submit Login button",
          "selector_hint": "button[type='submit'], #login-btn, text='Log In'",
          "input_value": null,
          "expected_outcome": "Form submitted"
        },
        {
          "step_number": 5,
          "action": "assert_visible",
          "target_description": "Dashboard element visible",
          "selector_hint": ".dashboard-welcome, #dashboard, text='Welcome'",
          "input_value": null,
          "expected_outcome": "Dashboard welcome message displayed"
        }
      ],
      "edge_cases": ["Invalid password error toast", "Empty email validation error"]
    }
  ]
}
"""


class RequirementsAnalyzerAgent:
    """
    Agent responsible for converting natural language requirements into
    structured Gherkin BDD test suites and executable Playwright JSON test steps.
    """

    def __init__(self):
        self.client = groq_client

    async def analyze_requirement(
        self,
        requirement_text: str,
        target_url: Optional[str] = None
    ) -> TestSuiteResponse:
        """
        Parses requirements text using Groq LLM API and returns a validated TestSuiteResponse.
        """
        logger.info(f"Analyzing requirement (length: {len(requirement_text)})")
        suite_id = f"suite-{uuid.uuid4().hex[:8]}"

        user_prompt = f"Requirement Specification:\n{requirement_text}\n"
        if target_url:
            user_prompt += f"\nTarget Application URL: {target_url}\n"

        # Define fallback mock response in case of offline/mock mode
        default_target_url = target_url or "https://example.com"
        mock_response = {
            "title": "Automated BDD Test Suite",
            "summary": f"Generated test scenarios for: {requirement_text[:100]}...",
            "target_url": default_target_url,
            "prerequisites": ["Browser instance active", "Target website accessible"],
            "scenarios": [
                {
                    "id": "SC-001",
                    "title": "Main User Flow Verification",
                    "gherkin_text": f"Feature: Main User Flow\n  Scenario: Execute requirement steps\n    Given User navigates to {default_target_url}\n    When User performs primary actions\n    Then Application responds accurately",
                    "given": [f"User navigates to {default_target_url}"],
                    "when": ["User completes main form fields", "User clicks submit button"],
                    "then": ["Success response or target section is displayed"],
                    "test_steps": [
                        {
                            "step_number": 1,
                            "action": "navigate",
                            "target_description": f"Navigate to target app {default_target_url}",
                            "selector_hint": None,
                            "input_value": default_target_url,
                            "expected_outcome": "Page loads with HTTP 200"
                        },
                        {
                            "step_number": 2,
                            "action": "wait_for_selector",
                            "target_description": "Wait for body/main container",
                            "selector_hint": "body, main, #app",
                            "input_value": None,
                            "expected_outcome": "Main page container is rendered"
                        },
                        {
                            "step_number": 3,
                            "action": "assert_visible",
                            "target_description": "Assert header/title presence",
                            "selector_hint": "h1, header, .title, a",
                            "input_value": None,
                            "expected_outcome": "Header element is visible"
                        }
                    ],
                    "edge_cases": ["Page timeout handled gracefully", "Network connectivity interruption"]
                }
            ]
        }

        completion_res = await self.client.generate_chat_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            json_mode=True,
            mock_fallback_response=mock_response
        )

        parsed_data = completion_res.get("parsed") or mock_response

        # Build Pydantic model response
        scenarios = []
        for sc in parsed_data.get("scenarios", []):
            steps = [TestStep(**st) for st in sc.get("test_steps", [])]
            scenario = BDDScenario(
                id=sc.get("id", f"SC-{uuid.uuid4().hex[:4]}"),
                title=sc.get("title", "Untitled Scenario"),
                gherkin_text=sc.get("gherkin_text", ""),
                given=sc.get("given", []),
                when=sc.get("when", []),
                then=sc.get("then", []),
                test_steps=steps,
                edge_cases=sc.get("edge_cases", [])
            )
            scenarios.append(scenario)

        suite = TestSuiteResponse(
            id=suite_id,
            title=parsed_data.get("title", "Generated Test Suite"),
            summary=parsed_data.get("summary", "Test suite derived from user requirement."),
            target_url=parsed_data.get("target_url") or default_target_url,
            scenarios=scenarios,
            prerequisites=parsed_data.get("prerequisites", []),
            metadata={
                "model_used": completion_res.get("model_used"),
                "execution_time_ms": completion_res.get("execution_time_ms"),
                "total_tokens": completion_res.get("total_tokens"),
                "is_mock": completion_res.get("is_mock", False)
            }
        )

        return suite


# Singleton instance
requirements_agent = RequirementsAnalyzerAgent()
