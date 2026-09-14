"""
Approval Gate Subsystem for MRPL AI Workbench.
Evaluates agent tasks and plans against governance policies to enforce human-in-the-loop gates.
"""

import logging
from typing import Dict, Any

from src.agents.agent_plan import AgentPlan
from src.agents.agent_task import AgentTask
from src.agents.agent_types import ApprovalStatus, ToolRiskLevel
from src.agents.policies import AgentPolicy

logger = logging.getLogger("MRPL.Agents.ApprovalGate")


class ApprovalGate:
    """
    Evaluates whether tasks or plans require explicit human approval before execution.
    """

    def __init__(self, policy: AgentPolicy = None) -> None:
        self.policy = policy or AgentPolicy()

    def evaluate_task(self, task: AgentTask, policy: AgentPolicy = None) -> ApprovalStatus:
        """
        Evaluate single task approval requirement.

        Args:
            task: AgentTask instance.
            policy: Optional policy override.

        Returns:
            ApprovalStatus enum (NOT_REQUIRED or PENDING).
        """
        pol = policy or self.policy

        # Check explicit task approval flag
        if task.approval_required:
            logger.info(f"[APPROVAL GATE] Task '{task.task_id}' requires approval (flag set).")
            return ApprovalStatus.PENDING

        # Check policy evaluation for risk level or tool name
        if pol.is_approval_required(task.tool_name, task.risk_level):
            logger.info(
                f"[APPROVAL GATE] Task '{task.task_id}' tool '{task.tool_name}' "
                f"risk '{task.risk_level.value}' requires approval by policy."
            )
            return ApprovalStatus.PENDING

        return ApprovalStatus.NOT_REQUIRED

    def evaluate_plan(self, plan: AgentPlan, policy: AgentPolicy = None) -> bool:
        """
        Evaluate full plan. Updates task and plan approval fields.

        Returns:
            True if at least one task in the plan requires approval.
        """
        pol = policy or self.policy
        plan_requires_approval = False

        for task in plan.tasks:
            status = self.evaluate_task(task, pol)
            if status == ApprovalStatus.PENDING:
                task.approval_required = True
                task.approval_status = ApprovalStatus.PENDING
                plan_requires_approval = True
            else:
                task.approval_status = ApprovalStatus.NOT_REQUIRED

        plan.requires_approval = plan_requires_approval
        return plan_requires_approval
