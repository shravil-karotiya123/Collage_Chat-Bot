"""
MRPL AI Workbench — Ed25519 Evidence Attestor Module
Generates and verifies Ed25519 digital proof packages (.clora-proof) for offline auditability.
"""

import base64
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger("MRPL.Attestation")


class EvidenceAttestor:
    """
    Ed25519 digital signature generator for engineering proof packages.
    """

    def __init__(self, private_key_pem: Optional[str] = None) -> None:
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"),
                password=None,
            )
        else:
            # Generate local Ed25519 keypair
            self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def get_public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def create_proof_package(
        self,
        request_id: str,
        response_text: str,
        citations: Optional[list] = None,
        key_id: str = "mrpl-local-key-01",
    ) -> Dict[str, Any]:
        """
        Generate canonical payload, compute SHA-256 fingerprint, and sign with local Ed25519 key.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        fingerprint = hashlib.sha256(response_text.encode("utf-8")).hexdigest()

        canonical_payload = {
            "request_id": request_id,
            "timestamp": timestamp,
            "canonical_fingerprint": fingerprint,
            "citations": citations or [],
            "key_id": key_id,
        }

        canonical_bytes = json.dumps(canonical_payload, sort_keys=True).encode("utf-8")
        signature_bytes = self.private_key.sign(canonical_bytes)
        signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")
        public_key_b64 = base64.b64encode(self.get_public_key_bytes()).decode("utf-8")

        proof_package = {
            "version": "1.0",
            "proof_type": "Ed25519_CLORA_PROOF",
            "payload": canonical_payload,
            "signature": signature_b64,
            "public_key": public_key_b64,
        }
        return proof_package

    @staticmethod
    def verify_proof_package(proof_package: Dict[str, Any]) -> bool:
        """
        Verify an exported proof package offline using the embedded public key and signature.
        """
        try:
            payload = proof_package.get("payload", {})
            sig_b64 = proof_package.get("signature", "")
            pub_b64 = proof_package.get("public_key", "")

            canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
            sig_bytes = base64.b64decode(sig_b64)
            pub_bytes = base64.b64decode(pub_b64)

            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            public_key.verify(sig_bytes, canonical_bytes)
            return True
        except Exception as exc:
            logger.warning(f"Proof package signature verification failed: {exc}")
            return False
