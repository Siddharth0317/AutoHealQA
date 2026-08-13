import pytest
from agents.code_exporter import code_exporter
from backend.app.models.bdd import TestSuiteResponse, BDDScenario, TestStep


def test_code_exporter_pytest():
    suite = TestSuiteResponse(
        id="suite-export-01",
        title="Export Test Suite",
        summary="Test suite for python export",
        target_url="https://example.com",
        scenarios=[
            BDDScenario(
                id="SC-01",
                title="Login Verification",
                gherkin_text="Given User is on page\nWhen User clicks button\nThen Header is visible",
                given=["User is on page"],
                when=["User clicks button"],
                then=["Header is visible"],
                test_steps=[
                    TestStep(
                        step_number=1,
                        action="navigate",
                        target_description="Navigate page",
                        selector_hint=None,
                        input_value="https://example.com",
                        expected_outcome="Loaded"
                    ),
                    TestStep(
                        step_number=2,
                        action="click",
                        target_description="Click Submit",
                        selector_hint="button[type='submit']",
                        input_value=None,
                        expected_outcome="Clicked"
                    )
                ]
            )
        ]
    )

    py_code = code_exporter.export_to_python_pytest(suite)
    assert "import pytest" in py_code
    assert "def test_sc_01_login_verification(page: Page):" in py_code
    assert 'page.goto("https://example.com")' in py_code
    assert 'page.click("button[type=\'submit\']")' in py_code

    gherkin_text = code_exporter.export_to_gherkin_feature(suite)
    assert "Feature: Export Test Suite" in gherkin_text
    assert "Scenario: Login Verification" in gherkin_text
