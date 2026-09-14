"""
Code generation & sandbox execution service interface definition.
"""

from typing import Any, Dict


class CodeService:
    """
    Service layer contract for code synthesis, safety inspection, and sandbox execution.
    """

    async def generate_code(self, specification: str, language: str = "python") -> str:
        """
        Contract for generating code snippets via specialized local coding models.
        """
        raise NotImplementedError("Service interface contract only.")

    async def execute_code_in_sandbox(self, code: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Contract for safely executing Python code inside isolated sandbox subprocesses.
        """
        raise NotImplementedError("Service interface contract only.")
