# MRPL AI Workbench — Hardware Optimization & Memory Strategy

## Targeted Hardware Profile

The MRPL AI Workbench is optimized specifically for workstation deployment with the following resource limits:

- **Processor**: Multi-core Intel Core i7 / AMD Ryzen 7
- **GPU**: NVIDIA RTX 5050 (~8 GB VRAM)
- **System Memory**: 16 GB RAM
- **Storage**: SSD Storage (`data/` directory)

---

## Single-Model Memory Strategy

To operate reliably within 16 GB system RAM and ~8 GB GPU VRAM, the workbench enforces a **strict single-model loading lifecycle**:

```text
User Request Received
       ↓
Identify Target Model (Qwen2.5-7B / Qwen2.5-Coder-7B / Qwen2.5-VL-3B)
       ↓
Evict Unused Model from VRAM
       ↓
Load Target Model into VRAM
       ↓
Execute Inference
       ↓
Unload / Evict Model & Release VRAM
```

### Key Principles

1. **Never Load Models Simultaneously**: Never load Qwen, Coder, and Vision models into VRAM concurrently.
2. **Lazy Loading**: Models are loaded on demand and immediately evicted after request execution.
3. **Lightweight Embeddings**: Local `SentenceTransformers` embeddings (`all-MiniLM-L6-v2`) occupy ~80 MB RAM.
4. **Bounded Caching**: Vector database queries and DuckDB analytical contexts use bounded memory pools.
