"""
Agentic System Enumerations and Strongly Typed Constants.
Defines AgentStatus, TaskStatus, ApprovalStatus, and ToolRiskLevel.
"""

from enum import Enum


class AgentStatus(str, Enum):
    """
    Lifecycle status of an Agent run request.
    """

    CREATED = "CREATED"
    PLANNING = "PLANNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"


class TaskStatus(str, Enum):
    """
    Status of an individual AgentTask in a plan execution graph.
    """

    PENDING = "PENDING"
    READY = "READY"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    REJECTED = "REJECTED"


class ApprovalStatus(str, Enum):
    """
    Status of human/governance approval gate evaluation.
    """

    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ToolRiskLevel(str, Enum):
    """
    Risk severity classification for tool execution.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
