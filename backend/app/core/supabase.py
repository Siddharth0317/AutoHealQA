from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from backend.app.config import settings

logger = logging.getLogger(__name__)


class SupabaseServiceManager:
    """
    Supabase client wrapper with hybrid persistent in-memory fallback store
    to guarantee functionality even when Supabase environment keys are unset.
    """

    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        self.is_mock = not self.url or "placeholder" in self.url or not self.key or "placeholder" in self.key
        self.client = None

        # In-memory database fallback cache
        self._test_suites_db: Dict[str, Dict[str, Any]] = {}
        self._test_runs_db: Dict[str, Dict[str, Any]] = {}
        self._self_healing_db: List[Dict[str, Any]] = []
        self._metrics_db: List[Dict[str, Any]] = []

        if not self.is_mock:
            try:
                from supabase import create_client, Client
                self.client: Optional[Client] = create_client(self.url, self.key)
                logger.info("Supabase client successfully initialized.")
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}. Defaulting to local memory persistence.")
                self.is_mock = True

    async def save_test_suite(self, suite_data: Dict[str, Any], user_id: str = "guest_user") -> Dict[str, Any]:
        suite_id = suite_data.get("id")
        record = {
            "id": suite_id,
            "user_id": user_id,
            "title": suite_data.get("title"),
            "summary": suite_data.get("summary"),
            "target_url": suite_data.get("target_url"),
            "bdd_json": suite_data,
            "created_at": suite_data.get("created_at") or datetime.now(timezone.utc).isoformat()
        }
        self._test_suites_db[suite_id] = record

        if not self.is_mock and self.client:
            try:
                self.client.table("test_suites").insert(record).execute()
            except Exception as e:
                logger.error(f"Error saving test suite to Supabase: {e}")

        return record

    async def save_test_run(self, run_result: Dict[str, Any], user_id: str = "guest_user") -> Dict[str, Any]:
        run_id = run_result.get("run_id") or run_result.get("id")
        raw_status = run_result.get("status", "passed")
        formatted_status = raw_status.upper() if isinstance(raw_status, str) else "PASSED"

        record = {
            "id": run_id,
            "suite_id": run_result.get("suite_id"),
            "user_id": user_id,
            "status": formatted_status,
            "target_url": run_result.get("target_url") or "https://example.com",
            "requirement_prompt": run_result.get("requirement_prompt") or "Natural language user story execution",
            "engine": run_result.get("browser_type") or run_result.get("engine") or "chromium",
            "device": run_result.get("device_preset") or run_result.get("device") or "Desktop",
            "execution_mode": run_result.get("execution_mode") or "👀 Open Live Browser Window",
            "duration_ms": run_result.get("duration_ms"),
            "total_steps": run_result.get("total_steps"),
            "steps_passed": run_result.get("steps_passed"),
            "steps_failed": run_result.get("steps_failed"),
            "steps_healed": run_result.get("steps_healed"),
            "step_logs": run_result.get("step_logs"),
            "screenshots": run_result.get("screenshots"),
            "trace_url": run_result.get("trace_url"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self._test_runs_db[run_id] = record

        # Save any self-healing logs
        for event in run_result.get("self_healing_events", []):
            heal_entry = {
                "run_id": run_id,
                "step_number": event.get("step_number"),
                "original_selector": event.get("original_selector"),
                "healed_selector": event.get("healed_selector"),
                "reasoning": event.get("reasoning"),
                "confidence_score": event.get("confidence_score"),
                "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat()
            }
            self._self_healing_db.append(heal_entry)

        if not self.is_mock and self.client:
            try:
                self.client.table("test_runs").insert(record).execute()
            except Exception as e:
                logger.warning(f"Supabase primary insert notice: {e}. Retrying with core schema fields...")
                try:
                    core_record = {
                        "id": record["id"],
                        "suite_id": record.get("suite_id"),
                        "user_id": record["user_id"],
                        "status": record["status"].lower(),
                        "duration_ms": record["duration_ms"],
                        "total_steps": record["total_steps"],
                        "steps_passed": record["steps_passed"],
                        "steps_failed": record["steps_failed"],
                        "steps_healed": record["steps_healed"],
                        "step_logs": record["step_logs"],
                        "screenshots": record["screenshots"],
                        "trace_url": record["trace_url"],
                        "created_at": record["created_at"]
                    }
                    self.client.table("test_runs").insert(core_record).execute()
                except Exception as err2:
                    logger.error(f"Error saving test run to Supabase: {err2}")

        return record

    async def clear_history(self, user_id: Optional[str] = None) -> bool:
        if user_id:
            self._test_runs_db = {k: v for k, v in self._test_runs_db.items() if v.get("user_id") != user_id}
        else:
            self._test_runs_db.clear()
            self._self_healing_db.clear()

        if not self.is_mock and self.client:
            try:
                query = self.client.table("test_runs").delete()
                if user_id:
                    query = query.eq("user_id", user_id)
                else:
                    query = query.neq("id", "")
                query.execute()
            except Exception as e:
                logger.error(f"Error clearing history from Supabase: {e}")
        return True

    async def get_test_run_by_id(self, run_id: str) -> Optional[Dict[str, Any]]:
        if run_id in self._test_runs_db:
            return self._test_runs_db[run_id]

        if not self.is_mock and self.client:
            try:
                res = self.client.table("test_runs").select("*").eq("id", run_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Error fetching test run {run_id} from Supabase: {e}")

        return None

    async def get_run_history(self, limit: int = 20, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        history = list(self._test_runs_db.values())
        if user_id:
            history = [r for r in history if r.get("user_id") == user_id]

        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        if not self.is_mock and self.client:
            try:
                query = self.client.table("test_runs").select("*")
                if user_id:
                    query = query.eq("user_id", user_id)
                res = query.order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return res.data
            except Exception as e:
                logger.error(f"Error fetching run history from Supabase: {e}")

        return history[:limit]

    async def get_self_healing_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._self_healing_db[-limit:]


# Singleton instance
supabase_service = SupabaseServiceManager()
