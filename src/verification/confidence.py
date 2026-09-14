"""
MRPL AI Workbench — Confidence Scorer Module
Calculates derived confidence score from evidence verification results.
"""

from typing import List, Dict, Any


class ConfidenceScorer:
    """
    Calculates non-fabricated confidence metric based on evidence support scores.
    """

    @staticmethod
    def calculate_confidence(verification_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall evidence-backed confidence score between 0.0 and 1.0.
        """
        if not verification_results:
            return 0.0

        total_score = 0.0
        for res in verification_results:
            verdict = res.get("verdict")
            score = res.get("verification_score", 0.0)

            if verdict == "CONTRADICTED":
                return 0.0  # Immediate zero confidence on contradiction
            total_score += score

        avg = total_score / len(verification_results)
        return round(min(max(avg, 0.0), 1.0), 4)
