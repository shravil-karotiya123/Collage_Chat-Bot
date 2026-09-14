/**
 * Audit Trail & Security Event Viewer Module for MRPL Sovereign AI Workbench UI.
 */

const AuditPage = {
  initialized: false,

  async load() {
    await this.fetchAuditLogs();
  },

  async fetchAuditLogs() {
    const container = document.getElementById('audit-container');
    if (!container) return;

    try {
      container.innerHTML = `<p class="card-subtitle">Loading audit logs and security telemetry events...</p>`;

      const secEvents = await API.get('/security/events').catch(() => []);
      const tasksData = await API.get('/agent/tasks').catch(() => ({ items: [] }));
      const tasks = tasksData.items || [];

      let allAuditRows = [];

      // Collect Security Events
      if (secEvents && secEvents.length > 0) {
        secEvents.forEach(e => {
          allAuditRows.push({
            timestamp: e.timestamp,
            task_id: e.request_id || 'SYSTEM',
            event_type: e.event_type,
            actor: e.actor_id || 'system',
            tool: 'SECURITY',
            status: e.severity || 'INFO',
            details: JSON.stringify(e.details || {})
          });
        });
      }

      // Collect Agent Task Trajectory Events
      for (const t of tasks.slice(0, 10)) {
        try {
          const events = await API.get(`/agent/tasks/${encodeURIComponent(t.task_id)}/audit`);
          if (events && events.length > 0) {
            events.forEach(e => {
              allAuditRows.push({
                timestamp: e.timestamp,
                task_id: e.task_id,
                event_type: e.event_type,
                actor: e.actor_id || 'agent',
                tool: e.tool_name || 'N/A',
                status: e.status,
                details: JSON.stringify(e.metadata || {})
              });
            });
          }
        } catch {
          // Ignore individual task audit fetch errors
        }
      }

      // Sort by timestamp descending
      allAuditRows.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

      if (allAuditRows.length === 0) {
        container.innerHTML = `<p class="card-subtitle">No audit events recorded yet.</p>`;
        return;
      }

      const rowsHtml = allAuditRows.map(r => `
        <tr>
          <td><small>${Utils.formatDate(r.timestamp)}</small></td>
          <td><code>${Utils.escapeHtml(r.task_id)}</code></td>
          <td><strong>${Utils.escapeHtml(r.event_type)}</strong></td>
          <td>${Utils.escapeHtml(r.actor)}</td>
          <td><code>${Utils.escapeHtml(r.tool)}</code></td>
          <td>${Utils.createBadge(r.status)}</td>
          <td><small style="color: var(--text-secondary); font-family: monospace;">${Utils.escapeHtml(r.details)}</small></td>
        </tr>
      `).join('');

      container.innerHTML = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Task / Req ID</th>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Component / Tool</th>
                <th>Status / Severity</th>
                <th>Sanitized Metadata</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<p class="card-subtitle" style="color: var(--status-error);">Failed to load audit logs (${Utils.escapeHtml(err.message)})</p>`;
    }
  }
};

window.AuditPage = AuditPage;
