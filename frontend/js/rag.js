/**
 * Knowledge Base & RAG Query Module for MRPL Sovereign AI Workbench UI.
 */

const RAGPage = {
  initialized: false,

  async load() {
    if (!this.initialized) {
      this.bindEvents();
      this.initialized = true;
    }
    await this.fetchRAGHealth();
  },

  bindEvents() {
    const btn = document.getElementById('rag-query-btn');
    if (btn) {
      btn.addEventListener('click', () => this.runQuery());
    }
  },

  async fetchRAGHealth() {
    const headerEl = document.getElementById('rag-status-header');
    if (!headerEl) return;

    try {
      const data = await API.get('/documents/rag/health');
      headerEl.innerHTML = `
        <div class="cards-grid">
          <div class="card">
            <span class="card-subtitle">Collection Name</span>
            <div class="card-metric">${Utils.escapeHtml(data.collection_name)}</div>
          </div>
          <div class="card">
            <span class="card-subtitle">Total Chunks Indexed</span>
            <div class="card-metric">${data.total_chunks_indexed}</div>
          </div>
          <div class="card">
            <span class="card-subtitle">Embedding Model</span>
            <div class="card-metric" style="font-size: 1.2rem;">${Utils.escapeHtml(data.embedding_provider?.model_name || 'all-MiniLM-L6-v2')}</div>
          </div>
        </div>
      `;
    } catch (err) {
      headerEl.innerHTML = `<p class="card-subtitle" style="color: var(--status-error);">RAG telemetry unavailable (${Utils.escapeHtml(err.message)})</p>`;
    }
  },

  async runQuery() {
    const queryEl = document.getElementById('rag-query-input');
    const topKEl = document.getElementById('rag-topk-select');
    const resultDiv = document.getElementById('rag-query-result');
    const btn = document.getElementById('rag-query-btn');

    if (!queryEl || !queryEl.value.trim()) {
      Utils.showToast('Please enter a query string', true);
      return;
    }

    const query = queryEl.value.trim();
    const topK = parseInt(topKEl ? topKEl.value : '3', 10);

    try {
      btn.disabled = true;
      if (resultDiv) {
        resultDiv.innerHTML = `<p class="card-subtitle">Retrieving grounded vector chunks...</p>`;
      }

      const res = await API.post('/documents/query', {
        query: query,
        top_k: topK
      });

      if (resultDiv) {
        let sourcesHtml = '';
        if (res.sources && res.sources.length > 0) {
          sourcesHtml = res.sources.map(s => `
            <div class="card" style="margin-bottom: 12px;">
              <div class="card-header">
                <span class="card-title">📄 ${Utils.escapeHtml(s.filename)} (Chunk ${s.chunk_id}, Page ${s.page || 1})</span>
                <span class="badge badge-info">Score: ${s.score ? s.score.toFixed(3) : 'N/A'}</span>
              </div>
              <p style="font-size: 0.9rem; color: var(--text-primary); margin-bottom: 8px;">
                ${Utils.escapeHtml(s.snippet || '')}
              </p>
              <div class="card-subtitle">Doc ID: ${Utils.escapeHtml(s.document_id)}</div>
            </div>
          `).join('');
        } else {
          sourcesHtml = `<p class="card-subtitle">No matching document chunks found above similarity threshold.</p>`;
        }

        resultDiv.innerHTML = `
          <div style="margin-top: 16px;">
            <h3>Grounded Answer (${Utils.escapeHtml(res.model_used)})</h3>
            <div class="card" style="margin: 12px 0; border-color: var(--accent-teal);">
              <div class="assistant-response-content">${Utils.renderMarkdown(res.answer)}</div>
            </div>
            <h4>Retrieved Source Passages:</h4>
            ${sourcesHtml}
          </div>
        `;
      }
    } catch (err) {
      if (resultDiv) {
        resultDiv.innerHTML = `
          <div class="card" style="border-color: var(--status-error);">
            <h4 style="color: var(--status-error);">RAG Query Error</h4>
            <p class="card-subtitle">${Utils.escapeHtml(err.message)}</p>
          </div>
        `;
      }
      Utils.showToast(err.message, true);
    } finally {
      btn.disabled = false;
    }
  }
};

window.RAGPage = RAGPage;
