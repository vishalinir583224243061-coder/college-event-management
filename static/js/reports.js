/**
 * Reports & Analytics Page Scripts with Chart.js & CSV export triggers
 */

let reportsCategoryChart = null;
let reportsDeptChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initReportsCharts();
});

function initReportsCharts() {
    const categoryCanvas = document.getElementById('reportsCategoryChart');
    const deptCanvas = document.getElementById('reportsDeptChart');
    if (!categoryCanvas || !deptCanvas) return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#E2E8F0' : '#1E202A';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';

    // Parse data from embedded JSON if available
    const categoryDataEl = document.getElementById('reportsCategoryData');
    const deptDataEl = document.getElementById('reportsDeptData');

    if (categoryDataEl && deptDataEl) {
        try {
            const categories = JSON.parse(categoryDataEl.textContent);
            const depts = JSON.parse(deptDataEl.textContent);

            // 1. Category Bar Chart
            reportsCategoryChart = new Chart(categoryCanvas, {
                type: 'bar',
                data: {
                    labels: categories.map(c => c.category),
                    datasets: [{
                        label: 'Total Registrations',
                        data: categories.map(c => c.reg_count),
                        backgroundColor: ['#6C5CE7', '#FD79A8', '#00B894', '#0984E3', '#FDCB6E'],
                        borderRadius: 8
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
                            ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: '600' } },
                            grid: { display: false }
                        },
                        y: {
                            ticks: { color: textColor },
                            grid: { color: gridColor },
                            beginAtZero: true
                        }
                    }
                }
            });

            // 2. Department Polar Area / Doughnut Chart
            reportsDeptChart = new Chart(deptCanvas, {
                type: 'polarArea',
                data: {
                    labels: depts.map(d => d.department),
                    datasets: [{
                        data: depts.map(d => d.count),
                        backgroundColor: [
                            'rgba(108, 92, 231, 0.75)',
                            'rgba(253, 121, 168, 0.75)',
                            'rgba(9, 132, 227, 0.75)',
                            'rgba(0, 184, 148, 0.75)',
                            'rgba(253, 203, 110, 0.75)',
                            'rgba(163, 103, 220, 0.75)'
                        ],
                        borderWidth: 2,
                        borderColor: isDark ? '#141726' : '#FFFFFF'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 12 } }
                        }
                    },
                    scales: {
                        r: {
                            grid: { color: gridColor },
                            ticks: { display: false }
                        }
                    }
                }
            });

        } catch (e) {
            console.error('Failed to parse chart data', e);
        }
    }
}
