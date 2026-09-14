"""
Unit tests for Model Performance Benchmarking telemetry.
"""

from src.observability.benchmark import ModelBenchmarkManager, ModelPerformanceMetric


def test_model_benchmark_manager():
    mgr = ModelBenchmarkManager()
    data = mgr.get_latest_metrics()
    assert data["status"] == "OPERATIONAL"
    assert "qwen2.5:7b" in data["benchmarks"]
    assert "deepseek-coder:6.7b" in data["benchmarks"]
    assert "minicpm-v:8b" in data["benchmarks"]

    # Record metric
    metric = ModelPerformanceMetric(
        model_name="qwen2.5:7b",
        load_time_ms=1100.0,
        unload_time_ms=300.0,
        first_token_latency_ms=150.0,
        total_inference_time_ms=800.0,
        tokens_per_second=40.0,
        vram_usage_mb=5000.0,
        ram_usage_mb=2000.0,
        model_switch_time_ms=350.0,
    )
    mgr.record_metric(metric)

    data_after = mgr.get_latest_metrics()
    qwen_bench = data_after["benchmarks"]["qwen2.5:7b"]
    assert qwen_bench["measured"] is True
    assert qwen_bench["load_time_ms"] == 1100.0
    assert qwen_bench["tokens_per_second"] == 40.0
