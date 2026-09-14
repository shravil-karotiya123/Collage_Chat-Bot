/**
 * Helper Utility Functions for MRPL Sovereign AI Workbench UI.
 */

const Utils = {
  /**
   * Escape HTML string safely to prevent XSS.
   */
  escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  /**
   * Format ISO date string into readable local timestamp.
   */
  formatDate(isoStr) {
    if (!isoStr) return 'N/A';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString();
    } catch {
      return String(isoStr);
    }
  },

  /**
   * Generate HTML markup for a status badge pill.
   */
  createBadge(status) {
    if (!status) return '<span class="badge badge-info">UNKNOWN</span>';
    const clean = String(status).toLowerCase();
    let badgeClass = 'badge-info';

    if (['healthy', 'pass', 'completed', 'success', 'ready'].includes(clean)) {
      badgeClass = 'badge-healthy';
    } else if (['warning', 'waiting_for_approval', 'running', 'pending', 'degraded'].includes(clean)) {
      badgeClass = 'badge-warning';
    } else if (['error', 'fail', 'failed', 'rejected', 'unhealthy'].includes(clean)) {
      badgeClass = 'badge-error';
    }

    return `<span class="badge ${badgeClass}">${this.escapeHtml(status)}</span>`;
  },

  /**
   * Toast notification display helper.
   */
  showToast(message, isError = false) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : ''}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.5s';
      setTimeout(() => toast.remove(), 500);
    }, 4000);
  }
};
