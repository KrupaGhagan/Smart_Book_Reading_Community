/**
 * Vignan Library Management System - Authentication Module
 * Handles login, register, session management (connected to MySQL backend)
 */

const Auth = {
    /**
     * Register a new student (via API)
     */
    async register(userData) {
        const result = await Utils.api('/auth/signup', {
            method: 'POST',
            body: {
                username: userData.username || userData.regNo || userData.email,
                email: userData.email,
                password: userData.password,
                name: userData.name
            }
        });
        if (!result) return { success: false, message: 'Network error. Please try again.' };
        return {
            success: Boolean(result.user_id),
            message: result.message || (result.user_id ? 'User created successfully' : 'Registration failed'),
            userId: result.user_id
        };
    },

    /**
     * Login user (via API)
     */
    async login(email, password) {
        const result = await Utils.api('/auth/login', {
            method: 'POST',
            body: { username: email, password }
        });
        if (result && result.token) {
            Utils.setCurrentUser({
                id: result.user_id,
                username: email,
                email,
                name: email.split('@')[0],
                role: 'student',
                department: 'Readers',
                token: result.token
            });
        }
        if (!result) return { success: false, message: 'Network error. Please try again.' };
        return {
            success: Boolean(result.token),
            message: result.token ? 'Login successful' : (result.message || 'Login failed')
        };
    },

    /**
     * Logout user
     */
    logout() {
        sessionStorage.removeItem('vignan_current_user');
        window.location.href = window.BOOK_PLATFORM_ROUTES?.login || '/login';
    },

    /**
     * Get current user
     */
    getCurrentUser() {
        return Utils.getCurrentUser();
    },

    /**
     * Check if user is admin
     */
    isAdmin() {
        const user = this.getCurrentUser();
        return user && user.role === 'admin';
    }
};

/* ===== Login Page Logic ===== */
function initLoginPage() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        const result = await Auth.login(email, password);
        if (result.success) {
            Alerts.success(result.message);
            setTimeout(() => {
                window.location.href = window.BOOK_PLATFORM_ROUTES?.dashboard || '/dashboard';
            }, 800);
        } else {
            Alerts.error(result.message);
        }
    });
}

/* ===== Register Page Logic ===== */
function initRegisterPage() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('regName').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        const department = document.getElementById('regDepartment').value;
        const username = document.getElementById('regRegNo').value.trim();
        const phone = document.getElementById('regPhone').value.trim();

        // Validations
        if (password !== confirmPassword) {
            Alerts.error('Passwords do not match!');
            return;
        }
        if (password.length < 6) {
            Alerts.error('Password must be at least 6 characters!');
            return;
        }

        const result = await Auth.register({ name, email, password, department, username, phone });
        if (result.success) {
            Alerts.success(result.message);
            setTimeout(() => {
                window.location.href = window.BOOK_PLATFORM_ROUTES?.login || '/login';
            }, 1200);
        } else {
            Alerts.error(result.message);
        }
    });
}

/* ===== Toggle Password Visibility ===== */
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
    } else {
        input.type = 'password';
        btn.textContent = 'Show';
    }
}
