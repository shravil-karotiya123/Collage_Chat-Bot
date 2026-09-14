"""
Unit tests for StartupValidator component.
"""

from src.security.startup_validator import StartupValidator


def test_startup_validator():
    validator = StartupValidator()
    report = validator.run_startup_validation()

    assert "status" in report
    assert report["status"] in ("healthy", "degraded")
