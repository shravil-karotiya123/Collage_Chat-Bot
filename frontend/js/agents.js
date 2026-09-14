/**
 * Agent Task Console Module for MRPL Sovereign AI Workbench UI.
 */

const AgentsPage = {
  initialized: false,

  async load() {
    if (!this.initialized) {
      this.bindEvents();
      this.initialized = true;
    }
    await this.fetchTaskList();
  },

  bindEvents() {
    const form = document.getElementById('agent-task-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.createTask();
      });
    }
  },

  async createTask() {
    const queryEl = document.getElementById('agent-query-input');
    const submitBtn = document.getElementById('agent-submit-btn');

    if (!queryEl || !queryEl.value.trim()) {
      Utils.showToast('Please enter an agent prompt', true);
      return;
    }

    const prompt = queryEl.value.trim();

    try {
      submitBtn.disabled = true;
      const res = await API.post('/agent/tasks', { query: prompt });
      Utils.showToast(`Agent task '${res.task_id}' created! Status: ${res.agent_status}`);

      queryEl.value = '';
      await this.fetchTaskList();
    } catch (err) {
      Utils.showToast(`Failed to create task: ${err.message}`, true);
    } finally {
      submitBtn.disabled = false;
    }
  },

  async fetchTaskList() {
    const container = document.getElementById('agent-tasks-container');
    if (!container) return;

    try {
      const data = await API.get('/agent/tasks');
      const tasks = data.items || [];
      State.agentTasks = tasks;

      if (!tasks || tasks.length === 0) {
        container.innerHTML = `<p class="card-subtitle">No active or historical agent tasks found.</p>`;
        return;
      }

      const rows = tasks.map(t => `
        <tr>
          <td><code>${Utils.escapeHtml(t.task_id)}</code></td>
          <td>${Utils.escapeHtml(t.user_query)}</td>
          <td>${Utils.escapeHtml(t.intent || 'GENERAL_CHAT')}</td>
          <td>${Utils.escapeHtml(t.selected_model || 'qwen2.5:7b')}</td>
          <td>${Utils.createBadge(t.agent_status || t.status)}</td>
          <td>${Utils.formatDate(t.created_at)}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="AgentsPage.viewTaskDetails('${Utils.escapeHtml(t.task_id)}')">View</button>
            ${t.status === 'RUNNING' || t.status === 'WAITING_FOR_APPROVAL' ? `<button class="btn btn-danger btn-sm" onclick="AgentsPage.cancelTask('${Utils.escapeHtml(t.task_id)}')">Cancel</button>` : ''}
            ${t.status === 'INTERRUPTED' || t.status === 'FAILED' ? `<button class="btn btn-primary btn-sm" onclick="AgentsPage.resumeTask('${Utils.escapeHtml(t.task_id)}')">Resume</button>` : ''}
          </td>
        </tr>
      `).join('');

      container.innerHTML = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Task ID</th>
                <th>Query</th>
                <th>Intent</th>
                <th>Model</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>
        <div id="agent-detail-view" style="margin-top: 24px;"></div>
      `;
    } catch (err) {
      container.innerHTML = `<p class="card-subtitle" style="color: var(--status-error);">Could not load task list (${Utils.escapeHtml(err.message)})</p>`;
    }
  },

  async viewTaskDetails(taskId) {
    const detailDiv = document.getElementById('agent-detail-view');
    if (!detailDiv) return;

    try {
      detailDiv.innerHTML = `<p class="card-subtitle">Fetching task execution trajectory for '${Utils.escapeHtml(taskId)}'...</p>`;

      const task = await API.get(`/agent/tasks/${encodeURIComponent(taskId)}`);
      const timeline = await API.get(`/agent/tasks/${encodeURIComponent(taskId)}/timeline`).catch(() => []);

      let planStepsHtml = '';
      if (task.plan && task.plan.tasks) {
        planStepsHtml = task.plan.tasks.map((st, idx) => `
          <div class="plan-step-card">
            <div style="font-weight: 700; width: 30px;">#${idx + 1}</div>
            <div style="flex: 1;">
              <div><strong>Tool:</strong> <code>${Utils.escapeHtml(st.tool_name)}</code></div>
              <div class="card-subtitle">${Utils.escapeHtml(st.description || '')}</div>
            </div>
            <div>${Utils.createBadge(st.risk_level || 'LOW')}</div>
          </div>
        `).join('<div class="plan-step-arrow">↓</div>');
      }

      detailDiv.innerHTML = `
        <div class="card" style="border-color: var(--accent-teal);">
          <div class="card-header">
            <span class="card-title">Task Trajectory Detail: ${Utils.escapeHtml(task.task_id)}</span>
            ${Utils.createBadge(task.status)}
          </div>
          <div class="kv-list" style="margin-bottom: 16px;">
            <div class="kv-item"><span class="kv-label">Query</span><span class="kv-value">${Utils.escapeHtml(task.user_query)}</span></div>
            <div class="kv-item"><span class="kv-label">Approval Status</span><span class="kv-value">${Utils.escapeHtml(task.approval_status)}</span></div>
            <div class="kv-item"><span class="kv-label">Current Step</span><span class="kv-value">${task.current_step} / ${task.total_steps}</span></div>
          </div>

          <h4>Generated Execution Plan:</h4>
          <div class="plan-flow">
            ${planStepsHtml || '<p class="card-subtitle">No plan step graph available.</p>'}
          </div>
        </div>
      `;
    } catch (err) {
      detailDiv.innerHTML = `<p class="card-subtitle" style="color: var(--status-error);">Failed to load details (${Utils.escapeHtml(err.message)})</p>`;
    }
  },

  async resumeTask(taskId) {
    try {
      await API.post(`/agent/tasks/${encodeURIComponent(taskId)}/resume`);
      Utils.showToast(`Task '${taskId}' resumed successfully.`);
      await this.fetchTaskList();
    } catch (err) {
      Utils.showToast(`Resume failed: ${err.message}`, true);
    }
  },

  async cancelTask(taskId) {
    try {
      await API.post(`/agent/tasks/${encodeURIComponent(taskId)}/cancel`);
      Utils.showToast(`Task '${taskId}' cancelled.`);
      await this.fetchTaskList();
    } catch (err) {
      Utils.showToast(`Cancel failed: ${err.message}`, true);
    }
  }
};

window.AgentsPage = AgentsPage;
