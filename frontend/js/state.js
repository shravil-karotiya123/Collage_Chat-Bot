/**
 * Reactive Application State Container for MRPL Sovereign AI Workbench UI.
 */

const State = {
  currentView: 'dashboard',
  theme: 'dark', // 'dark' or 'light'
  
  // Health & Posture
  systemHealth: null,
  offlineStatus: null,
  
  // Chat History
  chatMessages: [],
  
  // Documents & RAG
  documents: [],
  
  // Agents & Tasks
  agentTasks: [],
  pendingApprovals: [],
  
  listeners: [],

  subscribe(listener) {
    this.listeners.push(listener);
  },

  notify() {
    this.listeners.forEach(fn => fn(this));
  },

  setView(viewName) {
    this.currentView = viewName;
    this.notify();
  },

  setSystemHealth(healthData) {
    this.systemHealth = healthData;
    if (healthData && healthData.offline_status) {
      this.offlineStatus = healthData.offline_status;
    }
    this.notify();
  },

  setOfflineStatus(statusData) {
    this.offlineStatus = statusData;
    this.notify();
  }
};
