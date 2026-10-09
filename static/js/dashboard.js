/**
 * Dashboard Analytics & Charts using Chart.js
 */

let categoryChartInstance = null;
let deptChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    initDashboardCharts();
});

function getThemeChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        textColor: isDark ? '#E2E8F0' : '#1E202A',
        gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
        palette: [
            '#6C5CE7', // Tech - Purple
            '#FD79A8', // Cultural - Pink
            '#00B894', // Sports - Emerald
            '#0984E3', // Workshop - Blue
            '#FDCB6E'  // Seminar - Amber
        ]
    };
}

async function initDashboardCharts() {
    try {
        const res = await fetch('/api/dashboard/metrics');
        const data = await res.json();
        renderCategoryChart(data.category_stats);
        renderDeptChart(data.dept_stats);
    } catch (e) {
        console.error('Failed to load dashboard metrics for charts', e);
    }
}

function renderCategoryChart(categoryStats) {
    const canvas = document.getElementById('categoryDonutChart');
    if (!canvas) return;

    const colors = getThemeChartColors();
    const labels = categoryStats.map(c => c.category);
    const counts = categoryStats.map(c => c.reg_count || c.event_count);

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    categoryChartInstance = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors.palette,
                borderWidth: 2,
                borderColor: document.documentElement.getAttribute('data-theme') === 'dark' ? '#141726' : '#FFFFFF',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.textColor,
                        font: { family: 'Plus Jakarta Sans', weight: '600', size: 12 },
                        padding: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${context.raw} Registrations`;
                        }
                    }
                }
            },
            cutout: '68%'
        }
    });
}

function renderDeptChart(deptStats) {
    const canvas = document.getElementById('deptBarChart');
    if (!canvas) return;

    const colors = getThemeChartColors();
    const labels = deptStats.map(d => d.department);
    const counts = deptStats.map(d => d.count);

    if (deptChartInstance) {
        deptChartInstance.destroy();
    }

    deptChartInstance = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Registered Students',
                data: counts,
                backgroundColor: '#6C5CE7',
                borderRadius: 8,
                hoverBackgroundColor: '#FD79A8'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: colors.textColor,
                        font: { family: 'Plus Jakarta Sans', weight: '600' }
                    }
                },
                y: {
                    grid: { color: colors.gridColor },
                    ticks: {
                        color: colors.textColor,
                        stepSize: 2
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

// Global theme change callback
window.onThemeChanged = function() {
    initDashboardCharts();
};
