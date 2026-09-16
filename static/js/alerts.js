const Alerts = {
    container: null,

    /**
     * Initialize alert container
     */
    init() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        this.container = document.getElementById('toast-container');
    },

    /**
     * Show toast notification
     * @param {string} message
     * @param {string} type - 'success' | 'error' | 'warning' | 'info'
     * @param {number} duration - milliseconds
     */
    toast(message, type = 'info', duration = 4000) {
        this.init();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `
      <div class="toast-icon">${icons[type] || icons.info}</div>
      <div class="toast-content">
        <p class="toast-message">${message}</p>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">×</button>
`;

        this.container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add('toast-show'));

        // Auto remove
        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    success(message, duration) { this.toast(message, 'success', duration); },
    error(message, duration) { this.toast(message, 'error', duration); },
    warning(message, duration) { this.toast(message, 'warning', duration); },
    info(message, duration) { this.toast(message, 'info', duration); },

    /**
     * Check for due date alerts for a user
     */
    checkDueDateAlerts(userId) {
        const borrows = Utils.getData('vignan_borrows')
            .filter(b => b.userId === userId && b.status === 'active');

        const alerts = [];

        borrows.forEach(borrow => {
            const statusInfo = Utils.getBorrowStatus(borrow.dueDate);
            if (statusInfo.status === 'overdue') {
                const fine = Utils.calculateFine(borrow.dueDate);
                alerts.push({
                    type: 'overdue',
                    message: `"${borrow.bookTitle}" is overdue by ${Math.abs(statusInfo.daysLeft)} days! Fine: ${Utils.formatCurrency(fine)}`,
                    borrow
                });
            } else if (statusInfo.status === 'due-soon') {
                alerts.push({
                    type: 'due-soon',
                    message: `"${borrow.bookTitle}" is due in ${statusInfo.daysLeft} day${statusInfo.daysLeft !== 1 ? 's' : ''}. Return soon!`,
                    borrow
                });
            }
        });

        return alerts;
    },

    /**
     * Display due date alerts as toasts
     */
    showDueDateAlerts(userId) {
        const alerts = this.checkDueDateAlerts(userId);
        alerts.forEach((alert, index) => {
            setTimeout(() => {
                if (alert.type === 'overdue') {
                    this.error(alert.message, 6000);
                } else {
                    this.warning(alert.message, 5000);
                }
            }, index * 800);
        });
        return alerts;
    },

    /**
     * Generate notification panel HTML
     */
    getNotificationPanelHTML(userId) {
        const alerts = this.checkDueDateAlerts(userId);
        if (alerts.length === 0) {
            return `<div class="notification-empty">
        <span class="notif-icon">🔔</span>
        <p>No pending notifications</p>
      </div>`;
        }

        let html = '';
        alerts.forEach(alert => {
            const iconClass = alert.type === 'overdue' ? 'notif-overdue' : 'notif-warning';
            const icon = alert.type === 'overdue' ? '🔴' : '🟡';
            html += `
      <div class="notification-item ${iconClass}">
          <span class="notif-dot">${icon}</span>
          <div class="notif-text">
            <p>${alert.message}</p>
            <small>Due: ${Utils.formatDate(alert.borrow.dueDate)}</small>
          </div>
        </div>`;
        });

        return html;
    },

    /**
     * Generate email simulation message
     */
    simulateEmailAlert(userEmail, bookTitle, dueDate, type) {
        const subject = type === 'overdue'
            ? `[OVERDUE] Library Book Return Notice - ${bookTitle}`
            : `[REMINDER] Library Book Due Soon - ${bookTitle}`;

        const body = type === 'overdue'
            ? `Dear Student,\n\nThis is to inform you that the book "${bookTitle}" borrowed from Vignan University Library is overdue. The due date was ${Utils.formatDate(dueDate)}.\n\nPlease return the book immediately to avoid further fines (₹2/day).\n\nRegards,\nVignan University Library`
            : `Dear Student,\n\nThis is a friendly reminder that the book "${bookTitle}" is due on ${Utils.formatDate(dueDate)}.\n\nPlease return or renew the book before the due date to avoid fines.\n\nRegards,\nVignan University Library`;

        return { to: userEmail, subject, body, sentAt: new Date().toISOString() };
    },

    /**
     * Show return-soon warning banner
     */
    showWarningBanner(message) {
        let banner = document.getElementById('warning-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'warning-banner';
            banner.className = 'warning-banner';
            const mainContent = document.querySelector('.main-content') || document.body;
            mainContent.prepend(banner);
        }
        banner.innerHTML = `
      <div class="banner-content">
        <span class="banner-icon">⚠️</span>
        <span class="banner-text">${message}</span>
        <button class="banner-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>`;
        banner.style.display = 'block';
    },

    /**
     * Confirm dialog
     */
    confirm(message) {
        return new Promise(resolve => {
            const overlay = document.createElement('div');
            overlay.className = 'confirm-overlay';
            overlay.innerHTML = `
      <div class="confirm-dialog">
          <div class="confirm-icon">❓</div>
          <p class="confirm-message">${message}</p>
          <div class="confirm-actions">
            <button class="btn btn-secondary" id="confirmNo">Cancel</button>
            <button class="btn btn-primary" id="confirmYes">Confirm</button>
          </div>
        </div>`;
            document.body.appendChild(overlay);
            requestAnimationFrame(() => overlay.classList.add('show'));

            overlay.querySelector('#confirmYes').onclick = () => {
                overlay.remove();
                resolve(true);
            };
            overlay.querySelector('#confirmNo').onclick = () => {
                overlay.remove();
                resolve(false);
            };
        });
    }
};
