/**
 * AdaptiveLearn AI - Global Application Controller & Helpers
 */

const App = {
  api: async (endpoint, options = {}) => {
    const defaults = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    const config = { ...defaults, ...options };
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }
    try {
      const response = await fetch(endpoint, config);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `HTTP error ${response.status}`);
      }
      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      App.toast(err.message, 'error');
      throw err;
    }
  },

  toast: (message, type = 'info') => {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'error' ? '❌' : (type === 'success' ? '✅' : '💡');
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  initPersonaSwitcher: () => {
    const select = document.getElementById('globalPersonaSelect');
    if (!select) return;

    select.addEventListener('change', async (e) => {
      const userId = e.target.value;
      try {
        const res = await App.api('/api/auth/switch-demo-user', {
          method: 'POST',
          body: { user_id: parseInt(userId) }
        });
        App.toast(res.message, 'success');
        setTimeout(() => {
          if (res.user.role === 'facilitator') {
            window.location.href = '/facilitator';
          } else {
            window.location.href = '/dashboard';
          }
        }, 600);
      } catch (err) {
        // error handled
      }
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.initPersonaSwitcher();
});
