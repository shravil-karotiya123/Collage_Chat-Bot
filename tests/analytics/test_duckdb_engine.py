"""
Unit tests for DuckDB Analytics & SQL Safety Validator.
"""

import pytest
from src.analytics.duckdb_engine import DuckDBInvestigationEngine, SQLValidator


def test_sql_validator():
    assert SQLValidator.validate_query("SELECT * FROM refinery_telemetry") is True
    assert SQLValidator.validate_query("WITH summary AS (SELECT count(*) FROM refinery_telemetry) SELECT * FROM summary") is True

    with pytest.raises(ValueError, match="SQL SAFETY REJECT"):
        SQLValidator.validate_query("DROP TABLE refinery_telemetry")

    with pytest.raises(ValueError, match="SQL SAFETY REJECT"):
        SQLValidator.validate_query("DELETE FROM refinery_telemetry WHERE unit_id = 'UNIT-04'")


def test_duckdb_investigation_engine():
    engine = DuckDBInvestigationEngine()
    rows = engine.execute_analytical_query("SELECT unit_id, pressure_psi FROM refinery_telemetry LIMIT 2")
    assert len(rows) > 0
    assert "unit_id" in rows[0]
    assert "pressure_psi" in rows[0]
