from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.models.bdd import TestSuiteResponse


class GenerateTestRequest(BaseModel):
    requirement_text: str = Field(..., min_length=5, description="Natural language user story, Jira ticket, or software requirement")
    target_url: Optional[str] = Field(None, description="Optional target application URL")


class ExecuteTestRequest(BaseModel):
    test_suite: TestSuiteResponse = Field(..., description="Structured BDD test suite to execute")
    target_url_override: Optional[str] = Field(None, description="Override default target application URL")
    headless: bool = Field(True, description="Run browser in headless mode")


class HistoryResponse(BaseModel):
    total_count: int
    runs: List[Dict[str, Any]]
