"""
Unit tests for LangGraph Deterministic Orchestration Pipeline.
"""

from src.orchestration.langgraph_pipeline import WorkbenchOrchestrator


def test_orchestrator_full_pipeline_run():
    orchestrator = WorkbenchOrchestrator()
    res = orchestrator.run_pipeline(
        query="Inspect refinery unit 4 telemetry pressure and temperature logs.",
        user_id="user-123",
        role="OPERATOR",
        workspace_id="ws-refinery-01",
    )

    assert res["status"] == "COMPLETED"
    assert res["request_id"].startswith("req-")
    assert res["role"] == "OPERATOR"
    assert res["workspace_id"] == "ws-refinery-01"
    assert "intent" in res
    assert "workflow_route" in res
    assert res["authorization_scope"]["effective_classification_ceiling"] == 3
    assert "final_response" in res
    assert "### 1. Verified Findings" in res["final_response"]
    assert "### 4. Confidence Score" in res["final_response"]
    assert res["attestation_package"] is not None
    assert res["attestation_package"]["proof_type"] == "Ed25519_CLORA_PROOF"
