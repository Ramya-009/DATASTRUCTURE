/**
 * Chart.js Integration Module for Water Analytics
 */

const Charts = {
  // 1. Line Chart: 7-Day Water Consumption Trend
  renderConsumptionChart(canvasId, labels, dataPoints) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Daily Consumption (Litres)',
          data: dataPoints || [9800, 10200, 10500, 11000, 10800, 11500, 12000],
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.08)',
          borderWidth: 3,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#0284c7',
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 12,
            titleFont: { size: 13, weight: 'bold' },
            bodyFont: { size: 12 }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            grid: { color: 'rgba(226, 232, 240, 0.6)' },
            ticks: {
              callback: val => `${val} L`
            }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  },

  // 2. Bar Chart: Tank Capacity vs Current Level
  renderTankComparisonChart(canvasId, tankNames, capacities, currentLevels) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: tankNames || ['Tank 1', 'Tank 2', 'Tank 3', 'Tank 4'],
        datasets: [
          {
            label: 'Current Water Level (L)',
            data: currentLevels || [72000, 64000, 37200, 22500],
            backgroundColor: '#0ea5e9',
            borderRadius: 6
          },
          {
            label: 'Total Capacity (L)',
            data: capacities || [100000, 80000, 60000, 50000],
            backgroundColor: 'rgba(203, 213, 225, 0.7)',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 14, font: { weight: '600' } } }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { callback: v => `${v / 1000}k L` }
          }
        }
      }
    });
  },

  // 3. Doughnut Chart: Area Allocation Breakdown
  renderAreaDoughnutChart(canvasId, areaNames, allocationData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: areaNames || ['Poonamallee', 'Avadi', 'Porur', 'Ambattur', 'Guindy'],
        datasets: [{
          data: allocationData || [35, 28, 18, 12, 7],
          backgroundColor: [
            '#0284c7',
            '#38bdf8',
            '#10b981',
            '#f59e0b',
            '#8b5cf6'
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 12, font: { size: 12 } } }
        },
        cutout: '70%'
      }
    });
  }
};
