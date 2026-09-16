/**
 * Vignan Library Management System - Utility Functions
 * Common helper functions used across modules
 */

const API_BASE = window.location.origin + '/api';

const Utils = {
    /**
     * Make API call to backend
     */
    async api(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: { 'Content-Type': 'application/json' },
                ...options,
                body: options.body ? JSON.stringify(options.body) : undefined
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    },

    /**
     * Generate unique ID with prefix
     */
    generateId(prefix = 'ID') {
        return prefix + '_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 5);
    },

    /**
     * Format date to DD/MM/YYYY
     */
    formatDate(date) {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        return `${day}/${month}/${year}`;
    },

    /**
     * Format date to ISO string (YYYY-MM-DD)
     */
    formatDateISO(date) {
        const d = new Date(date);
        return d.toISOString().split('T')[0];
    },

    /**
     * Calculate days between two dates
     */
    daysBetween(date1, date2) {
        const d1 = new Date(date1);
        const d2 = new Date(date2);
        const diffTime = d2.getTime() - d1.getTime();
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    },

    /**
     * Get due date (30 days from issue)
     */
    getDueDate(issueDate) {
        const d = new Date(issueDate);
        d.setDate(d.getDate() + 30);
        return d;
    },

    /**
     * Calculate fine (₹2/day after due date)
     */
    calculateFine(dueDate) {
        const now = new Date();
        const due = new Date(dueDate);
        if (now <= due) return 0;
        const overdueDays = this.daysBetween(due, now);
        return overdueDays * 2;
    },

    /**
     * Get borrow status
     */
    getBorrowStatus(dueDate) {
        const now = new Date();
        const due = new Date(dueDate);
        const daysLeft = this.daysBetween(now, due);
        if (daysLeft < 0) return { status: 'overdue', label: 'Overdue', class: 'status-overdue', daysLeft };
        if (daysLeft <= 5) return { status: 'due-soon', label: 'Due Soon', class: 'status-due-soon', daysLeft };
        return { status: 'active', label: 'Active', class: 'status-active', daysLeft };
    },

    /**
     * Get current logged-in user from sessionStorage
     */
    getCurrentUser() {
        try {
            return JSON.parse(sessionStorage.getItem('vignan_current_user'));
        } catch {
            return null;
        }
    },

    /**
     * Set current user in session
     */
    setCurrentUser(user) {
        sessionStorage.setItem('vignan_current_user', JSON.stringify(user));
    },

    /**
     * Check auth and redirect
     */
    requireAuth() {
        const user = this.getCurrentUser();
        if (!user) {
            window.location.href = window.BOOK_PLATFORM_ROUTES?.login || '/login';
            return null;
        }
        return user;
    },

    /**
     * Debounce function
     */
    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    },

    /**
     * Format currency in INR
     */
    formatCurrency(amount) {
        return '₹' + Number(amount).toFixed(2);
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Truncate text
     */
    truncate(text, length = 80) {
        if (!text) return '';
        return text.length > length ? text.substring(0, length) + '...' : text;
    },

    /**
     * Dark mode toggle
     */
    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('vignan_dark_mode', isDark);
        return isDark;
    },

    loadDarkMode() {
        const isDark = localStorage.getItem('vignan_dark_mode') === 'true';
        if (isDark) document.body.classList.add('dark-mode');
        return isDark;
    }
};
