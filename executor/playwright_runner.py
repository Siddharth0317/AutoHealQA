import os
import time
import uuid
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError

from backend.app.models.bdd import TestSuiteResponse, BDDScenario, TestStep
from executor.dom_inspector import DOMInspector
from agents.self_healing_agent import self_healing_agent, HealedSelectorResponse

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.join("storage", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


class StepLog(BaseModel):
    step_number: int
    scenario_title: str
    action: str
    target_description: str
    selector_used: Optional[str] = None
    input_value: Optional[str] = None
    status: str  # "passed", "failed", "healed"
    execution_time_ms: int
    error_message: Optional[str] = None
    healed_info: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None


class SelfHealingEvent(BaseModel):
    step_number: int
    original_selector: str
    healed_selector: str
    reasoning: str
    confidence_score: float
    timestamp: str


class TestRunResult(BaseModel):
    __test__ = False
    run_id: str
    suite_id: str
    status: str  # "passed", "failed", "healed"
    duration_ms: int
    scenarios_passed: int
    scenarios_failed: int
    total_steps: int
    steps_passed: int
    steps_failed: int
    steps_healed: int
    step_logs: List[StepLog] = Field(default_factory=list)
    self_healing_events: List[SelfHealingEvent] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    trace_url: Optional[str] = None


class PlaywrightTestExecutor:
    """
    Async Playwright Test Execution Engine with Self-Healing Selector Capabilities.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def execute_test_suite(
        self,
        test_suite: TestSuiteResponse,
        run_id: Optional[str] = None,
        base_url_override: Optional[str] = None,
        browser_type: str = "chromium",
        device_preset: str = "Desktop"
    ) -> TestRunResult:
        """
        Executes all scenarios and test steps in a test suite across Chromium, Firefox, WebKit,
        or Mobile device viewports, generating logs, screenshots, and auto-healing broken selectors.
        """
        run_id = run_id or f"run-{uuid.uuid4().hex[:8]}"
        run_dir = os.path.join(ARTIFACTS_DIR, run_id)
        os.makedirs(run_dir, exist_ok=True)

        start_time = time.time()
        step_logs: List[StepLog] = []
        healing_events: List[SelfHealingEvent] = []
        screenshots: List[str] = []

        scenarios_passed = 0
        scenarios_failed = 0
        total_steps_count = 0
        steps_passed_count = 0
        steps_failed_count = 0
        steps_healed_count = 0

        target_base_url = base_url_override or test_suite.target_url or "https://example.com"

        logger.info(f"Starting test execution [Run ID: {run_id}] Engine: '{browser_type}', Device: '{device_preset}' against {target_base_url}")

        viewport = {"width": 1280, "height": 720}
        user_agent = None

        if device_preset == "iPhone 14":
            viewport = {"width": 390, "height": 844}
            user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        elif device_preset == "Pixel 7":
            viewport = {"width": 412, "height": 915}
            user_agent = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"

        async with async_playwright() as p:
            browser_engine = getattr(p, browser_type, p.chromium)
            browser = await browser_engine.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"] if browser_type == "chromium" else []
            )
            
            trace_path = os.path.join(run_dir, "trace.zip")
            context: BrowserContext = await browser.new_context(
                viewport=viewport,
                user_agent=user_agent,
                is_mobile=(device_preset != "Desktop"),
                record_video_dir=run_dir if not self.headless else None
            )

            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page: Page = await context.new_page()

            suite_has_failure = False

            for scenario in test_suite.scenarios:
                scenario_passed = True
                logger.info(f"Executing Scenario: '{scenario.title}'")

                for step in scenario.test_steps:
                    total_steps_count += 1
                    step_start = time.time()
                    step_status = "passed"
                    error_msg = None
                    healed_info = None
                    screenshot_rel_path = None

                    # Perform action with self-healing retry block
                    success, error_msg, healed_event = await self._execute_step_with_healing(
                        page=page,
                        step=step,
                        scenario_title=scenario.title,
                        base_url=target_base_url
                    )

                    step_duration = int((time.time() - step_start) * 1000)

                    if healed_event:
                        step_status = "healed"
                        steps_healed_count += 1
                        healing_events.append(healed_event)
                        healed_info = healed_event.model_dump()

                    if success:
                        steps_passed_count += 1
                    else:
                        step_status = "failed"
                        steps_failed_count += 1
                        scenario_passed = False
                        suite_has_failure = True

                    # Capture screenshot for step
                    try:
                        shot_name = f"step_{step.step_number}_{step_status}_{uuid.uuid4().hex[:4]}.png"
                        shot_full_path = os.path.join(run_dir, shot_name)
                        await page.screenshot(path=shot_full_path, full_page=True)
                        screenshot_rel_path = f"/artifacts/{run_id}/{shot_name}"
                        screenshots.append(screenshot_rel_path)
                    except Exception as shot_err:
                        logger.warning(f"Failed to capture screenshot: {shot_err}")

                    step_logs.append(
                        StepLog(
                            step_number=step.step_number,
                            scenario_title=scenario.title,
                            action=step.action,
                            target_description=step.target_description,
                            selector_used=step.selector_hint,
                            input_value=step.input_value,
                            status=step_status,
                            execution_time_ms=step_duration,
                            error_message=error_msg,
                            healed_info=healed_info,
                            screenshot_path=screenshot_rel_path
                        )
                    )

                    if not success:
                        logger.error(f"Step {step.step_number} failed in scenario '{scenario.title}'. Skipping remaining scenario steps.")
                        break

                if scenario_passed:
                    scenarios_passed += 1
                else:
                    scenarios_failed += 1

            await context.tracing.stop(path=trace_path)
            await context.close()
            await browser.close()

        total_duration = int((time.time() - start_time) * 1000)
        overall_status = "healed" if steps_healed_count > 0 and not suite_has_failure else ("failed" if suite_has_failure else "passed")

        return TestRunResult(
            run_id=run_id,
            suite_id=test_suite.id,
            status=overall_status,
            duration_ms=total_duration,
            scenarios_passed=scenarios_passed,
            scenarios_failed=scenarios_failed,
            total_steps=total_steps_count,
            steps_passed=steps_passed_count,
            steps_failed=steps_failed_count,
            steps_healed=steps_healed_count,
            step_logs=step_logs,
            self_healing_events=healing_events,
            screenshots=screenshots,
            trace_url=f"/artifacts/{run_id}/trace.zip"
        )

    async def _execute_step_with_healing(
        self,
        page: Page,
        step: TestStep,
        scenario_title: str,
        base_url: str
    ) -> tuple[bool, Optional[str], Optional[SelfHealingEvent]]:
        """
        Executes a single Playwright action. If an element selector fails,
        captures DOM context, triggers self-healing LLM agent, and retries action.
        """
        selector = step.selector_hint or "body"

        # Attempt 1: Standard execution
        try:
            await self._run_playwright_action(page, step.action, selector, step.input_value, base_url)
            return True, None, None
        except Exception as first_error:
            first_err_msg = str(first_error)
            logger.warning(f"Action '{step.action}' failed on selector '{selector}': {first_err_msg}. Triggering Self-Healing...")

            # If action was navigate and URL failed, return failure directly
            if step.action == "navigate":
                return False, first_err_msg, None

            # Capture DOM failure context
            dom_context = await DOMInspector.capture_failure_context(
                page=page,
                failed_selector=selector,
                target_description=step.target_description,
                action=step.action
            )

            # Request repair selector from AI Self-Healing Agent
            heal_response: HealedSelectorResponse = await self_healing_agent.heal_selector(
                failed_selector=selector,
                target_description=step.target_description,
                action=step.action,
                error_message=first_err_msg,
                dom_context=dom_context
            )

            repair_selectors = [heal_response.healed_selector]
            if heal_response.fallback_selector:
                repair_selectors.append(heal_response.fallback_selector)

            # Attempt 2: Execution with repaired selectors
            for repair_sel in repair_selectors:
                try:
                    logger.info(f"Retrying step {step.step_number} with healed selector: '{repair_sel}'")
                    await self._run_playwright_action(page, step.action, repair_sel, step.input_value, base_url)
                    
                    event = SelfHealingEvent(
                        step_number=step.step_number,
                        original_selector=selector,
                        healed_selector=repair_sel,
                        reasoning=heal_response.reasoning,
                        confidence_score=heal_response.confidence_score,
                        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    )
                    return True, None, event
                except Exception as retry_err:
                    logger.warning(f"Retried selector '{repair_sel}' failed: {retry_err}")

            return False, f"Original selector '{selector}' and healed selector '{heal_response.healed_selector}' failed. Error: {first_err_msg}", None

    async def _run_playwright_action(
        self,
        page: Page,
        action: str,
        selector: str,
        input_value: Optional[str],
        base_url: str
    ):
        """
        Low-level Playwright action dispatcher.
        """
        timeout = 4000  # 4 second timeout per selector attempt to allow fast self-healing

        if action == "navigate":
            target_url = input_value if input_value and input_value.startswith("http") else base_url
            logger.info(f"Navigating to: {target_url}")
            await page.goto(target_url, timeout=10000, wait_until="domcontentloaded")

        elif action == "click":
            logger.info(f"Clicking selector: {selector}")
            await page.click(selector, timeout=timeout)

        elif action == "fill":
            logger.info(f"Filling selector '{selector}' with value '{input_value}'")
            val = input_value or ""
            await page.fill(selector, val, timeout=timeout)

        elif action == "wait_for_selector":
            logger.info(f"Waiting for selector: {selector}")
            await page.wait_for_selector(selector, timeout=timeout, state="visible")

        elif action == "assert_visible":
            logger.info(f"Asserting visible selector: {selector}")
            await page.wait_for_selector(selector, timeout=timeout, state="visible")

        elif action == "assert_text":
            logger.info(f"Asserting text on selector: {selector}")
            element = await page.wait_for_selector(selector, timeout=timeout)
            text_content = await element.text_content() if element else ""
            if input_value and input_value.lower() not in (text_content or "").lower():
                raise AssertionError(f"Expected text '{input_value}' not found in element content '{text_content}'")

        elif action == "select_option":
            logger.info(f"Selecting option '{input_value}' in selector '{selector}'")
            await page.select_option(selector, value=input_value, timeout=timeout)

        elif action == "press_key":
            key = input_value or "Enter"
            logger.info(f"Pressing key '{key}' on selector '{selector}'")
            await page.press(selector, key, timeout=timeout)

        else:
            logger.warning(f"Unrecognized action '{action}'. Defaulting to wait for selector.")
            await page.wait_for_selector("body", timeout=timeout)


# Singleton instance
playwright_executor = PlaywrightTestExecutor(headless=True)
