"""
Agent Task State Machine Validator.
Enforces deterministic task lifecycle transitions and protects terminal state immutability.
"""

import logging
from typing import Set

from src.agents.agent_types import AgentStatus
from src.persistence.exceptions import InvalidTaskStateError

logger = logging.getLogger("MRPL.Agents.StateMachine")


class TaskStateMachine:
    """
    State machine enforcing valid agent task lifecycle transitions.
    """

    VALID_TRANSITIONS = {
        AgentStatus.CREATED: {AgentStatus.PLANNING, AgentStatus.FAILED, AgentStatus.CANCELLED},
        AgentStatus.PLANNING: {
            AgentStatus.WAITING_FOR_APPROVAL,
            AgentStatus.APPROVED,
            AgentStatus.FAILED,
            AgentStatus.CANCELLED,
        },
        AgentStatus.WAITING_FOR_APPROVAL: {
            AgentStatus.APPROVED,
            AgentStatus.REJECTED,
            AgentStatus.CANCELLED,
        },
        AgentStatus.APPROVED: {
            AgentStatus.RUNNING,
            AgentStatus.EXECUTING,
            AgentStatus.CANCELLED,
            AgentStatus.FAILED,
        },
        AgentStatus.EXECUTING: {
            AgentStatus.COMPLETED,
            AgentStatus.FAILED,
            AgentStatus.CANCELLED,
            AgentStatus.INTERRUPTED,
            AgentStatus.RUNNING,
        },
        AgentStatus.RUNNING: {
            AgentStatus.COMPLETED,
            AgentStatus.FAILED,
            AgentStatus.CANCELLED,
            AgentStatus.INTERRUPTED,
            AgentStatus.EXECUTING,
        },
        AgentStatus.INTERRUPTED: {
            AgentStatus.RUNNING,
            AgentStatus.EXECUTING,
            AgentStatus.WAITING_FOR_APPROVAL,
            AgentStatus.APPROVED,
            AgentStatus.FAILED,
            AgentStatus.CANCELLED,
        },
        # Terminal States
        AgentStatus.COMPLETED: set(),
        AgentStatus.REJECTED: set(),
        AgentStatus.CANCELLED: set(),
        AgentStatus.FAILED: {AgentStatus.PLANNING, AgentStatus.RUNNING, AgentStatus.EXECUTING},  # Explicit retry exception
    }

    TERMINAL_STATES = {AgentStatus.COMPLETED, AgentStatus.REJECTED, AgentStatus.CANCELLED}

    @classmethod
    def can_transition(cls, current_state: AgentStatus, new_state: AgentStatus) -> bool:
        """Check if transition from current_state to new_state is permitted."""
        if current_state == new_state:
            return True  # Idempotent state touch is allowed
        allowed = cls.VALID_TRANSITIONS.get(current_state, set())
        return new_state in allowed

    @classmethod
    def validate_transition(cls, task_id: str, current_state: AgentStatus, new_state: AgentStatus) -> None:
        """Validate state transition, raising InvalidTaskStateError if forbidden."""
        if not cls.can_transition(current_state, new_state):
            logger.warning(f"Forbidden task state transition rejected: {task_id} [{current_state} -> {new_state}]")
            raise InvalidTaskStateError(
                task_id=task_id,
                current_state=current_state.value,
                requested_state=new_state.value,
            )
