/**
 * Unified Chat & Grounded QA Module for MRPL Sovereign AI Workbench UI.
 */

const ChatPage = {
  initialized: false,

  load() {
    if (!this.initialized) {
      this.bindEvents();
      this.initialized = true;
    }
  },

  bindEvents() {
    const sendBtn = document.getElementById('chat-send-btn');
    const inputEl = document.getElementById('chat-input');
    const clearBtn = document.getElementById('chat-clear-btn');

    if (sendBtn && inputEl) {
      sendBtn.addEventListener('click', () => this.sendMessage());
      inputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearChat());
    }
  },

  clearChat() {
    State.chatMessages = [];
    const container = document.getElementById('chat-messages-container');
    if (container) {
      container.innerHTML = `
        <div class="message-bubble assistant">
          Hello! I am the MRPL Sovereign AI Assistant. How can I assist you today?
        </div>
      `;
    }
  },

  async sendMessage() {
    const inputEl = document.getElementById('chat-input');
    const forceRagEl = document.getElementById('chat-force-rag');
    const sendBtn = document.getElementById('chat-send-btn');
    const container = document.getElementById('chat-messages-container');

    if (!inputEl || !container) return;
    const query = inputEl.value.trim();
    if (!query) return;

    const forceRag = forceRagEl ? forceRagEl.checked : false;

    // Append User Message
    this.appendMessage('user', query);
    inputEl.value = '';

    // Disable button & show loading indicator
    sendBtn.disabled = true;
    const loadingBubble = this.appendLoadingBubble();

    try {
      const payload = {
        query: query,
        force_rag: forceRag,
        top_k: 3
      };

      const res = await API.post('/workbench/chat', payload);
      loadingBubble.remove();

      this.appendAssistantResponse(res);
    } catch (err) {
      loadingBubble.remove();
      this.appendErrorMessage(err.message || 'Failed to process chat turn');
      Utils.showToast(err.message, true);
    } finally {
      sendBtn.disabled = false;
    }
  },

  appendMessage(role, text) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = `message-bubble ${role}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  },

  appendLoadingBubble() {
    const container = document.getElementById('chat-messages-container');
    const div = document.createElement('div');
    div.className = 'message-bubble assistant';
    div.innerHTML = `<div class="spinner"></div> Model inference in progress...`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  },

  appendAssistantResponse(res) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'message-bubble assistant';

    let answerHtml = `<div class="assistant-response-content">${Utils.renderMarkdown(res.answer)}</div>`;

    if (res.status === 'FALLBACK_NO_CONTEXT') {
      answerHtml = `
        <div style="color: var(--status-warning); font-weight: 600; margin-bottom: 8px;">
          ⚠ No sufficient document context was found.
        </div>
        <div class="assistant-response-content">${Utils.renderMarkdown(res.answer)}</div>
      `;
    }

    let citationsHtml = '';
    if (res.sources && res.sources.length > 0) {
      citationsHtml = `
        <div class="citation-list">
          <strong>Source Citations (${res.sources.length}):</strong>
          ${res.sources.map(s => `
            <div class="citation-item">
              📄 <strong>${Utils.escapeHtml(s.filename)}</strong> (Page ${s.page || 1}, Chunk ${s.chunk_id})
              ${s.snippet ? `<br><small style="color: var(--text-muted);">${Utils.escapeHtml(s.snippet)}</small>` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }

    const metaHtml = `
      <div class="message-meta">
        <span>Intent: <strong>${Utils.escapeHtml(res.intent)}</strong></span>
        <span>Model: <strong>${Utils.escapeHtml(res.selected_model)}</strong></span>
        <span>Grounded: <strong>${res.grounded_in_docs ? 'YES' : 'NO'}</strong></span>
        <span>Time: <strong>${res.execution_time_seconds ? res.execution_time_seconds.toFixed(2) : 0}s</strong></span>
      </div>
    `;

    div.innerHTML = answerHtml + citationsHtml + metaHtml;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  appendErrorMessage(errMsg) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'message-bubble assistant';
    div.style.borderColor = 'var(--status-error)';
    div.innerHTML = `
      <div style="color: var(--status-error); font-weight: 600;">Error</div>
      <div>${Utils.escapeHtml(errMsg)}</div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }
};

window.ChatPage = ChatPage;
