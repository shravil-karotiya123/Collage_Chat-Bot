"""
Agent Planner Module.
Generates deterministic task execution graphs (AgentPlan) based on intent classification and request context.
Connects with Intelligent Model Router. Strips internal model chain-of-thought.
"""

from abc import ABC, abstractmethod
import logging
import uuid
from typing import Any, Dict, Optional

from src.agents.agent_plan import AgentPlan
from src.agents.agent_task import AgentTask
from src.agents.agent_types import AgentStatus, ApprovalStatus, ToolRiskLevel
from src.routing.base_router import BaseRouter
from src.routing.intent_classifier import UserIntent
from src.routing.router_factory import RouterFactory

logger = logging.getLogger("MRPL.Agents.Planner")


class BasePlanner(ABC):
    """
    Abstract Base Class for Agent Planners.
    """

    @abstractmethod
    def plan(
        self,
        query: str,
        document_id: Optional[str] = None,
        force_rag: bool = False,
        top_k: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentPlan:
        pass


class WorkbenchPlanner(BasePlanner):
    """
    Deterministic Agent Planner for MRPL AI Workbench.
    Maps intent classification outcomes to ordered task graphs.
    """

    EXTERNAL_ACTION_KEYWORDS = {
        "send", "email", "post", "dispatch", "transmit", "notify", "publish", "share with management"
    }

    def __init__(self, router: Optional[BaseRouter] = None) -> None:
        self.router = router or RouterFactory.create_router()

    def plan(
        self,
        query: str,
        document_id: Optional[str] = None,
        force_rag: bool = False,
        top_k: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentPlan:
        """
        Generate deterministic AgentPlan for input query.

        Args:
            query: User text prompt.
            document_id: Optional document ID for RAG context.
            force_rag: Explicit toggle requesting RAG retrieval.
            top_k: Optional vector retrieval top_k limit.
            context: Context dictionary payload.

        Returns:
            AgentPlan instance.
        """
        ctx = context or {}
        req_id = ctx.get("request_id") or f"req_{uuid.uuid4().hex[:10]}"
        plan_id = f"plan_{uuid.uuid4().hex[:10]}"
        cleaned_query = (query or "").strip()

        # Route query through Intelligent Model Router to classify intent
        route_res = self.router.route(cleaned_query, context=ctx)
        intent_tag = route_res.intent

        tasks = []
        requires_approval = False

        # Intent Mapping & Deterministic Graph Construction
        if intent_tag == UserIntent.DOCUMENT or force_rag or document_id is not None:
            # Multi-step RAG Workflow: Step 1 (Retrieve) -> Step 2 (Answer)
            t1_id = f"task_{uuid.uuid4().hex[:8]}"
            t2_id = f"task_{uuid.uuid4().hex[:8]}"

            t1 = AgentTask(
                task_id=t1_id,
                description=f"Retrieve document context for query: {cleaned_query[:60]}",
                task_type="RAG_RETRIEVAL",
                tool_name="rag_tool",
                parameters={"query": cleaned_query, "document_id": document_id, "top_k": top_k},
                risk_level=ToolRiskLevel.LOW,
            )

            t2 = AgentTask(
                task_id=t2_id,
                description="Generate grounded answer from retrieved document context",
                task_type="GROUNDED_ANSWER",
                tool_name="chat_tool",
                dependencies=[t1_id],
                parameters={"query": cleaned_query, "context": {"use_previous_task_result": t1_id}},
                risk_level=ToolRiskLevel.LOW,
            )
            tasks = [t1, t2]
            reasoning_summary = "Retrieve relevant document context via vector store, then synthesize a grounded response."

        elif intent_tag == UserIntent.APPROVAL_NOTE:
            # Approval Note Workflow
            requires_rag_step = bool(document_id or force_rag or "document" in cleaned_query.lower() or "file" in cleaned_query.lower())
            
            t1_id = None
            if requires_rag_step:
                t1_id = f"task_{uuid.uuid4().hex[:8]}"
                t1 = AgentTask(
                    task_id=t1_id,
                    description="Retrieve background context for approval note generation",
                    task_type="RAG_RETRIEVAL",
                    tool_name="rag_tool",
                    parameters={"query": cleaned_query, "document_id": document_id, "top_k": top_k},
                    risk_level=ToolRiskLevel.LOW,
                )
                tasks.append(t1)

            t2_id = f"task_{uuid.uuid4().hex[:8]}"
            t2_deps = [t1_id] if t1_id else []
            t2 = AgentTask(
                task_id=t2_id,
                description="Generate formal approval note draft using Qwen local LLM",
                task_type="APPROVAL_NOTE_GEN",
                tool_name="chat_tool",
                dependencies=t2_deps,
                parameters={"query": cleaned_query},
                risk_level=ToolRiskLevel.LOW,
            )
            tasks.append(t2)

            # Check if external side-effect is requested in query
            is_external_action_requested = any(kw in cleaned_query.lower() for kw in self.EXTERNAL_ACTION_KEYWORDS)
            if is_external_action_requested:
                t3_id = f"task_{uuid.uuid4().hex[:8]}"
                t3 = AgentTask(
                    task_id=t3_id,
                    description="Transmit approved note to external management recipient",
                    task_type="EXTERNAL_COMMUNICATION",
                    tool_name="external_communication_tool",
                    dependencies=[t2_id],
                    parameters={"query": cleaned_query},
                    approval_required=True,
                    approval_status=ApprovalStatus.PENDING,
                    risk_level=ToolRiskLevel.HIGH,
                )
                tasks.append(t3)
                requires_approval = True
                reasoning_summary = "Retrieve background context, generate approval note draft, and await approval before sending external notification."
            else:
                reasoning_summary = "Retrieve background context if available and generate formal approval note draft."

        elif intent_tag in (UserIntent.CODING, UserIntent.DEBUGGING):
            t1_id = f"task_{uuid.uuid4().hex[:8]}"
            t1 = AgentTask(
                task_id=t1_id,
                description=f"Synthesize code using DeepSeek Coder 6.7B for query: {cleaned_query[:60]}",
                task_type="CODE_GENERATION",
                tool_name="coding_tool",
                parameters={"query": cleaned_query, "context": ctx},
                risk_level=ToolRiskLevel.LOW,
            )
            tasks = [t1]
            reasoning_summary = "Route software engineering prompt to DeepSeek Coder model for generation."

        elif intent_tag in (UserIntent.IMAGE, UserIntent.OCR, UserIntent.DIAGRAM):
            t1_id = f"task_{uuid.uuid4().hex[:8]}"
            t1 = AgentTask(
                task_id=t1_id,
                description="Perform multimodal vision/OCR inspection using MiniCPM-V 8B",
                task_type="VISION_INSPECTION",
                tool_name="vision_tool",
                parameters={"query": cleaned_query, "context": ctx},
                risk_level=ToolRiskLevel.LOW,
            )
            tasks = [t1]
            reasoning_summary = "Inspect image or diagram using MiniCPM-V visual language model."

        else:
            # GENERAL_CHAT / SUMMARIZATION / UNKNOWN Fallback
            t1_id = f"task_{uuid.uuid4().hex[:8]}"
            t1 = AgentTask(
                task_id=t1_id,
                description=f"Process general reasoning prompt: {cleaned_query[:60]}",
                task_type="GENERAL_REASONING",
                tool_name="chat_tool",
                parameters={"query": cleaned_query, "context": ctx},
                risk_level=ToolRiskLevel.LOW,
            )
            tasks = [t1]
            reasoning_summary = "Process general query using Qwen 2.5 7B LLM."

        plan = AgentPlan(
            plan_id=plan_id,
            request_id=req_id,
            objective=cleaned_query,
            tasks=tasks,
            status=AgentStatus.CREATED,
            reasoning_summary=reasoning_summary,
            requires_approval=requires_approval,
        )

        logger.info(
            f"[PLANNER] Created plan '{plan_id}' for request '{req_id}' | "
            f"intent={intent_tag} | task_count={len(tasks)} | requires_approval={requires_approval}"
        )

        return plan
