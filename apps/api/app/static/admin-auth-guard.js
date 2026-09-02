(() => {
  async function validateAdminToken() {
    const t = localStorage.getItem('stayhub_admin_token');
    if (!t) return false;
    try {
      const r = await fetch('/users/me', { headers: { Authorization: `Bearer ${t}` } });
      const u = await r.json().catch(() => ({}));
      if (!r.ok || u.role !== 'admin') throw new Error('Admin access required');
      return true;
    } catch (e) {
      localStorage.removeItem('stayhub_admin_token');
      const loginView = document.getElementById('loginView');
      const portal = document.getElementById('portal');
      if (portal) portal.classList.add('hidden');
      if (loginView) loginView.classList.remove('hidden');
      const error = document.getElementById('error');
      if (error) error.textContent = 'This account is not a StayHub Admin account.';
      return false;
    }
  }

  window.login = async function () {
    try {
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const b = new URLSearchParams();
      b.append('username', email);
      b.append('password', password);
      b.append('grant_type', 'password');
      const r = await fetch('/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: b
      });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || 'Login failed');
      const me = await fetch('/users/me', { headers: { Authorization: `Bearer ${d.access_token}` } });
      const u = await me.json().catch(() => ({}));
      if (!me.ok || u.role !== 'admin') throw new Error('This account is not a StayHub Admin account.');
      token = d.access_token;
      localStorage.setItem('stayhub_admin_token', token);
      document.getElementById('error').textContent = '';
      document.getElementById('loginView').classList.add('hidden');
      document.getElementById('portal').classList.remove('hidden');
      await loadAll();
      await loadPending();
      // The enhanced admin-property-operations module initializes on
      // DOMContentLoaded, which has already fired by the time an interactive
      // login normally happens. Re-dispatch it so the enhanced dashboard,
      // including Pending Properties, initializes immediately after login.
      document.dispatchEvent(new Event('DOMContentLoaded'));
    } catch (e) {
      localStorage.removeItem('stayhub_admin_token');
      document.getElementById('error').textContent = e.message;
    }
  };

  validateAdminToken().then(ok => {
    if (!ok) return;
  });
})();
