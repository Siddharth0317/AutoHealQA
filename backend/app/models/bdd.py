from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


ActionType = Literal[
    "navigate",
    "click",
    "fill",
    "assert_text",
    "assert_visible",
    "wait_for_selector",
    "select_option",
    "press_key"
]


class TestStep(BaseModel):
    __test__ = False
    step_number: int = Field(..., description="1-indexed sequence number of the test step")
    action: ActionType = Field(..., description="Action to perform in Playwright")
    target_description: str = Field(..., description="Human-readable description of target element or page")
    selector_hint: Optional[str] = Field(None, description="Suggested CSS selector, XPath, or text locator")
    input_value: Optional[str] = Field(None, description="Input data string if action is fill or select_option")
    expected_outcome: str = Field(..., description="Expected result or assertion criteria for this step")


class BDDScenario(BaseModel):
    id: str = Field(..., description="Unique ID for scenario e.g. SC-001")
    title: str = Field(..., description="Concise title of the scenario")
    gherkin_text: str = Field(..., description="Full Gherkin syntax (Given/When/Then)")
    given: List[str] = Field(default_factory=list, description="Given preconditions")
    when: List[str] = Field(default_factory=list, description="When actions")
    then: List[str] = Field(default_factory=list, description="Then expected assertions")
    test_steps: List[TestStep] = Field(default_factory=list, description="Executable structured Playwright steps")
    edge_cases: List[str] = Field(default_factory=list, description="Potential boundary or edge case considerations")


class TestSuiteResponse(BaseModel):
    __test__ = False
    id: str = Field(..., description="Unique test suite identifier")
    title: str = Field(..., description="Title of the test suite")
    summary: str = Field(..., description="Executive summary of generated test cases")
    target_url: Optional[str] = Field(None, description="Base application URL for execution")
    scenarios: List[BDDScenario] = Field(default_factory=list, description="List of generated BDD scenarios")
    prerequisites: List[str] = Field(default_factory=list, description="Pre-execution setup requirements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="LLM token usage and execution metadata")
