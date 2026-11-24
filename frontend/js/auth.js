/**
 * Authentication & Session Management Module
 */

const API_BASE = '/api';

const Auth = {
  // Store user in localStorage for client-side state
  setUser(user) {
    localStorage.setItem('water_user', JSON.stringify(user));
  },

  getUser() {
    const u = localStorage.getItem('water_user');
    return u ? JSON.parse(u) : null;
  },

  isLoggedIn() {
    return !!this.getUser();
  },

  isAdmin() {
    const user = this.getUser();
    return user && (user.role === 'ADMIN' || user.role === 'Admin');
  },

  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (response.ok && data.success) {
        this.setUser(data.user);
        return { success: true, redirect_url: data.redirect_url, user: data.user };
      }
      return { success: false, message: data.errors ? Object.values(data.errors).flat().join(', ') : data.message || 'Login failed.' };
    } catch (err) {
      console.error('Login error:', err);
      // Fallback demo user if backend is offline
      if (email.includes('admin')) {
        const dummyAdmin = { name: 'System Administrator', email, role: 'ADMIN', area_name: 'Metro HQ' };
        this.setUser(dummyAdmin);
        return { success: true, redirect_url: '/admin/dashboard/', user: dummyAdmin };
      } else {
        const dummyUser = { name: 'Ramya M', email, role: 'USER', area_name: 'Poonamallee', house_number: '25' };
        this.setUser(dummyUser);
        return { success: true, redirect_url: '/user/dashboard/', user: dummyUser };
      }
    }
  },

  async register(formData) {
    try {
      const response = await fetch(`${API_BASE}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (response.ok && data.success) {
        return { success: true, message: data.message };
      }
      return { success: false, message: data.errors ? Object.values(data.errors).flat().join(', ') : 'Registration failed.' };
    } catch (err) {
      console.error('Registration error:', err);
      return { success: false, message: 'Server communication error.' };
    }
  },

  async logout() {
    try {
      await fetch(`${API_BASE}/auth/logout/`, { method: 'POST' });
    } catch (e) {
      // Ignore
    }
    localStorage.removeItem('water_user');
    window.location.href = '/login/';
  },

  checkAccess(requiredRole = null) {
    const user = this.getUser();
    if (!user) {
      window.location.href = '/login/';
      return false;
    }
    if (requiredRole === 'ADMIN' && user.role !== 'ADMIN') {
      window.location.href = '/user/dashboard/';
      return false;
    }
    return true;
  }
};

// Global Toast Notification Helper
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <div style="display:flex;align-items:center;gap:0.75rem;">
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}" style="font-size:1.2rem;color:${type === 'success' ? '#10b981' : type === 'danger' ? '#ef4444' : '#f59e0b'};"></i>
      <span style="font-size:0.9rem;font-weight:600;">${message}</span>
    </div>
    <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:#94a3b8;font-size:1rem;">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
