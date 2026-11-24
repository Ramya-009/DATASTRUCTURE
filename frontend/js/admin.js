/**
 * Admin Command Center Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check Admin access
  Auth.checkAccess('ADMIN');

  loadAdminSummary();
  setupAdminModals();
});

async function loadAdminSummary() {
  try {
    const res = await fetch('/api/reports/summary/');
    const data = await res.json();
    if (data.success) {
      updateAdminDashboardUI(data);
    }
  } catch (err) {
    console.error('Failed to load admin summary:', err);
  }
}

function updateAdminDashboardUI(data) {
  const s = data.summary;

  // Stat counters (Section 10)
  document.getElementById('admin-total-users').textContent = Number(s.total_users).toLocaleString();
  document.getElementById('admin-active-users').textContent = Number(s.active_users).toLocaleString();
  document.getElementById('admin-pending-reqs').textContent = s.pending_requests;
  document.getElementById('admin-avail-water').textContent = `${Number(s.available_water_litres).toLocaleString()} L`;

  // Request status counts
  const pendingEl = document.getElementById('count-pending');
  if (pendingEl) pendingEl.textContent = s.pending_requests;
  const approvedEl = document.getElementById('count-approved');
  if (approvedEl) approvedEl.textContent = s.approved_requests;
  const rejectedEl = document.getElementById('count-rejected');
  if (rejectedEl) rejectedEl.textContent = s.rejected_requests;
  const completedEl = document.getElementById('count-completed');
  if (completedEl) completedEl.textContent = s.completed_requests;

  // Render Tanks Grid (Section 11)
  const tanksGrid = document.getElementById('admin-tanks-grid');
  if (tanksGrid && data.tanks) {
    tanksGrid.innerHTML = data.tanks.map(t => {
      let statusColor = '#10b981';
      if (t.percentage < 50) statusColor = '#f59e0b';
      if (t.percentage < 25) statusColor = '#ef4444';

      return `
        <div class="card tank-visual-card">
          <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
            <span style="font-weight:700;font-size:0.85rem;color:var(--primary-600);font-family:var(--font-mono);">${t.tank_id}</span>
            <span class="badge ${t.status === 'ACTIVE' ? 'badge-allocated' : 'badge-rejected'}">${t.status}</span>
          </div>
          <div class="cylinder-gauge-wrapper">
            <div class="cylinder-water-fill" style="height: ${Math.min(100, t.percentage)}%;"></div>
          </div>
          <div class="gauge-percentage-badge">${t.percentage}%</div>
          <h4 style="font-size:0.95rem;margin:0.25rem 0 0.15rem 0;">${t.name}</h4>
          <p style="font-size:0.75rem;color:var(--text-muted);">${t.location}</p>
          <div style="font-size:0.8rem;margin-top:0.5rem;font-weight:600;color:var(--text-main);">
            ${Number(t.current_level).toLocaleString()} / ${Number(t.capacity).toLocaleString()} L
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Charts (Section 38)
  if (data.charts) {
    Charts.renderConsumptionChart('admin-trend-chart', data.charts.trend_labels, data.charts.trend_consumption);
    
    if (data.tanks) {
      const names = data.tanks.map(t => t.tank_id);
      const caps = data.tanks.map(t => t.capacity);
      const curs = data.tanks.map(t => t.current_level);
      Charts.renderTankComparisonChart('admin-tank-comparison-chart', names, caps, curs);
    }

    if (data.charts.area_labels) {
      Charts.renderAreaDoughnutChart('admin-area-doughnut', data.charts.area_labels, data.charts.area_quota);
    }
  }
}

function setupAdminModals() {
  const algoModal = document.getElementById('run-algorithm-modal');
  const leakModal = document.getElementById('test-leakage-modal');

  window.openAlgorithmModal = () => algoModal && algoModal.classList.add('active');
  window.closeAlgorithmModal = () => algoModal && algoModal.classList.remove('active');

  window.openLeakTestModal = () => leakModal && leakModal.classList.add('active');
  window.closeLeakTestModal = () => leakModal && leakModal.classList.remove('active');

  // Trigger C Distribution Algorithm (Section 12, 14, 15, 16)
  window.executeDistributionAlgorithm = async () => {
    const btn = document.getElementById('btn-execute-algo');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running C Priority Queue & Graph Engine...';
    }

    try {
      const res = await fetch('/api/distribution/run-algorithm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (data.success) {
        showToast(data.message, 'success');
        renderAlgorithmResults(data);
        loadAdminSummary();
      } else {
        showToast(data.message || 'Algorithm execution failed', 'danger');
      }
    } catch (err) {
      showToast('Error executing C algorithm', 'danger');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-bolt"></i> Run C Allocation Algorithm';
      }
    }
  };

  // Run Anomaly Leakage Test (Section 34)
  window.testLeakageAnomaly = async () => {
    const tankOut = parseFloat(document.getElementById('sim-tank-output').value || 10000);
    const areaIn = parseFloat(document.getElementById('sim-area-input').value || 7800);
    const threshold = parseFloat(document.getElementById('sim-threshold').value || 8);

    try {
      const res = await fetch('/api/leakage/detect-anomaly/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tank_output_litres: tankOut,
          area_received_litres: areaIn,
          threshold_percentage: threshold
        })
      });
      const data = await res.json();
      if (data.success) {
        const a = data.analysis;
        const resBox = document.getElementById('anomaly-result-box');
        if (resBox) {
          resBox.style.display = 'block';
          resBox.innerHTML = `
            <div style="padding:1.25rem;border-radius:var(--radius-md);background:${a.is_leak_detected ? '#fef2f2' : '#f0fdf4'};border:1px solid ${a.is_leak_detected ? '#fecaca' : '#bbf7d0'};">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
                <span style="font-weight:800;color:${a.is_leak_detected ? '#dc2626' : '#16a34a'};font-size:1.05rem;">
                  <i class="fas fa-${a.is_leak_detected ? 'triangle-exclamation' : 'circle-check'}"></i>
                  ${a.is_leak_detected ? 'LEAKAGE ANOMALY DETECTED!' : 'NORMAL PIPELINE FLOW'}
                </span>
                <span class="badge ${a.is_leak_detected ? 'badge-emergency' : 'badge-allocated'}">${a.severity}</span>
              </div>
              <div style="font-size:0.88rem;color:#334155;line-height:1.6;">
                <strong>Output:</strong> ${a.tank_output_litres} L | <strong>Received:</strong> ${a.area_received_litres} L<br>
                <strong>Unaccounted Loss:</strong> ${a.loss_litres} L (${a.loss_percentage}%)<br>
                <strong>Permissible Threshold:</strong> ${a.threshold_percentage}%<br>
                <strong>Engine:</strong> ${a.engine}
              </div>
            </div>
          `;
        }
      }
    } catch (e) {
      showToast('Error testing anomaly detection', 'danger');
    }
  };
}

function renderAlgorithmResults(data) {
  const container = document.getElementById('algo-results-container');
  if (!container) return;
  container.style.display = 'block';

  const sum = data.summary;
  const results = data.results;

  const prioNames = ['', 'Emergency', 'Hospital', 'Essential', 'Household', 'Commercial', 'Low'];

  container.innerHTML = `
    <div class="card" style="margin-top:1.5rem;border-color:var(--primary-300);">
      <div class="card-header">
        <h3 class="card-title"><i class="fas fa-microchip text-cyan"></i> C Engine Execution Audit</h3>
        <span class="c-tag">${data.engine_used}</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.25rem;">
        <div style="background:#f8fafc;padding:0.75rem;border-radius:var(--radius-sm);text-align:center;">
          <div style="font-size:0.75rem;color:var(--text-muted);">Demanded Water</div>
          <div style="font-size:1.1rem;font-weight:800;">${sum.total_demanded_water} L</div>
        </div>
        <div style="background:#f8fafc;padding:0.75rem;border-radius:var(--radius-sm);text-align:center;">
          <div style="font-size:0.75rem;color:var(--text-muted);">Allocated Water</div>
          <div style="font-size:1.1rem;font-weight:800;color:var(--success);">${sum.total_allocated_water} L</div>
        </div>
        <div style="background:#f8fafc;padding:0.75rem;border-radius:var(--radius-sm);text-align:center;">
          <div style="font-size:0.75rem;color:var(--text-muted);">Remaining Water</div>
          <div style="font-size:1.1rem;font-weight:800;color:var(--primary-600);">${sum.remaining_water} L</div>
        </div>
        <div style="background:#f8fafc;padding:0.75rem;border-radius:var(--radius-sm);text-align:center;">
          <div style="font-size:0.75rem;color:var(--text-muted);">Success Rate</div>
          <div style="font-size:1.1rem;font-weight:800;color:#0284c7;">${sum.approved_requests + sum.partial_requests}/${sum.total_requests}</div>
        </div>
      </div>
      <div class="table-responsive">
        <table class="custom-table">
          <thead>
            <tr>
              <th>Req ID</th>
              <th>Priority Level</th>
              <th>Demanded</th>
              <th>Allocated</th>
              <th>Satisfaction</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${results.map(r => `
              <tr>
                <td>#${r.request_id}</td>
                <td><span class="badge badge-${r.priority === 1 ? 'emergency' : r.priority === 2 ? 'hospital' : r.priority === 3 ? 'essential' : r.priority === 4 ? 'household' : 'commercial'}">P${r.priority}: ${prioNames[r.priority] || 'Prio'}</span></td>
                <td>${r.requested_quantity} L</td>
                <td><strong>${r.allocated_quantity} L</strong></td>
                <td>
                  <div style="display:flex;align-items:center;gap:0.5rem;">
                    <div style="flex:1;height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;">
                      <div style="height:100%;width:${r.satisfaction_rate}%;background:${r.satisfaction_rate > 90 ? '#10b981' : r.satisfaction_rate > 50 ? '#0284c7' : '#f59e0b'};"></div>
                    </div>
                    <span style="font-size:0.75rem;font-weight:700;">${r.satisfaction_rate}%</span>
                  </div>
                </td>
                <td><span class="badge ${r.status === 'APPROVED' ? 'badge-allocated' : 'badge-rejected'}">${r.status}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
