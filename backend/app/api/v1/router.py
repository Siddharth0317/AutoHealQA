from fastapi import APIRouter
from backend.app.api.v1.endpoints import generate, execute, runs, history, admin, export, webhooks

api_router = APIRouter()

api_router.include_router(generate.router, tags=["Test Generation"])
api_router.include_router(execute.router, tags=["Test Execution"])
api_router.include_router(export.router, tags=["Code Export"])
api_router.include_router(webhooks.router, tags=["Jira & GitHub Webhooks"])
api_router.include_router(runs.router, tags=["Test Runs"])
api_router.include_router(history.router, tags=["History"])
api_router.include_router(admin.router, tags=["Admin & Telemetry"])
