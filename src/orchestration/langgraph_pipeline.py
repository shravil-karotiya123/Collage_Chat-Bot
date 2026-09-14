"""
MRPL AI Workbench — LangGraph Deterministic Pipeline Engine
Connects Router -> Authorization Gate -> RAG -> Investigation -> Synthesis -> Verification -> Formatter -> Attestor.
"""

import logging
import uuid
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END
from src.orchestration.workflow_state import WorkbenchWorkflowState
from src.routing.model_router import ModelRouter
from src.core.security.authorization_gate import AuthorizationGate
from src.retrieval.retriever import AuthorizedRetriever
from src.analytics.duckdb_engine import DuckDBInvestigationEngine
from src.verification.claim_extractor import ClaimExtractor
from src.verification.evidence_verifier import EvidenceVerifier
from src.verification.confidence import ConfidenceScorer
from src.verification.causal_guard import CausalLeapGuard
from src.verification.guardrail_formatter import GuardrailFormatter
from src.audit.hash_ledger import AuditLedger
from src.attestation.evidence_attestor import EvidenceAttestor

logger = logging.getLogger("MRPL.Orchestration.LangGraph")


class WorkbenchOrchestrator:
    """
    Deterministic LangGraph pipeline execution engine.
    """

    def __init__(
        self,
        router: Optional[ModelRouter] = None,
        auth_gate: Optional[AuthorizationGate] = None,
        retriever: Optional[AuthorizedRetriever] = None,
        analytics_engine: Optional[DuckDBInvestigationEngine] = None,
        audit_ledger: Optional[AuditLedger] = None,
        attestor: Optional[EvidenceAttestor] = None,
    ) -> None:
        self.router = router or ModelRouter()
        self.auth_gate = auth_gate or AuthorizationGate()
        self.retriever = retriever or AuthorizedRetriever(auth_gate=self.auth_gate)
        self.analytics_engine = analytics_engine or DuckDBInvestigationEngine()
        self.audit_ledger = audit_ledger or AuditLedger()
        self.attestor = attestor or EvidenceAttestor()

        self.claim_extractor = ClaimExtractor()
        self.evidence_verifier = EvidenceVerifier()
        self.causal_guard = CausalLeapGuard()
        self.formatter = GuardrailFormatter()

        self.graph = self._build_graph()

    # Node 1: Router Node
    def node_router(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        query = state.get("query", "")
        route_res = self.router.route(query)
        target_model = getattr(route_res, "target_model", "qwen2.5:7b")
        intent = getattr(route_res, "intent", "general")

        self.audit_ledger.append_event(
            event_type="ROUTER_SELECTION",
            request_id=state["request_id"],
            user_id=state.get("user_id"),
            workspace_id=state.get("workspace_id"),
            operation=f"Model: {target_model}, Intent: {intent}",
        )
        return {
            **state,
            "intent": str(intent),
            "workflow_route": str(target_model),
            "status": "ROUTED",
        }

    # Node 2: Authorization Gate Node
    def node_authorization_gate(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        policy = self.auth_gate.build_retrieval_policy(
            role=state.get("role", "USER"),
            workspace_id=state.get("workspace_id", "default"),
            user_id=state.get("user_id"),
        )
        self.audit_ledger.append_event(
            event_type="AUTHORIZATION_POLICY_COMPILED",
            request_id=state["request_id"],
            user_id=state.get("user_id"),
            workspace_id=state.get("workspace_id"),
            operation=f"Ceiling: {policy.get('effective_classification_ceiling')}",
        )
        return {
            **state,
            "authorization_scope": policy,
            "status": "AUTHORIZED",
        }

    # Node 3: RAG Retrieval Node
    def node_rag_retrieval(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        query = state.get("query", "")
        results = self.retriever.retrieve(
            query=query,
            role=state.get("role", "USER"),
            workspace_id=state.get("workspace_id", "default"),
            user_id=state.get("user_id"),
        )
        chunk_ids = [r.get("id") for r in results]
        self.audit_ledger.append_event(
            event_type="RAG_RETRIEVAL",
            request_id=state["request_id"],
            user_id=state.get("user_id"),
            workspace_id=state.get("workspace_id"),
            operation=f"Retrieved {len(chunk_ids)} chunks",
        )
        return {
            **state,
            "citations": results,
            "retrieved_chunk_ids": chunk_ids,
            "status": "RETRIEVED",
        }

    # Node 4: Investigation Node (DuckDB)
    def node_investigation(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        query = state.get("query", "").lower()
        analysis = {}

        if any(term in query for term in ["telemetry", "pressure", "temperature", "sensor"]):
            sql = "SELECT unit_id, sensor_id, pressure_psi, temperature_c, status FROM refinery_telemetry LIMIT 5"
            analysis["rows"] = self.analytics_engine.execute_analytical_query(sql)
            analysis["query"] = sql

            self.audit_ledger.append_event(
                event_type="TELEMETRY_INVESTIGATION",
                request_id=state["request_id"],
                user_id=state.get("user_id"),
                workspace_id=state.get("workspace_id"),
                operation=f"DuckDB SQL: {sql}",
            )

        return {
            **state,
            "analysis_results": analysis,
            "status": "INVESTIGATED",
        }

    # Node 5: Industrial Synthesis Node
    def node_industrial_synthesis(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        query = state.get("query", "")
        citations = state.get("citations", [])
        analysis = state.get("analysis_results", {})

        context_str = "\n".join([f"- [{c.get('id')}] {c.get('document')}" for c in citations])
        draft = f"Operational Summary for query '{query}'. Grounded in retrieved evidence:\n{context_str}"
        if analysis and "rows" in analysis:
            draft += f"\nTelemetry analytics observation: {analysis['rows']}"

        self.audit_ledger.append_event(
            event_type="INDUSTRIAL_SYNTHESIS",
            request_id=state["request_id"],
            user_id=state.get("user_id"),
            workspace_id=state.get("workspace_id"),
            operation="Draft generated with citations",
        )
        return {
            **state,
            "draft_response": draft,
            "status": "SYNTHESIZED",
        }

    # Node 6: Hallucination Firewall & Verification Node
    def node_verification_firewall(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        draft = state.get("draft_response", "")
        citations = state.get("citations", [])

        claims = self.claim_extractor.extract_claims(draft)
        verifications = self.evidence_verifier.verify_claims(claims, citations)
        confidence = ConfidenceScorer.calculate_confidence(verifications)

        sanitized_draft, flags = self.causal_guard.audit_text(draft, has_causal_proof=False)

        self.audit_ledger.append_event(
            event_type="HALLUCINATION_FIREWALL_VERIFICATION",
            request_id=state["request_id"],
            user_id=state.get("user_id"),
            workspace_id=state.get("workspace_id"),
            operation=f"Claims: {len(claims)}, Confidence: {confidence}",
        )
        return {
            **state,
            "draft_claims": claims,
            "verification_results": verifications,
            "uncertainty_items": flags,
            "confidence_score": confidence,
            "draft_response": sanitized_draft,
            "status": "VERIFIED",
        }

    # Node 7: Guardrail Formatter Node
    def node_guardrail_formatter(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        findings = state.get("draft_response", "")
        analysis = "Observations derived strictly from permitted vector store evidence and local DuckDB analytics."
        uncertainty = state.get("uncertainty_items", [])
        confidence = state.get("confidence_score", 0.0)
        citations = state.get("citations", [])

        final_formatted = self.formatter.format_response(
            findings=findings,
            analysis=analysis,
            uncertainty_items=uncertainty,
            confidence_score=confidence,
            evidence_citations=citations,
        )
        return {
            **state,
            "final_response": final_formatted,
            "status": "FORMATTED",
        }

    # Node 8: Ed25519 Attestation Node
    def node_attestation(self, state: WorkbenchWorkflowState) -> WorkbenchWorkflowState:
        req_id = state["request_id"]
        response_text = state.get("final_response", "")
        chunk_ids = state.get("retrieved_chunk_ids", [])

        proof = self.attestor.create_proof_package(
            request_id=req_id,
            response_text=response_text,
            citations=chunk_ids,
        )
        attest_id = f"proof-{req_id[:8]}"

        self.audit_ledger.append_event(
            event_type="ED25519_ATTESTATION",
            request_id=req_id,
            user_id=state.get("user_id"),
            workspace_id=state.get("workspace_id"),
            operation=f"Proof package generated: {attest_id}",
        )
        return {
            **state,
            "attestation_package": proof,
            "attestation_id": attest_id,
            "status": "COMPLETED",
        }

    def _build_graph(self) -> Any:
        builder = StateGraph(WorkbenchWorkflowState)

        builder.add_node("router", self.node_router)
        builder.add_node("authorization_gate", self.node_authorization_gate)
        builder.add_node("rag_retrieval", self.node_rag_retrieval)
        builder.add_node("investigation", self.node_investigation)
        builder.add_node("industrial_synthesis", self.node_industrial_synthesis)
        builder.add_node("verification_firewall", self.node_verification_firewall)
        builder.add_node("guardrail_formatter", self.node_guardrail_formatter)
        builder.add_node("attestation", self.node_attestation)

        builder.set_entry_point("router")
        builder.add_edge("router", "authorization_gate")
        builder.add_edge("authorization_gate", "rag_retrieval")
        builder.add_edge("rag_retrieval", "investigation")
        builder.add_edge("investigation", "industrial_synthesis")
        builder.add_edge("industrial_synthesis", "verification_firewall")
        builder.add_edge("verification_firewall", "guardrail_formatter")
        builder.add_edge("guardrail_formatter", "attestation")
        builder.add_edge("attestation", END)

        return builder.compile()

    def run_pipeline(
        self,
        query: str,
        user_id: str = "user-01",
        role: str = "USER",
        workspace_id: str = "workspace-default",
    ) -> WorkbenchWorkflowState:
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        initial_state: WorkbenchWorkflowState = {
            "request_id": req_id,
            "query": query,
            "user_id": user_id,
            "role": role,
            "workspace_id": workspace_id,
            "network_profile": "STRICT_AIRGAP",
            "status": "INITIALIZED",
        }
        return self.graph.invoke(initial_state)
