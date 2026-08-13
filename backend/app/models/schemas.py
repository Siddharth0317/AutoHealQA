from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from backend.app.models.bdd import TestSuiteResponse

BrowserType = Literal["chromium", "firefox", "webkit"]
DevicePreset = Literal["Desktop", "iPhone 14", "Pixel 7"]


class GenerateTestRequest(BaseModel):
    requirement_text: str = Field(..., min_length=5, description="Natural language user story, Jira ticket, or software requirement")
    target_url: Optional[str] = Field(None, description="Optional target application URL")


class ExecuteTestRequest(BaseModel):
    test_suite: TestSuiteResponse = Field(..., description="Structured BDD test suite to execute")
    target_url_override: Optional[str] = Field(None, description="Override default target application URL")
    headless: bool = Field(True, description="Run browser in headless mode")
    browser_type: BrowserType = Field("chromium", description="Browser engine to launch")
    device_preset: DevicePreset = Field("Desktop", description="Viewport / device emulation preset")


class CodeExportRequest(BaseModel):
    test_suite: TestSuiteResponse
    export_format: Literal["python", "gherkin"] = "python"


class JiraWebhookRequest(BaseModel):
    issue_key: str = Field(..., description="Jira issue key e.g. QA-101")
    summary: str = Field(..., description="Jira issue summary")
    description: Optional[str] = Field(None, description="Jira issue description")
    target_url: Optional[str] = Field(None, description="Target URL")


class GitHubWebhookRequest(BaseModel):
    action: str = Field(..., description="GitHub action e.g. opened, synchronize")
    pr_title: str = Field(..., description="PR title")
    pr_body: Optional[str] = Field(None, description="PR body description")
    preview_url: Optional[str] = Field(None, description="Vercel/Preview deployment URL")


class HistoryResponse(BaseModel):
    total_count: int
    runs: List[Dict[str, Any]]
