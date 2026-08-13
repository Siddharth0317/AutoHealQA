import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from agents.code_exporter import code_exporter

logger = logging.getLogger(__name__)
router = APIRouter()


class CodeExportRequest(BaseModel):
    test_suite: Dict[str, Any] = Field(..., description="Structured test suite JSON")
    export_format: str = Field("python", description="Format: python | gherkin | zip")
    latest_run: Optional[Dict[str, Any]] = None


class CodeExportResponse(BaseModel):
    export_format: str
    exported_code: str
    filename: str


@router.post("/export-code", response_model=CodeExportResponse, status_code=status.HTTP_200_OK)
async def export_code(payload: CodeExportRequest) -> CodeExportResponse:
    """
    Exports a test suite to runnable Pytest code or Cucumber Gherkin feature files.
    """
    suite_id = payload.test_suite.get("id", "suite")

    if payload.export_format.lower() == "gherkin":
        code = code_exporter.to_gherkin_feature(payload.test_suite)
        return CodeExportResponse(
            export_format="gherkin",
            exported_code=code,
            filename=f"{suite_id}.feature"
        )
    else:
        code = code_exporter.to_pytest_script(payload.test_suite)
        return CodeExportResponse(
            export_format="python",
            exported_code=code,
            filename=f"{suite_id}.py"
        )


@router.post("/export-zip", status_code=status.HTTP_200_OK)
async def export_zip(payload: CodeExportRequest):
    """
    Generates and streams a full project .zip bundle containing python scripts, gherkin features, html reports, and README.
    """
    suite_id = payload.test_suite.get("id", "suite_001")
    zip_bytes = code_exporter.create_full_suite_zip(payload.test_suite, payload.latest_run)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=AutoHealQA_Suite_{suite_id}.zip"
        }
    )
