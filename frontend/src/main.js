// CampusAI Assistant Client Logic (Vercel Ready)

// Endpoint State (Defaults to local or environment override)
let renderApiUrl = localStorage.getItem('RENDER_API_URL') || 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
  const apiInput = document.getElementById('render-api-input');
  const saveBtn = document.getElementById('save-endpoint-btn');
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const chatMessages = document.getElementById('chat-messages');
  
  const navTabs = document.querySelectorAll('.nav-tab');
  const viewChat = document.getElementById('view-chat');
  const viewInfo = document.getElementById('view-info');
  const infoContent = document.getElementById('info-view-content');
  const quickChips = document.getElementById('quick-chips-container');

  if (apiInput) apiInput.value = renderApiUrl;

  // 1. Health Check & Backend Connectivity
  async function checkBackendHealth() {
    try {
      statusText.textContent = 'Connecting to Render API...';
      const res = await fetch(`${renderApiUrl.replace(/\/$/, '')}/health`);
      if (res.ok) {
        statusDot.className = 'dot online';
        statusText.textContent = 'Render API Connected';
      } else {
        throw new Error('Non-200 Health Check');
      }
    } catch (err) {
      statusDot.className = 'dot offline';
      statusText.textContent = 'Local / Offline Mode';
    }
  }

  checkBackendHealth();

  // Save API Endpoint
  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      const val = apiInput.value.trim();
      if (val) {
        renderApiUrl = val;
        localStorage.setItem('RENDER_API_URL', renderApiUrl);
        checkBackendHealth();
      }
    });
  }

  // 2. Navigation Tabs
  navTabs.forEach((tab) => {
    tab.addEventListener('click', async () => {
      navTabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');

      const targetTab = tab.dataset.tab;
      if (targetTab === 'chat') {
        viewChat.classList.add('active');
        viewInfo.classList.remove('active');
      } else {
        viewChat.classList.remove('active');
        viewInfo.classList.add('active');
        await loadInfoTab(targetTab);
      }
    });
  });

  // 3. Render Information Tab Loader
  async function loadInfoTab(category) {
    infoContent.innerHTML = '<p style="color: var(--text-muted);">Loading information...</p>';
    try {
      const res = await fetch(`${renderApiUrl.replace(/\/$/, '')}/api/info/${category}`);
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      renderInfoCategory(category, data[category] || data);
    } catch (err) {
      // Fallback local mock data for client rendering preview
      renderLocalFallbackInfo(category);
    }
  }

  function renderInfoCategory(category, data) {
    let html = '';
    if (category === 'courses' && Array.isArray(data)) {
      html = data.map((c) => `
        <div class="info-card-item">
          <h3>${c.name}</h3>
          <p><strong>Duration:</strong> ${c.duration} | <strong>Intake:</strong> ${c.intake} seats</p>
          <p><strong>Eligibility:</strong> ${c.eligibility}</p>
          <p>${c.description}</p>
        </div>
      `).join('');
    } else if (category === 'admissions') {
      html = `
        <div class="info-card-item">
          <h3>${data.status}</h3>
          <p><strong>Application Deadline:</strong> ${data.deadline}</p>
          <p><strong>Scholarship Policy:</strong> ${data.scholarships}</p>
        </div>
      `;
    } else if (category === 'placements') {
      html = `
        <div class="info-card-item">
          <h3>Placement Record</h3>
          <p><strong>Highest Package:</strong> ${data.highest_package}</p>
          <p><strong>Average Package:</strong> ${data.average_package}</p>
          <p><strong>Placement Rate:</strong> ${data.placement_rate}</p>
          <p><strong>Top Recruiters:</strong> ${Array.isArray(data.top_recruiters) ? data.top_recruiters.join(', ') : ''}</p>
        </div>
      `;
    }
    infoContent.innerHTML = html || '<p>No records found.</p>';
  }

  function renderLocalFallbackInfo(category) {
    infoContent.innerHTML = `
      <div class="info-card-item">
        <h3>${category.toUpperCase()} Preview Mode</h3>
        <p>Connected to Vercel static fallback. Configure Render API endpoint in left sidebar to pull dynamic database records.</p>
      </div>
    `;
  }

  // 4. Chat Message Sending & Stream Handling
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';

    // Show Typing Indicator
    const typingId = appendTypingIndicator();

    try {
      const res = await fetch(`${renderApiUrl.replace(/\/$/, '')}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      removeTypingIndicator(typingId);

      if (res.ok) {
        const data = await res.json();
        appendMessage('system', data.reply);
      } else {
        throw new Error('API Response Error');
      }
    } catch (err) {
      removeTypingIndicator(typingId);
      // Client-side fallback response if backend service is waking up from Render free tier sleep
      appendMessage('system', `[CampusAI Local] ${getLocalBotReply(message)}`);
    }
  });

  // Quick Chips Click Event
  if (quickChips) {
    quickChips.addEventListener('click', (e) => {
      const btn = e.target.closest('.chip-btn');
      if (btn) {
        const q = btn.dataset.query;
        userInput.value = q;
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  }

  function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender === 'user' ? 'user-msg' : 'system-msg'}`;
    msgDiv.innerHTML = `
      <div class="avatar">${sender === 'user' ? '👤' : '🤖'}</div>
      <div class="bubble"><p>${text}</p></div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendTypingIndicator() {
    const id = 'typing-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.id = id;
    msgDiv.className = 'message system-msg';
    msgDiv.innerHTML = `
      <div class="avatar">🤖</div>
      <div class="bubble"><p><em>CampusAI is thinking...</em></p></div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function getLocalBotReply(msg) {
    const m = msg.toLowerCase();
    if (m.includes('course') || m.includes('b.tech')) {
      return "We offer B.Tech in Computer Science (AI/ML), Chemical Engineering, M.Tech Automation, and MBA Technology Management.";
    } else if (m.includes('admission') || m.includes('deadline')) {
      return "Admissions for 2026-2027 are currently open! Application deadline is July 15, 2026.";
    } else if (m.includes('placement') || m.includes('package')) {
      return "Our highest package is 45.0 LPA with an average package of 8.5 LPA (94.2% placement rate). Top recruiters include MRPL, TCS, Infosys, and Reliance.";
    }
    return "I am CampusAI. You can ask me about courses, fees, admissions, placements, or campus facilities!";
  }
});
