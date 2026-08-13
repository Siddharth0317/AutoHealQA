import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response, HTMLResponse
from agents.code_exporter import code_exporter
from backend.app.core.pdf_generator import pdf_report_generator

logger = logging.getLogger(__name__)
router = APIRouter()


class CodeExportRequest(BaseModel):
    test_suite: Dict[str, Any] = Field(..., description="Structured test suite JSON")
    export_format: str = Field("python", description="Format: python | zip")
    latest_run: Optional[Dict[str, Any]] = None


class CodeExportResponse(BaseModel):
    export_format: str
    exported_code: str
    filename: str


@router.post("/export-code", response_model=CodeExportResponse, status_code=status.HTTP_200_OK)
async def export_code(payload: CodeExportRequest) -> CodeExportResponse:
    """
    Exports a test suite to runnable Pytest code.
    """
    suite_id = payload.test_suite.get("id", "suite")

    code = code_exporter.to_pytest_script(payload.test_suite)
    return CodeExportResponse(
        export_format="python",
        exported_code=code,
        filename=f"{suite_id}.py"
    )


@router.post("/export-pdf", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def export_pdf(payload: CodeExportRequest):
    """
    Generates a printable HTML/PDF report for a test suite and execution run.
    """
    suite_id = payload.test_suite.get("id", "suite_001")
    run_record = payload.latest_run or {
        "id": f"suite-spec-{suite_id}",
        "status": "READY",
        "duration_ms": 0,
        "total_steps": sum(len(s.get("test_steps", [])) for s in payload.test_suite.get("scenarios", [])),
        "steps_passed": 0,
        "steps_healed": 0,
        "steps_failed": 0,
        "step_logs": [
            {
                "step_number": st.get("step_number"),
                "action": st.get("action"),
                "target_description": st.get("target_description"),
                "selector_used": st.get("selector_hint") or "auto",
                "status": "pending",
                "execution_time_ms": 0
            }
            for sc in payload.test_suite.get("scenarios", [])
            for st in sc.get("test_steps", [])
        ],
        "self_healing_events": []
    }

    html_content = pdf_report_generator.generate_html_report(run_record)
    return HTMLResponse(
        content=html_content,
        headers={
            "Content-Disposition": f"inline; filename=AutoHealQA_Report_{suite_id}.html"
        }
    )


@router.post("/export-zip", status_code=status.HTTP_200_OK)
async def export_zip(payload: CodeExportRequest):
    """
    Generates and streams a full project .zip bundle containing python scripts, html reports, and README.
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
