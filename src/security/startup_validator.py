"""
Application Startup Offline Policy Validator.
Executes configuration and runtime endpoint posture checks on application launch.
"""

import logging
from typing import Dict, Any, Optional

from config.settings import settings
from src.security.offline_guard import OfflineGuard

logger = logging.getLogger("MRPL.Security.StartupValidator")


class StartupValidator:
    """
    Executes offline posture validation during FastAPI startup hook.
    """

    def __init__(self, offline_guard: Optional[OfflineGuard] = None) -> None:
        self.guard = offline_guard or OfflineGuard()

    def run_startup_validation(self) -> Dict[str, Any]:
        """
        Execute startup offline security checks.
        """
        logger.info("Executing startup air-gapped security posture validation...")
        if not settings.OFFLINE_VALIDATION_ENABLED:
            logger.info("Startup offline validation is disabled in settings.")
            return {"status": "DISABLED"}

        report = self.guard.validate_all()
        status = report["status"]

        if status == "healthy":
            logger.info("Startup offline posture validation PASSED. All endpoints and providers are 100% local.")
        elif status == "degraded":
            logger.warning(f"Startup offline posture validation DEGRADED: {report.get('checks')}")
        else:
            err_msg = f"CRITICAL: Startup offline posture validation FAILED: {report}"
            logger.critical(err_msg)
            if settings.OFFLINE_STRICT_MODE:
                raise RuntimeError(err_msg)

        return report
