"""
MRPL AI Workbench — DuckDB Telemetry & Analytical Engine
Provides in-memory local telemetry correlation and aggregation queries
with strict read-only SQL safety validation.
"""

import logging
import re
from typing import Dict, Any, List, Optional
import duckdb

logger = logging.getLogger("MRPL.Analytics.DuckDB")


class SQLValidator:
    """
    Validates analytical SQL queries against destructive or non-sovereign commands.
    """

    FORBIDDEN_PATTERNS = [
        r"\bDROP\b",
        r"\bDELETE\b",
        r"\bUPDATE\b",
        r"\bINSERT\b",
        r"\bALTER\b",
        r"\bCREATE\b",
        r"\bTRUNCATE\b",
        r"\bATTACH\b",
        r"\bCOPY\b",
        r"\bINSTALL\b",
        r"\bLOAD\b",
        r"http://",
        r"https://",
    ]

    @classmethod
    def validate_query(cls, sql_query: str) -> bool:
        """
        Validate that query is read-only and free of forbidden patterns.

        Raises:
            ValueError: If query contains forbidden SQL constructs.
        """
        query_upper = sql_query.upper().strip()
        if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
            raise ValueError("[SQL SAFETY REJECT] Only SELECT or WITH read-only analytical queries are permitted.")

        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, query_upper):
                raise ValueError(f"[SQL SAFETY REJECT] Query contains forbidden keyword or pattern: '{pattern}'")
        return True


class DuckDBInvestigationEngine:
    """
    Local DuckDB in-memory analytical investigation engine.
    Used for correlating sensor telemetry, operational logs, and analytical metrics.
    """

    def __init__(self, database_path: str = ":memory:") -> None:
        self.conn = duckdb.connect(database=database_path)
        self._init_sample_schema()

    def _init_sample_schema(self) -> None:
        """Initialize in-memory refinery telemetry tables for local investigation."""
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS refinery_telemetry (
                    unit_id VARCHAR,
                    sensor_id VARCHAR,
                    timestamp TIMESTAMP,
                    pressure_psi DOUBLE,
                    temperature_c DOUBLE,
                    flow_rate DOUBLE,
                    status VARCHAR
                );
            """)
            # Insert baseline sample records if empty
            res = self.conn.execute("SELECT COUNT(*) FROM refinery_telemetry").fetchone()
            if res and res[0] == 0:
                self.conn.execute("""
                    INSERT INTO refinery_telemetry VALUES
                    ('UNIT-04', 'PT-101', NOW(), 145.2, 284.5, 520.0, 'NORMAL'),
                    ('UNIT-04', 'PT-102', NOW(), 144.8, 285.0, 518.5, 'NORMAL'),
                    ('UNIT-04', 'TT-201', NOW(), 160.5, 310.2, 490.0, 'ELEVATED');
                """)
        except Exception as exc:
            logger.warning(f"DuckDB schema init note: {exc}")

    def execute_analytical_query(self, sql_query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute read-only SQL analytical query.

        Args:
            sql_query: SQL statement to execute.
            params: Optional query parameters.

        Returns:
            List of result row dictionaries.
        """
        SQLValidator.validate_query(sql_query)
        logger.info(f"Executing approved DuckDB query: '{sql_query}'")
        rel = self.conn.execute(sql_query, params or [])
        columns = [desc[0] for desc in rel.description]
        rows = rel.fetchall()
        return [dict(zip(columns, row)) for row in rows]
