"""
Idempotent Database Migrations and DDL Schema Definitions.
"""

import logging
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger("MRPL.Persistence.Migrations")


def run_migrations(conn: sqlite3.Connection, current_version: int, target_version: int) -> None:
    """
    Apply database schema migrations idempotently from current_version to target_version.
    """
    logger.info(f"Running database migrations from version {current_version} to {target_version}...")

    if current_version < 1:
        # Migration 1: Base Tables
        conn.executescript(
            """
            -- Agent Tasks Table
            CREATE TABLE IF NOT EXISTS agent_tasks (
                task_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                title TEXT NOT NULL,
                query TEXT NOT NULL,
                status TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                requires_approval INTEGER NOT NULL DEFAULT 0,
                approval_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                cancelled_at TEXT,
                failed_at TEXT,
                current_step INTEGER NOT NULL DEFAULT 0,
                total_steps INTEGER NOT NULL DEFAULT 0,
                retry_count INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 2,
                result_status TEXT NOT NULL DEFAULT 'PENDING',
                result_summary TEXT,
                error_code TEXT,
                error_message TEXT,
                recovery_status TEXT,
                metadata_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_user ON agent_tasks(user_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON agent_tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_created ON agent_tasks(created_at);
            CREATE INDEX IF NOT EXISTS idx_tasks_session ON agent_tasks(session_id);

            -- Agent Plans Table
            CREATE TABLE IF NOT EXISTS agent_plans (
                plan_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                plan_version INTEGER NOT NULL DEFAULT 1,
                intent TEXT NOT NULL,
                selected_model TEXT NOT NULL,
                total_tasks INTEGER NOT NULL DEFAULT 0,
                requires_approval INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                tasks_graph_json TEXT NOT NULL DEFAULT '[]',
                FOREIGN KEY (task_id) REFERENCES agent_tasks(task_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_plans_task ON agent_plans(task_id);

            -- Agent Executions Table
            CREATE TABLE IF NOT EXISTS agent_executions (
                execution_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                attempt_number INTEGER NOT NULL DEFAULT 1,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms REAL NOT NULL DEFAULT 0.0,
                safe_input_json TEXT NOT NULL DEFAULT '{}',
                safe_output_json TEXT NOT NULL DEFAULT '{}',
                result_excerpt TEXT,
                error_code TEXT,
                error_message TEXT,
                FOREIGN KEY (task_id) REFERENCES agent_tasks(task_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_exec_task ON agent_executions(task_id);
            CREATE INDEX IF NOT EXISTS idx_exec_tool ON agent_executions(tool_name);

            -- Agent Audit Events Table
            CREATE TABLE IF NOT EXISTS agent_audit_events (
                event_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                component TEXT NOT NULL,
                status TEXT NOT NULL,
                tool_name TEXT,
                risk_level TEXT,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                correlation_id TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_audit_task ON agent_audit_events(task_id);
            CREATE INDEX IF NOT EXISTS idx_audit_time ON agent_audit_events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_type ON agent_audit_events(event_type);
            """
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute("INSERT OR REPLACE INTO schema_info (version, installed_at) VALUES (1, ?);", (now_iso,))
        logger.info("Database migration v1 successfully applied.")
