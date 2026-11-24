/**
 * User / Citizen Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check auth
  const user = Auth.getUser();
  if (user) {
    const nameEl = document.getElementById('user-welcome-name');
    if (nameEl) nameEl.textContent = user.name || 'Citizen';
    const profileNameEl = document.getElementById('profile-name');
    if (profileNameEl) profileNameEl.textContent = user.name || 'Citizen';
    const profileRoleEl = document.getElementById('profile-role');
    if (profileRoleEl) profileRoleEl.textContent = user.area_name || 'Resident';
  }

  loadUserDashboardData();
  setupEventListeners();
});

async function loadUserDashboardData() {
  try {
    const res = await fetch('/api/water/dashboard/stats/');
    const data = await res.json();
    if (data.success) {
      updateDashboardUI(data);
    }
  } catch (err) {
    console.error('Failed to load user dashboard data:', err);
  }
}

function updateDashboardUI(data) {
  const stats = data.stats;

  // Water Availability
  const availEl = document.getElementById('stat-water-avail');
  if (availEl) availEl.textContent = `${stats.water_availability_percentage}%`;

  // Tank Level
  const tankEl = document.getElementById('stat-tank-level');
  if (tankEl) tankEl.textContent = `${stats.tank_level_percentage}%`;

  // Cylinder Gauge
  const cylinderFill = document.getElementById('cylinder-gauge-fill');
  if (cylinderFill) {
    cylinderFill.style.height = `${Math.min(100, stats.tank_level_percentage)}%`;
  }
  const cylinderPct = document.getElementById('cylinder-gauge-pct');
  if (cylinderPct) {
    cylinderPct.textContent = `${stats.tank_level_percentage}%`;
  }

  // Today's Usage
  const todayEl = document.getElementById('stat-today-usage');
  if (todayEl) todayEl.textContent = `${stats.today_usage_litres} L`;

  // Monthly Usage
  const monthEl = document.getElementById('stat-month-usage');
  if (monthEl) monthEl.textContent = `${stats.monthly_usage_litres} L`;

  // Unread notifications
  const notifEl = document.getElementById('notif-counter');
  if (notifEl) {
    notifEl.textContent = stats.unread_notifications || 0;
    notifEl.style.display = stats.unread_notifications > 0 ? 'flex' : 'none';
  }

  // Upcoming Distribution Schedule Table
  const schedBody = document.getElementById('upcoming-schedules-body');
  if (schedBody) {
    if (data.upcoming_schedules && data.upcoming_schedules.length > 0) {
      schedBody.innerHTML = data.upcoming_schedules.map(s => `
        <tr>
          <td><strong>${s.area_name}</strong></td>
          <td>${s.date}</td>
          <td><span style="font-family:var(--font-mono);font-size:0.85rem;">${s.time_slot}</span></td>
          <td><span class="badge badge-allocated">${s.status}</span></td>
        </tr>
      `).join('');
    } else {
      schedBody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:#94a3b8;padding:1.5rem;">No upcoming distribution scheduled yet.</td></tr>`;
    }
  }

  // Recent Requests Table
  const reqBody = document.getElementById('recent-requests-body');
  if (reqBody) {
    if (data.recent_requests && data.recent_requests.length > 0) {
      reqBody.innerHTML = data.recent_requests.map(r => {
        let badgeClass = 'badge-pending';
        if (r.status === 'ALLOCATED' || r.status === 'APPROVED') badgeClass = 'badge-allocated';
        if (r.status === 'REJECTED') badgeClass = 'badge-rejected';
        if (r.status === 'COMPLETED') badgeClass = 'badge-completed';

        return `
          <tr>
            <td>#${r.id}</td>
            <td><strong>${r.requested_quantity} L</strong></td>
            <td>${r.allocated_quantity > 0 ? r.allocated_quantity + ' L' : '-'}</td>
            <td>${r.request_date}</td>
            <td><span class="badge ${badgeClass}">${r.status}</span></td>
          </tr>
        `;
      }).join('');
    } else {
      reqBody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:1.5rem;">No requests submitted yet. Click [Request Water] to create one.</td></tr>`;
    }
  }
}

function setupEventListeners() {
  // Modal toggles
  const reqModal = document.getElementById('request-water-modal');
  const leakModal = document.getElementById('report-leakage-modal');

  window.openRequestModal = () => reqModal && reqModal.classList.add('active');
  window.closeRequestModal = () => reqModal && reqModal.classList.remove('active');

  window.openLeakageModal = () => leakModal && leakModal.classList.add('active');
  window.closeLeakageModal = () => leakModal && leakModal.classList.remove('active');

  // Submit Water Request Form
  const reqForm = document.getElementById('water-request-form');
  if (reqForm) {
    reqForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const qty = document.getElementById('req-quantity').value;
      const date = document.getElementById('req-date').value;
      const prio = document.getElementById('req-priority').value;
      const reason = document.getElementById('req-reason').value;

      try {
        const res = await fetch('/api/water/requests/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            requested_quantity: parseFloat(qty),
            request_date: date,
            priority: parseInt(prio),
            reason: reason
          })
        });
        const resp = await res.json();
        if (resp.success) {
          showToast('Water request submitted successfully! Awaiting allocation.', 'success');
          closeRequestModal();
          reqForm.reset();
          loadUserDashboardData();
        } else {
          showToast(resp.message || 'Error submitting request', 'danger');
        }
      } catch (err) {
        showToast('Error connecting to server', 'danger');
      }
    });
  }

  // Submit Leakage Report Form
  const leakForm = document.getElementById('leakage-report-form');
  if (leakForm) {
    leakForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const location = document.getElementById('leak-location').value;
      const desc = document.getElementById('leak-desc').value;
      const severity = document.getElementById('leak-severity').value;

      try {
        const res = await fetch('/api/leakage/reports/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: location,
            description: desc,
            severity: severity
          })
        });
        const resp = await res.json();
        if (resp.success) {
          showToast('Leakage report lodged! Maintenance dispatch alerted.', 'success');
          closeLeakageModal();
          leakForm.reset();
        } else {
          showToast('Failed to lodge leak report', 'danger');
        }
      } catch (err) {
        showToast('Error connecting to server', 'danger');
      }
    });
  }
}
