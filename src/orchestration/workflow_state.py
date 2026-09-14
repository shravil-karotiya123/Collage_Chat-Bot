"""
MRPL AI Workbench — LangGraph Typed State Module
Defines append-only typed state schema passed across pipeline nodes.
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict


class WorkbenchWorkflowState(TypedDict, total=False):
    """
    Typed workflow state passed deterministically through LangGraph pipeline nodes.
    """
    request_id: str
    user_id: str
    role: str
    workspace_id: str
    network_profile: str
    intent: str
    workflow_route: str
    authorization_scope: Dict[str, Any]
    query: str
    retrieved_chunk_ids: List[str]
    citations: List[Dict[str, Any]]
    approved_queries: List[str]
    analysis_results: Dict[str, Any]
    draft_response: str
    draft_claims: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    uncertainty_items: List[str]
    confidence_score: float
    final_response: str
    audit_event_ids: List[str]
    attestation_package: Optional[Dict[str, Any]]
    attestation_id: Optional[str]
    status: str
