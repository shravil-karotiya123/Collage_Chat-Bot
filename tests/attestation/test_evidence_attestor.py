"""
Unit tests for Ed25519 Evidence Attestor.
"""

from src.attestation.evidence_attestor import EvidenceAttestor


def test_evidence_attestor_signature_verification():
    attestor = EvidenceAttestor()
    proof = attestor.create_proof_package(
        request_id="req-999-test",
        response_text="Verified findings: Pressure PT-101 is 145 PSI normal.",
        citations=["chunk-01", "chunk-02"],
    )

    assert proof["version"] == "1.0"
    assert proof["proof_type"] == "Ed25519_CLORA_PROOF"
    assert "signature" in proof
    assert "public_key" in proof

    # Verify offline using public key
    is_valid = EvidenceAttestor.verify_proof_package(proof)
    assert is_valid is True

    # Test tampering detection
    tampered_proof = dict(proof)
    tampered_proof["payload"] = dict(proof["payload"])
    tampered_proof["payload"]["canonical_fingerprint"] = "tampered_hash_value"
    assert EvidenceAttestor.verify_proof_package(tampered_proof) is False
