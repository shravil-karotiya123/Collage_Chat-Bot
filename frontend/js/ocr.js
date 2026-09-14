/**
 * OCR & Vision Inspection Module for MRPL Sovereign AI Workbench UI.
 */

const OCRPage = {
  initialized: false,

  async load() {
    if (!this.initialized) {
      this.bindEvents();
      this.initialized = true;
    }
    await this.fetchOCRHealth();
  },

  bindEvents() {
    const form = document.getElementById('ocr-upload-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.processOCR();
      });
    }
  },

  async fetchOCRHealth() {
    const healthDiv = document.getElementById('ocr-health-panel');
    if (!healthDiv) return;

    try {
      const data = await API.get('/ocr/health');
      healthDiv.innerHTML = `
        <div class="card">
          <div class="card-header">
            <span class="card-title">OCR & Vision Health Status</span>
            ${Utils.createBadge(data.status)}
          </div>
          <div class="kv-list">
            <div class="kv-item"><span class="kv-label">OCR Engine</span><span class="kv-value">${Utils.escapeHtml(data.ocr_engine)}</span></div>
            <div class="kv-item"><span class="kv-label">Vision Model</span><span class="kv-value">${Utils.escapeHtml(data.vision_model)}</span></div>
            <div class="kv-item"><span class="kv-label">Local Execution</span><span class="kv-value">${data.local ? 'VERIFIED' : 'LOCAL'}</span></div>
          </div>
        </div>
      `;
    } catch (err) {
      healthDiv.innerHTML = `<p class="card-subtitle" style="color: var(--status-error);">OCR health check failed (${Utils.escapeHtml(err.message)})</p>`;
    }
  },

  async processOCR() {
    const fileInput = document.getElementById('ocr-file-input');
    const promptInput = document.getElementById('ocr-prompt-input');
    const resultDiv = document.getElementById('ocr-result-panel');
    const submitBtn = document.getElementById('ocr-submit-btn');

    if (!fileInput || !fileInput.files.length) {
      Utils.showToast('Please select an image or scanned file', true);
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    if (promptInput && promptInput.value.trim()) {
      formData.append('prompt', promptInput.value.trim());
    }

    try {
      submitBtn.disabled = true;
      if (resultDiv) {
        resultDiv.innerHTML = `<p class="card-subtitle">Executing OCR and visual analysis on '${Utils.escapeHtml(file.name)}'...</p>`;
      }

      const res = await API.upload('/ocr/process', formData);

      if (resultDiv) {
        resultDiv.innerHTML = `
          <div class="card" style="border-color: var(--accent-teal);">
            <div class="card-header">
              <span class="card-title">OCR Analysis Result: ${Utils.escapeHtml(res.filename || file.name)}</span>
              ${Utils.createBadge(res.extraction_mode || 'TEXT')}
            </div>
            <div class="kv-list" style="margin-bottom: 16px;">
              <div class="kv-item"><span class="kv-label">Page Classification</span><span class="kv-value">${Utils.escapeHtml(res.page_type || 'MIXED')}</span></div>
              <div class="kv-item"><span class="kv-label">Characters Extracted</span><span class="kv-value">${res.total_characters || 0}</span></div>
              <div class="kv-item"><span class="kv-label">Confidence Score</span><span class="kv-value">${res.confidence ? res.confidence.toFixed(2) : '1.00'}</span></div>
            </div>
            <h4>Extracted Text Content:</h4>
            <div class="card" style="background-color: var(--bg-primary); margin-top: 8px; white-space: pre-wrap; font-family: monospace;">
              ${Utils.escapeHtml(res.extracted_text || 'No text extracted.')}
            </div>
          </div>
        `;
      }

      fileInput.value = '';
    } catch (err) {
      if (resultDiv) {
        resultDiv.innerHTML = `
          <div class="card" style="border-color: var(--status-error);">
            <h4 style="color: var(--status-error);">OCR Processing Failed</h4>
            <p class="card-subtitle">${Utils.escapeHtml(err.message)}</p>
          </div>
        `;
      }
      Utils.showToast(err.message, true);
    } finally {
      submitBtn.disabled = false;
    }
  }
};

window.OCRPage = OCRPage;
