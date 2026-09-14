/**
 * Document Management Module for MRPL Sovereign AI Workbench UI.
 */

const DocumentsPage = {
  initialized: false,

  async load() {
    if (!this.initialized) {
      this.bindEvents();
      this.initialized = true;
    }
    await this.fetchDocumentList();
  },

  bindEvents() {
    const form = document.getElementById('document-upload-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.uploadDocument();
      });
    }
  },

  async uploadDocument() {
    const fileInput = document.getElementById('doc-file-input');
    const statusDiv = document.getElementById('upload-status-result');
    const submitBtn = document.getElementById('doc-upload-btn');

    if (!fileInput || !fileInput.files.length) {
      Utils.showToast('Please select a file to upload', true);
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      submitBtn.disabled = true;
      if (statusDiv) {
        statusDiv.innerHTML = `<p class="card-subtitle">Uploading & parsing document '${Utils.escapeHtml(file.name)}'...</p>`;
      }

      const res = await API.upload('/workbench/documents', formData);
      Utils.showToast(`Document '${file.name}' processed successfully!`);

      if (statusDiv) {
        statusDiv.innerHTML = `
          <div class="card" style="border-color: var(--status-success);">
            <div class="card-header">
              <span class="card-title">Document Ingestion Success</span>
              ${Utils.createBadge('SUCCESS')}
            </div>
            <div class="kv-list">
              <div class="kv-item"><span class="kv-label">Filename</span><span class="kv-value">${Utils.escapeHtml(res.filename)}</span></div>
              <div class="kv-item"><span class="kv-label">Document ID</span><span class="kv-value">${Utils.escapeHtml(res.document_id)}</span></div>
              <div class="kv-item"><span class="kv-label">Total Pages</span><span class="kv-value">${res.total_pages}</span></div>
              <div class="kv-item"><span class="kv-label">Indexed Chunks</span><span class="kv-value">${res.indexed_chunks_count}</span></div>
              <div class="kv-item"><span class="kv-label">Extraction Mode</span><span class="kv-value">${Utils.escapeHtml(res.extraction_mode)}</span></div>
            </div>
          </div>
        `;
      }

      fileInput.value = '';
      await this.fetchDocumentList();
    } catch (err) {
      if (statusDiv) {
        statusDiv.innerHTML = `
          <div class="card" style="border-color: var(--status-error);">
            <h4 style="color: var(--status-error);">Upload Failed</h4>
            <p class="card-subtitle">${Utils.escapeHtml(err.message)}</p>
          </div>
        `;
      }
      Utils.showToast(err.message, true);
    } finally {
      submitBtn.disabled = false;
    }
  },

  async fetchDocumentList() {
    const listContainer = document.getElementById('documents-list-container');
    if (!listContainer) return;

    try {
      const docs = await API.get('/documents');
      State.documents = docs;

      if (!docs || docs.length === 0) {
        listContainer.innerHTML = `<p class="card-subtitle">No documents currently uploaded or indexed.</p>`;
        return;
      }

      const rows = docs.map(d => `
        <tr>
          <td><strong>${Utils.escapeHtml(d.filename)}</strong></td>
          <td><code>${Utils.escapeHtml(d.document_id)}</code></td>
          <td>${d.total_chunks || d.indexed_chunks_count || 0}</td>
          <td>${Utils.formatDate(d.created_at)}</td>
          <td>
            <button class="btn btn-danger btn-sm" onclick="DocumentsPage.deleteDoc('${Utils.escapeHtml(d.document_id)}')">
              Delete
            </button>
          </td>
        </tr>
      `).join('');

      listContainer.innerHTML = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Document ID</th>
                <th>Chunks Indexed</th>
                <th>Uploaded At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {
      listContainer.innerHTML = `<p class="card-subtitle" style="color: var(--status-warning);">Could not load document list (${Utils.escapeHtml(err.message)})</p>`;
    }
  },

  async deleteDoc(documentId) {
    if (!confirm(`Are you sure you want to delete document '${documentId}' and purge its vector entries?`)) {
      return;
    }

    try {
      const res = await API.delete(`/documents/${encodeURIComponent(documentId)}`);
      Utils.showToast(`Deleted document '${documentId}' (${res.deleted_chunks_count || 0} chunks purged).`);
      await this.fetchDocumentList();
    } catch (err) {
      Utils.showToast(`Failed to delete document: ${err.message}`, true);
    }
  }
};

window.DocumentsPage = DocumentsPage;
