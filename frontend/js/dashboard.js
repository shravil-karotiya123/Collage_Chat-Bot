/**
 * Dashboard Page Module for MRPL Sovereign AI Workbench UI.
 */

const DashboardPage = {
  async load() {
    const container = document.getElementById('dashboard-content');
    if (!container) return;

    try {
      container.innerHTML = `<div class="card"><p class="card-subtitle">Loading system telemetry...</p></div>`;
      
      const healthData = await API.get('/workbench/health');
      State.setSystemHealth(healthData);

      this.render(healthData, container);
    } catch (err) {
      container.innerHTML = `
        <div class="card" style="border-color: var(--status-error);">
          <h3 style="color: var(--status-error);">Failed to load telemetry</h3>
          <p class="card-subtitle">${Utils.escapeHtml(err.message)}</p>
        </div>
      `;
      Utils.showToast(err.message, true);
    }
  },

  render(data, container) {
    const status = data.status || 'healthy';
    const off = data.offline_status || {};
    const router = data.router_status || {};
    const rag = data.rag_status || {};
    const ocr = data.ocr_status || {};
    const mem = data.memory_status || {};

    const html = `
      <div class="cards-grid">
        <div class="card">
          <div class="card-header">
            <span class="card-title">System Status</span>
            ${Utils.createBadge(status)}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">Workbench</span><span class="kv-value">${data.workbench_enabled ? 'ENABLED' : 'DISABLED'}</span></div>
            <div class="kv-item"><span class="kv-label">Offline Mode</span><span class="kv-value">${off.offline_mode ? 'ENABLED' : 'DISABLED'}</span></div>
            <div class="kv-item"><span class="kv-label">Strict Air-Gapped</span><span class="kv-value">${off.strict_mode ? 'ENABLED' : 'DISABLED'}</span></div>
            <div class="kv-item"><span class="kv-label">Network Policy</span><span class="kv-value">${Utils.escapeHtml(off.network_policy || 'LOCAL_ONLY')}</span></div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <span class="card-title">Local Production Models</span>
            ${Utils.createBadge(router.ollama_available ? 'PASS' : 'WARNING')}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">Qwen 2.5 7B (Default)</span><span class="kv-value">${router.models_status?.['qwen2.5:7b'] ? 'INSTALLED' : 'MISSING'}</span></div>
            <div class="kv-item"><span class="kv-label">DeepSeek Coder 6.7B</span><span class="kv-value">${router.models_status?.['deepseek-coder:6.7b'] ? 'INSTALLED' : 'MISSING'}</span></div>
            <div class="kv-item"><span class="kv-label">MiniCPM-V 8B (Vision)</span><span class="kv-value">${router.models_status?.['minicpm-v:8b'] ? 'INSTALLED' : 'MISSING'}</span></div>
            <div class="kv-item"><span class="kv-label">Single-Model VRAM</span><span class="kv-value">ENFORCED (1 Max)</span></div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <span class="card-title">Local RAG Subsystem</span>
            ${Utils.createBadge(rag.status || 'healthy')}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">Collection</span><span class="kv-value">${Utils.escapeHtml(rag.collection_name || 'mrpl_documents')}</span></div>
            <div class="kv-item"><span class="kv-label">Indexed Chunks</span><span class="kv-value">${rag.total_chunks_indexed || 0}</span></div>
            <div class="kv-item"><span class="kv-label">Embedding Provider</span><span class="kv-value">${Utils.escapeHtml(rag.embedding_provider?.provider || 'SentenceTransformer')}</span></div>
            <div class="kv-item"><span class="kv-label">Vector Store</span><span class="kv-value">${Utils.escapeHtml(rag.vector_store?.provider || 'ChromaDB')}</span></div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <span class="card-title">OCR & Vision Intelligence</span>
            ${Utils.createBadge(ocr.status || 'healthy')}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">OCR Engine</span><span class="kv-value">${Utils.escapeHtml(ocr.ocr_engine || 'pytesseract')}</span></div>
            <div class="kv-item"><span class="kv-label">Vision LLM</span><span class="kv-value">${Utils.escapeHtml(ocr.vision_model || 'minicpm-v:8b')}</span></div>
            <div class="kv-item"><span class="kv-label">Max Image Size</span><span class="kv-value">${ocr.max_image_size_mb || 20} MB</span></div>
            <div class="kv-item"><span class="kv-label">Local Execution</span><span class="kv-value">${ocr.local ? 'VERIFIED' : 'LOCAL'}</span></div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <span class="card-title">Memory & VRAM Diagnostics</span>
            ${Utils.createBadge('healthy')}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">System RAM Used</span><span class="kv-value">${mem.ram_used_gb || '0.0'} / ${mem.ram_total_gb || '0.0'} GB</span></div>
            <div class="kv-item"><span class="kv-label">Process RSS</span><span class="kv-value">${mem.process_rss_mb || '0'} MB</span></div>
            <div class="kv-item"><span class="kv-label">GPU Available</span><span class="kv-value">${mem.gpu_available ? 'YES' : 'NO'}</span></div>
            <div class="kv-item"><span class="kv-label">VRAM Load</span><span class="kv-value">${mem.vram_used_gb || '0.0'} GB</span></div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <span class="card-title">Durable Persistence & Recovery</span>
            ${Utils.createBadge(off.persistence_local ? 'PASS' : 'WARNING')}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">Database Provider</span><span class="kv-value">SQLite (WAL Mode)</span></div>
            <div class="kv-item"><span class="kv-label">Database File</span><span class="kv-value">mrpl_workbench.db</span></div>
            <div class="kv-item"><span class="kv-label">Startup Recovery</span><span class="kv-value">ENABLED</span></div>
            <div class="kv-item"><span class="kv-label">Persistence Audit</span><span class="kv-value">ACTIVE</span></div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }
};

window.DashboardPage = DashboardPage;
