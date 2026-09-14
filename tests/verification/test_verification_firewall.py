"""
Unit tests for Verification Subsystem & Hallucination Firewall.
"""

from src.verification.claim_extractor import ClaimExtractor
from src.verification.evidence_verifier import EvidenceVerifier, VerificationVerdict
from src.verification.confidence import ConfidenceScorer
from src.verification.causal_guard import CausalLeapGuard
from src.verification.guardrail_formatter import GuardrailFormatter


def test_claim_extractor():
    extractor = ClaimExtractor()
    text = "Refinery unit 4 pressure is normal at 145 PSI [chunk-01]. Temperature is elevated at 310 C [chunk-02]."
    claims = extractor.extract_claims(text)
    assert len(claims) == 2
    assert claims[0]["citations"] == ["chunk-01"]


def test_evidence_verifier():
    verifier = EvidenceVerifier()
    claims = [
        {"claim_id": "c1", "text": "Pressure is normal at 145 PSI.", "citations": ["chunk-01"]}
    ]
    evidence = [{"id": "chunk-01", "document": "Pressure reading PT-101 is 145.2 PSI normal."}]
    results = verifier.verify_claims(claims, evidence)
    assert len(results) == 1
    assert results[0]["verdict"] == VerificationVerdict.SUPPORTED.value
    assert results[0]["verification_score"] > 0.8


def test_confidence_scorer():
    results = [
        {"verdict": "SUPPORTED", "verification_score": 0.95},
        {"verdict": "SUPPORTED", "verification_score": 0.85},
    ]
    score = ConfidenceScorer.calculate_confidence(results)
    assert score == 0.9


def test_causal_guard():
    guard = CausalLeapGuard()
    text = "High temperature caused by valve failure."
    sanitized, flags = guard.audit_text(text, has_causal_proof=False)
    assert "caused by" not in sanitized
    assert "is correlated with" in sanitized
    assert len(flags) > 0


def test_guardrail_formatter():
    formatter = GuardrailFormatter()
    out = formatter.format_response(
        findings="Pressure is 145 PSI.",
        analysis="Observations derived from sensor telemetry.",
        uncertainty_items=["Minor telemetry noise."],
        confidence_score=0.92,
        evidence_citations=[{"id": "doc-1", "document": "Telemetry report"}],
    )
    assert "### 1. Verified Findings" in out
    assert "### 2. Analysis" in out
    assert "### 3. Uncertainty & Contradictions" in out
    assert "### 4. Confidence Score" in out
    assert "### 5. Evidence References" in out
    assert "92.0%" in out
