/**
 * Authentication & Quick-Login Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('loginEmail').value;
      const password = document.getElementById('loginPassword').value;

      try {
        const res = await App.api('/api/auth/login', {
          method: 'POST',
          body: { email, password }
        });
        App.toast(res.message, 'success');
        setTimeout(() => {
          if (res.user.role === 'facilitator') {
            window.location.href = '/facilitator';
          } else {
            window.location.href = '/dashboard';
          }
        }, 500);
      } catch (err) {
        // handled
      }
    });
  }

  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('regName').value;
      const email = document.getElementById('regEmail').value;
      const password = document.getElementById('regPassword').value;
      const role = document.getElementById('regRole').value;

      try {
        const res = await App.api('/api/auth/register', {
          method: 'POST',
          body: { name, email, password, role }
        });
        App.toast('Registration successful! Directing to onboarding...', 'success');
        setTimeout(() => {
          if (role === 'student') {
            window.location.href = '/onboarding';
          } else {
            window.location.href = '/facilitator';
          }
        }, 600);
      } catch (err) {
        // handled
      }
    });
  }

  // Quick 1-click Demo Persona Logins
  document.querySelectorAll('.btn-quick-login').forEach(btn => {
    btn.addEventListener('click', async () => {
      const email = btn.getAttribute('data-email');
      try {
        const res = await App.api('/api/auth/login', {
          method: 'POST',
          body: { email, password: 'password123' }
        });
        App.toast(`Logged in as ${res.user.name}`, 'success');
        setTimeout(() => {
          if (res.user.role === 'facilitator') {
            window.location.href = '/facilitator';
          } else {
            window.location.href = '/dashboard';
          }
        }, 400);
      } catch (err) {
        // handled
      }
    });
  });
});
