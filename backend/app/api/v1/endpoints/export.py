import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from agents.code_exporter import code_exporter
from backend.app.models.schemas import CodeExportRequest
from backend.app.core.auth import get_current_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export-code", status_code=status.HTTP_200_OK)
async def export_code(
    payload: CodeExportRequest,
    current_user: UserContext = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Exports a structured BDD test suite into a standalone Python pytest script
    or a standard Cucumber .feature file.
    """
    if payload.export_format == "gherkin":
        content = code_exporter.export_to_gherkin_feature(payload.test_suite)
        filename = f"{payload.test_suite.id}.feature"
        mime_type = "text/plain"
    else:
        content = code_exporter.export_to_python_pytest(payload.test_suite)
        filename = f"{payload.test_suite.id}.py"
        mime_type = "text/x-python"

    return {
        "suite_id": payload.test_suite.id,
        "format": payload.export_format,
        "filename": filename,
        "mime_type": mime_type,
        "exported_code": content
    }
