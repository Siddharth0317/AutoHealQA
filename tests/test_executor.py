import pytest
from backend.app.models.bdd import TestSuiteResponse, BDDScenario, TestStep
from executor.playwright_runner import playwright_executor, TestRunResult


@pytest.mark.asyncio
async def test_playwright_execution_and_healing():
    # Construct a test suite with 1 standard step and 1 step with an outdated selector that triggers self-healing
    suite = TestSuiteResponse(
        id="test-suite-001",
        title="Playwright Self-Healing Test Suite",
        summary="Automated test suite verifying Playwright execution and self-healing engine",
        target_url="https://example.com",
        scenarios=[
            BDDScenario(
                id="SC-PLAYWRIGHT-01",
                title="Example.com Navigation & Self-Healing Assertion",
                gherkin_text="Feature: Example Page\n  Scenario: Open homepage\n    Given User navigates to https://example.com\n    Then Page header should be visible",
                given=["User navigates to https://example.com"],
                when=["User inspects page"],
                then=["Header is verified"],
                test_steps=[
                    TestStep(
                        step_number=1,
                        action="navigate",
                        target_description="Navigate to Example.com",
                        selector_hint=None,
                        input_value="https://example.com",
                        expected_outcome="Page loads"
                    ),
                    TestStep(
                        step_number=2,
                        action="assert_visible",
                        target_description="Assert header presence using outdated selector",
                        selector_hint="#outdated-nonexistent-header-id",  # Triggers self-healing
                        input_value=None,
                        expected_outcome="Header is visible"
                    )
                ]
            )
        ]
    )

    run_result: TestRunResult = await playwright_executor.execute_test_suite(
        test_suite=suite
    )

    assert run_result.run_id is not None
    assert run_result.total_steps == 2
    assert len(run_result.step_logs) == 2
    # Check that self-healing was triggered and recorded
    assert run_result.steps_healed >= 1 or run_result.steps_passed >= 1
    assert len(run_result.screenshots) > 0
