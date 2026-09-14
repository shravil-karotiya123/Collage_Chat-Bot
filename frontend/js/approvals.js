/**
 * Human Approval Center Module for MRPL Sovereign AI Workbench UI.
 */

const ApprovalsPage = {
  initialized: false,

  async load() {
    await this.fetchPendingApprovals();
  },

  async fetchPendingApprovals() {
    const container = document.getElementById('approvals-container');
    if (!container) return;

    try {
      container.innerHTML = `<p class="card-subtitle">Loading tasks requiring operator approval...</p>`;

      const data = await API.get('/agent/tasks');
      const allTasks = data.items || [];
      const pending = allTasks.filter(t => t.status === 'WAITING_FOR_APPROVAL' || t.agent_status === 'WAITING_FOR_APPROVAL');
      State.pendingApprovals = pending;

      if (!pending || pending.length === 0) {
        container.innerHTML = `
          <div class="card">
            <div class="card-header">
              <span class="card-title">Pending Governance Approvals</span>
              ${Utils.createBadge('healthy')}
            </div>
            <p class="card-subtitle">No agent tasks currently waiting for operator authorization.</p>
          </div>
        `;
        return;
      }

      const cardsHtml = pending.map(t => `
        <div class="card" style="border-color: var(--status-warning); margin-bottom: 20px;">
          <div class="card-header">
            <span class="card-title">Task ID: <code>${Utils.escapeHtml(t.task_id)}</code></span>
            ${Utils.createBadge('WAITING_FOR_APPROVAL')}
          </div>
          <div style="margin-bottom: 16px;">
            <p style="font-size: 1rem; color: var(--text-primary);">
              <strong>Requested Goal:</strong> ${Utils.escapeHtml(t.user_query)}
            </p>
            <div class="kv-list" style="margin-top: 10px;">
              <div class="kv-item"><span class="kv-label">Intent Tag</span><span class="kv-value">${Utils.escapeHtml(t.intent || 'GENERAL_CHAT')}</span></div>
              <div class="kv-item"><span class="kv-label">Selected Model</span><span class="kv-value">${Utils.escapeHtml(t.selected_model || 'qwen2.5:7b')}</span></div>
              <div class="kv-item"><span class="kv-label">Requested At</span><span class="kv-value">${Utils.formatDate(t.created_at)}</span></div>
            </div>
          </div>

          <div style="background-color: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 6px; border-left: 4px solid var(--status-warning); margin-bottom: 16px; font-size: 0.85rem;">
            ⚠ <strong>Governance Warning:</strong> Approval authorizes execution of the requested tool operations. High-risk tool calls will execute sequentially upon approval.
          </div>

          <div style="display: flex; gap: 12px;">
            <button class="btn btn-primary" onclick="ApprovalsPage.approveTask('${Utils.escapeHtml(t.task_id)}')">
              ✓ Approve & Execute Task
            </button>
            <button class="btn btn-danger" onclick="ApprovalsPage.rejectTask('${Utils.escapeHtml(t.task_id)}')">
              ✕ Reject Task
            </button>
          </div>
        </div>
      `).join('');

      container.innerHTML = cardsHtml;
    } catch (err) {
      container.innerHTML = `<p class="card-subtitle" style="color: var(--status-error);">Failed to fetch pending approvals (${Utils.escapeHtml(err.message)})</p>`;
    }
  },

  async approveTask(taskId) {
    if (!confirm(`Are you sure you want to APPROVE task '${taskId}' for execution?`)) return;

    try {
      await API.post(`/agent/approve/${encodeURIComponent(taskId)}`);
      Utils.showToast(`Task '${taskId}' APPROVED for execution!`);
      await this.fetchPendingApprovals();
    } catch (err) {
      Utils.showToast(`Approval failed: ${err.message}`, true);
    }
  },

  async rejectTask(taskId) {
    if (!confirm(`Are you sure you want to REJECT task '${taskId}'?`)) return;

    try {
      await API.post(`/agent/reject/${encodeURIComponent(taskId)}`);
      Utils.showToast(`Task '${taskId}' REJECTED.`);
      await this.fetchPendingApprovals();
    } catch (err) {
      Utils.showToast(`Rejection failed: ${err.message}`, true);
    }
  }
};

window.ApprovalsPage = ApprovalsPage;
