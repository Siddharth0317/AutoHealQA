import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class APICallLog(BaseModel):
    endpoint: str
    method: str
    status_code: int
    duration_ms: int
    user_role: str
    timestamp: str


class SystemMetricsResponse(BaseModel):
    total_test_generations: int
    total_test_executions: int
    total_steps_executed: int
    total_self_healing_events: int
    self_healing_success_rate: float
    total_llm_tokens_consumed: int
    average_execution_duration_ms: int
    api_call_logs: List[APICallLog] = Field(default_factory=list)


class MetricsCollector:
    """
    In-memory system performance & telemetry collector.
    """

    def __init__(self):
        self.generations_count = 0
        self.executions_count = 0
        self.total_steps_executed = 0
        self.healing_events_count = 0
        self.healing_success_count = 0
        self.total_tokens_used = 0
        self.execution_durations: List[int] = []
        self.api_logs: List[APICallLog] = []

    def record_generation(self, tokens: int):
        self.generations_count += 1
        self.total_tokens_used += tokens

    def record_execution(self, steps: int, healed: int, duration_ms: int):
        self.executions_count += 1
        self.total_steps_executed += steps
        self.healing_events_count += healed
        self.healing_success_count += healed
        self.execution_durations.append(duration_ms)

    def record_api_call(self, endpoint: str, method: str, status_code: int, duration_ms: int, role: str):
        log = APICallLog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            user_role=role,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        self.api_logs.append(log)
        if len(self.api_logs) > 100:
            self.api_logs.pop(0)

    def get_metrics_summary(self) -> SystemMetricsResponse:
        avg_duration = (
            sum(self.execution_durations) // len(self.execution_durations)
            if self.execution_durations else 0
        )
        success_rate = (
            (self.healing_success_count / self.healing_events_count * 100.0)
            if self.healing_events_count > 0 else 100.0
        )

        return SystemMetricsResponse(
            total_test_generations=self.generations_count,
            total_test_executions=self.executions_count,
            total_steps_executed=self.total_steps_executed,
            total_self_healing_events=self.healing_events_count,
            self_healing_success_rate=round(success_rate, 2),
            total_llm_tokens_consumed=self.total_tokens_used,
            average_execution_duration_ms=avg_duration,
            api_call_logs=self.api_logs[-20:]
        )


# Singleton instance
metrics_collector = MetricsCollector()
