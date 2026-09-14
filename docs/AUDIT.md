# MRPL AI Workbench — SHA-256 Audit Ledger & Evidence Attestation

## Audit & Provenance Architecture

The platform combines **hash-chained audit logging** for execution traceability with **Ed25519 digital signatures** for offline artifact verification.

---

## 1. SHA-256 Tamper-Evident Chained Audit Ledger

All operational workflow events are appended to a local JSONL audit ledger (`data/audit/airgap_proof_log.jsonl`).

Each event entry is cryptographically linked to the previous entry:

```text
Event 1:
  previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"
  current_hash  = SHA-256(Event 1 Payload + previous_hash)

Event 2:
  previous_hash = current_hash(Event 1)
  current_hash  = SHA-256(Event 2 Payload + previous_hash)
```

If any historical record in `airgap_proof_log.jsonl` is altered or deleted, recalculating the SHA-256 hash chain immediately reveals the exact line of tampering.

---

## 2. Ed25519 Digital Evidence Attestation

When an engineering report or compliance note is finalized, the Evidence Attestor generates an exported proof package (`.clora-proof`):

### Proof Package Structure

```json
{
  "request_id": "req-98234-abcd",
  "timestamp": "2026-09-13T16:44:00Z",
  "canonical_fingerprint": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "signature": "ed25519:7f8a9b...",
  "public_key_id": "mrpl-key-01",
  "citations": ["doc-442-chunk-01", "doc-442-chunk-04"]
}
```

- **Private Key**: Generated locally during setup, stored in secure local configuration, and **never transmitted over any network connection**.
- **Verification**: Third-party auditors can verify the `.clora-proof` package completely offline using the public key.
