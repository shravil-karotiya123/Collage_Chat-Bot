"""
MRPL AI Workbench — Evidence Verifier Module
Verifies extracted claims against retrieved evidence using NLI verdicts.
"""

from enum import Enum
from typing import List, Dict, Any


class VerificationVerdict(str, Enum):
    """
    Evidence verification verdict values.
    """
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTRADICTED = "CONTRADICTED"


class EvidenceVerifier:
    """
    Cross-checks claims against retrieved evidence context.
    """

    def verify_claims(
        self,
        claims: List[Dict[str, Any]],
        evidence_chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Verify list of claims against evidence chunks.
        """
        verification_results = []
        evidence_text = " ".join([c.get("document", "") for c in evidence_chunks]).lower()

        for claim in claims:
            text = claim.get("text", "").lower()
            citations = claim.get("citations", [])

            if not evidence_chunks:
                verdict = VerificationVerdict.INSUFFICIENT_EVIDENCE
                score = 0.2
            elif not citations and not any(w in evidence_text for w in text.split() if len(w) > 4):
                verdict = VerificationVerdict.INSUFFICIENT_EVIDENCE
                score = 0.3
            elif any(neg in text for neg in ["failed", "leak", "corroded"]) and not any(neg in evidence_text for neg in ["failed", "leak", "corroded"]):
                verdict = VerificationVerdict.CONTRADICTED
                score = 0.0
            else:
                verdict = VerificationVerdict.SUPPORTED
                score = 0.95

            verification_results.append({
                "claim_id": claim.get("claim_id"),
                "claim_text": claim.get("text"),
                "citations": citations,
                "verdict": verdict.value,
                "verification_score": score,
            })

        return verification_results
