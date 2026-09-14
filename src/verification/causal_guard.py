"""
MRPL AI Workbench — Causal Leap Guard Module
Prevents statistical correlation or telemetry observations from being stated as definitive causation.
"""

import re
from typing import Tuple, List


class CausalLeapGuard:
    """
    Sanitizes causal assertions when evidence indicates correlation rather than causation.
    """

    CAUSAL_KEYWORDS = [
        r"\bcaused by\b",
        r"\bdue to\b",
        r"\bproves that\b",
        r"\bresulted from\b",
        r"\bis caused by\b",
    ]

    def audit_text(self, text: str, has_causal_proof: bool = False) -> Tuple[str, List[str]]:
        """
        Scan and rewrite premature causal claims if causal proof is absent.
        """
        flags = []
        sanitized = text

        if not has_causal_proof:
            for pattern in self.CAUSAL_KEYWORDS:
                if re.search(pattern, text, re.IGNORECASE):
                    flags.append(f"Causal keyword detected without proof: '{pattern}'")
                    sanitized = re.sub(pattern, "is correlated with", sanitized, flags=re.IGNORECASE)

        return sanitized, flags
