import pytest

from app.services.evaluation_service import EvaluationService


@pytest.mark.asyncio
async def test_evaluation_suite_runs() -> None:
    result = await EvaluationService().run_suite()
    assert result["total_cases"] >= 1
    assert 0.0 <= result["intent_accuracy"] <= 1.0
    assert 0.0 <= result["tool_selection_accuracy"] <= 1.0
    assert 0.0 <= result["structured_output_validity"] <= 1.0
    assert 0.0 <= result["workflow_success_rate"] <= 1.0
    assert result["average_latency_ms"] >= 0
