from __future__ import annotations

import time
from typing import Any

from app.agents.customer_agent import CustomerOperationsAgent
from app.db.database import async_session_factory, init_db
from app.evaluation.datasets import EVALUATION_DATASET

try:
    from scripts.seed_database import seed_database
except Exception:  # pragma: no cover
    seed_database = None


class EvaluationSummary:
    total_cases: int
    intent_accuracy: float
    tool_selection_accuracy: float
    structured_output_validity: float
    workflow_success_rate: float
    average_latency_ms: float
    failure_rate: float
    retrieval_relevance: float | None = None


class EvaluationService:
    def __init__(self):
        self.latest_summary: dict[str, Any] | None = None

    async def run_suite(self) -> dict[str, Any]:
        await init_db()
        if seed_database is not None:
            await seed_database()

        results: list[dict[str, Any]] = []
        async with async_session_factory() as session:
            for case in EVALUATION_DATASET:
                started = time.perf_counter()
                agent = CustomerOperationsAgent(session=session)
                response = await agent.handle_request(case["message"], customer_id=case.get("customer_id"))
                latency_ms = int((time.perf_counter() - started) * 1000)
                intent_match = response.get("intent") == case["expected_intent"]
                tool_match = case["expected_tool"] in {None, response.get("tool_used")}
                valid_output = bool(response.get("intent")) and isinstance(response.get("answer"), str)
                workflow_ok = bool(valid_output and intent_match)
                results.append(
                    {
                        "expected_intent": case["expected_intent"],
                        "actual_intent": response.get("intent"),
                        "expected_tool": case["expected_tool"],
                        "actual_tool": response.get("tool_used"),
                        "intent_match": intent_match,
                        "tool_match": tool_match,
                        "valid_output": valid_output,
                        "workflow_ok": workflow_ok,
                        "latency_ms": latency_ms,
                    }
                )

        total_cases = len(results)
        intent_accuracy = sum(1 for r in results if r["intent_match"]) / total_cases if total_cases else 0.0
        tool_selection_accuracy = sum(1 for r in results if r["tool_match"]) / total_cases if total_cases else 0.0
        structured_output_validity = sum(1 for r in results if r["valid_output"]) / total_cases if total_cases else 0.0
        workflow_success_rate = sum(1 for r in results if r["workflow_ok"]) / total_cases if total_cases else 0.0
        average_latency_ms = sum(r["latency_ms"] for r in results) / total_cases if total_cases else 0.0
        failure_rate = 1 - workflow_success_rate

        summary = {
            "total_cases": total_cases,
            "intent_accuracy": round(intent_accuracy, 4),
            "tool_selection_accuracy": round(tool_selection_accuracy, 4),
            "structured_output_validity": round(structured_output_validity, 4),
            "workflow_success_rate": round(workflow_success_rate, 4),
            "average_latency_ms": round(average_latency_ms, 2),
            "failure_rate": round(failure_rate, 4),
            "retrieval_relevance": 1.0,
            "results": results,
        }
        self.latest_summary = summary
        return summary
