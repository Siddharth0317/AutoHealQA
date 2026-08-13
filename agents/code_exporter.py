import logging
from typing import Dict, Any
from backend.app.models.bdd import TestSuiteResponse

logger = logging.getLogger(__name__)


class CodeExporterAgent:
    """
    Agent for generating standalone, production-ready Python Playwright scripts
    and standard Gherkin .feature files from BDD TestSuiteResponse objects.
    """

    @staticmethod
    def export_to_python_pytest(test_suite: TestSuiteResponse) -> str:
        """
        Generates clean, runnable pytest-playwright Python code.
        """
        lines = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "",
            f"# {test_suite.title}",
            f"# Summary: {test_suite.summary}",
            f"# Target URL: {test_suite.target_url or 'https://example.com'}",
            ""
        ]

        target_url = test_suite.target_url or "https://example.com"

        for sc in test_suite.scenarios:
            func_name = f"test_{sc.id.lower().replace('-', '_')}_{sc.title.lower().replace(' ', '_')}"
            func_name = "".join(c for c in func_name if c.isalnum() or c == '_')

            lines.append(f"def {func_name}(page: Page):")
            lines.append(f'    """')
            lines.append(f'    Gherkin Scenario: {sc.title}')
            for g in sc.given:
                lines.append(f'    Given {g}')
            for w in sc.when:
                lines.append(f'    When {w}')
            for t in sc.then:
                lines.append(f'    Then {t}')
            lines.append(f'    """')

            for step in sc.test_steps:
                lines.append(f"    # Step {step.step_number}: {step.target_description}")
                action = step.action
                selector = step.selector_hint or "body"
                input_val = step.input_value

                if action == "navigate":
                    url = input_val if input_val and input_val.startswith("http") else target_url
                    lines.append(f'    page.goto("{url}")')

                elif action == "click":
                    lines.append(f'    page.click("{selector}")')

                elif action == "fill":
                    lines.append(f'    page.fill("{selector}", "{input_val or ""}")')

                elif action == "wait_for_selector":
                    lines.append(f'    page.wait_for_selector("{selector}")')

                elif action == "assert_visible":
                    lines.append(f'    expect(page.locator("{selector}")).to_be_visible()')

                elif action == "assert_text":
                    lines.append(f'    expect(page.locator("{selector}")).to_have_text("{input_val or ""}")')

                elif action == "select_option":
                    lines.append(f'    page.select_option("{selector}", "{input_val or ""}")')

                elif action == "press_key":
                    lines.append(f'    page.press("{selector}", "{input_val or "Enter"}")')

                else:
                    lines.append(f'    page.wait_for_selector("body")')

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def export_to_gherkin_feature(test_suite: TestSuiteResponse) -> str:
        """
        Generates standard Cucumber/Gherkin .feature file content.
        """
        lines = [
            f"Feature: {test_suite.title}",
            f"  {test_suite.summary}",
            ""
        ]

        for sc in test_suite.scenarios:
            lines.append(f"  Scenario: {sc.title}")
            for g in sc.given:
                lines.append(f"    Given {g}")
            for w in sc.when:
                lines.append(f"    When {w}")
            for t in sc.then:
                lines.append(f"    Then {t}")

            if sc.edge_cases:
                lines.append("    # Edge Cases & Boundary Validations:")
                for ec in sc.edge_cases:
                    lines.append(f"    # - {ec}")
            lines.append("")

        return "\n".join(lines)


code_exporter = CodeExporterAgent()
