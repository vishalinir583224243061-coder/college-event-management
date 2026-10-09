/**
 * Main application scripts: Dark mode toggle, toasts, notifications
 */

// Initialize Theme from localStorage or system preference
(function initTheme() {
    const savedTheme = localStorage.getItem('campussphere_theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle button setup
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        updateThemeToggleIcon();
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Auto-dismiss alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch(e) {}
        }, 5000);
    });
});

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('campussphere_theme', newTheme);
    updateThemeToggleIcon();

    // Trigger Chart.js redraws if present
    if (window.onThemeChanged) {
        window.onThemeChanged(newTheme);
    }
}

function updateThemeToggleIcon() {
    const themeBtn = document.getElementById('themeToggleBtn');
    if (!themeBtn) return;
    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme === 'dark') {
        themeBtn.innerHTML = '<i class="fas fa-sun text-warning"></i>';
        themeBtn.setAttribute('title', 'Switch to Light Mode');
    } else {
        themeBtn.innerHTML = '<i class="fas fa-moon text-dark"></i>';
        themeBtn.setAttribute('title', 'Switch to Dark Mode');
    }
}

// Global Toast notification helper
function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1090';
        document.body.appendChild(container);
    }

    const toastId = 'toast_' + Date.now();
    const bgClass = type === 'success' ? 'bg-success text-white' :
                    type === 'danger' || type === 'error' ? 'bg-danger text-white' :
                    type === 'warning' ? 'bg-warning text-dark' : 'bg-primary text-white';

    const icon = type === 'success' ? 'fa-check-circle' :
                 type === 'danger' || type === 'error' ? 'fa-exclamation-triangle' :
                 type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2">
                    <i class="fas ${icon} fa-lg"></i>
                    <div>${message}</div>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
    bsToast.show();

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

// Mark notification as read
async function markNotificationAsRead(notifId, el) {
    try {
        const res = await fetch(`/api/notifications/${notifId}/read`, { method: 'POST' });
        if (res.ok) {
            if (el) {
                el.style.opacity = '0.5';
            }
            const countEl = document.getElementById('unreadNotifBadge');
            if (countEl) {
                let current = parseInt(countEl.innerText) || 0;
                if (current > 1) {
                    countEl.innerText = current - 1;
                } else {
                    countEl.remove();
                }
            }
        }
    } catch(err) {
        console.error('Failed to mark read', err);
    }
}
