"""
Unit tests for OfflineGuard component.
"""

from src.security.offline_guard import OfflineGuard


def test_offline_guard_validations():
    guard = OfflineGuard()

    # 1. Local endpoint check
    assert guard.is_local_endpoint("http://127.0.0.1:11434") is True
    assert guard.is_local_endpoint("http://localhost:11434") is True
    assert guard.is_local_endpoint("https://api.openai.com/v1") is False

    # 2. Subsystem posture checks
    ollama_res = guard.validate_ollama_endpoint()
    assert ollama_res["local"] is True
    assert ollama_res["status"] == "PASS"

    emb_res = guard.validate_embedding_provider()
    assert emb_res["local"] is True

    vstore_res = guard.validate_vector_store()
    assert vstore_res["local"] is True

    ocr_res = guard.validate_ocr_provider()
    assert ocr_res["local"] is True

    db_res = guard.validate_persistence()
    assert db_res["local"] is True

    # 3. Aggregate check
    all_res = guard.validate_all()
    assert all_res["status"] in ("healthy", "degraded")
    assert guard.is_offline_safe() is True
