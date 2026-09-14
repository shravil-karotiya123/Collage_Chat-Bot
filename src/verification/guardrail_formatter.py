"""
MRPL AI Workbench — 5-Section Guardrail Formatter Module
Renders operator-safe engineering responses formatted strictly into 5 required sections.
"""

from typing import Dict, Any, List


class GuardrailFormatter:
    """
    Formats release outputs into the mandatory 5-section engineering structure:
    1. Verified Findings
    2. Analysis (Observation vs Inference)
    3. Uncertainty & Contradictions
    4. Confidence Score
    5. Evidence References
    """

    def format_response(
        self,
        findings: str,
        analysis: str,
        uncertainty_items: List[str],
        confidence_score: float,
        evidence_citations: List[Dict[str, Any]],
    ) -> str:
        """
        Format response into standardized 5-section engineering report.
        """
        sections = []

        # Section 1: Verified Findings
        sections.append("### 1. Verified Findings")
        sections.append(findings.strip() if findings else "No verified findings extracted.")

        # Section 2: Analysis (Observation vs Inference)
        sections.append("\n### 2. Analysis")
        sections.append(analysis.strip() if analysis else "Observations distinguish verified data from model inference.")

        # Section 3: Uncertainty & Contradictions
        sections.append("\n### 3. Uncertainty & Contradictions")
        if uncertainty_items:
            for item in uncertainty_items:
                sections.append(f"- {item}")
        else:
            sections.append("No explicit evidence contradictions identified.")

        # Section 4: Confidence Score
        sections.append(f"\n### 4. Confidence Score")
        confidence_pct = round(confidence_score * 100, 2)
        sections.append(f"Derived Evidence Confidence: **{confidence_pct}%** ({confidence_score:.4f})")

        # Section 5: Evidence References
        sections.append("\n### 5. Evidence References")
        if evidence_citations:
            for c in evidence_citations:
                cid = c.get("id", "chunk")
                doc = c.get("document", "")[:80].replace("\n", " ")
                sections.append(f"- [{cid}] {doc}...")
        else:
            sections.append("No external evidence references appended.")

        return "\n".join(sections)
