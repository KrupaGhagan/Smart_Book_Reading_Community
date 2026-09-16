/**
 * Book Reading Community Platform - Dashboard Module
 * Handles dashboard stats, sidebar navigation, dark mode (connected to MySQL backend)
 */

const Dashboard = {
  currentUser: null,

  /**
   * Initialize dashboard
   */
  init() {
    this.currentUser = Utils.requireAuth();
    if (!this.currentUser) return;

    Utils.loadDarkMode();
    this.renderSidebar();
    this.setupMobileMenu();
    this.setupDarkModeToggle();
  },

  /**
   * Render sidebar navigation
   */
  renderSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    const isAdmin = this.currentUser.role === 'admin';
    const routes = window.BOOK_PLATFORM_ROUTES || {};
    const dashboardPath = routes.dashboard || '/dashboard';

    const studentNav = `
      <div class="nav-section">
        <div class="nav-section-title">Main Menu</div>
        <a href="${dashboardPath}" class="nav-item" data-page="dashboard">
          <span class="nav-icon">🏠</span> Dashboard
        </a>
        <a href="/books" class="nav-item" data-page="books">
          <span class="nav-icon">📖</span> Books
        </a>
        <a href="/groups" class="nav-item" data-page="groups">
          <span class="nav-icon">👥</span> Groups
        </a>
        <a href="/progress" class="nav-item" data-page="progress">
          <span class="nav-icon">🔄</span> Progress
        </a>
      </div>`;

    const adminNav = `
      <div class="nav-section">
        <div class="nav-section-title">Main Menu</div>
        <a href="${dashboardPath}" class="nav-item" data-page="dashboard">
          <span class="nav-icon">🏠</span> Dashboard
        </a>
      </div>
      <div class="nav-section">
        <div class="nav-section-title">Management</div>
        <a href="/books" class="nav-item" data-page="books">
          <span class="nav-icon">📚</span> Books
        </a>
        <a href="/groups" class="nav-item" data-page="groups">
          <span class="nav-icon">👥</span> Groups
        </a>
        <a href="/progress" class="nav-item" data-page="progress">
          <span class="nav-icon">🔄</span> Progress
        </a>
        <a href="/apidocs" class="nav-item" data-page="docs">
          <span class="nav-icon">📊</span> API Docs
        </a>
      </div>
      <div class="nav-section">
        <div class="nav-section-title">Student View</div>
        <a href="/api/ai" class="nav-item" data-page="ai">
          <span class="nav-icon">📖</span> AI Routes
        </a>
      </div>`;

    const initials = this.currentUser.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

    sidebar.innerHTML = `
      <div class="sidebar-brand">
        <span class="logo-icon">📚</span>
        <div class="brand-text">
          <h3>Book Reading</h3>
          <small>Community Platform</small>
        </div>
      </div>
      <nav class="sidebar-nav">
        ${isAdmin ? adminNav : studentNav}
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="user-avatar">${initials}</div>
          <div class="user-info">
            <h4>${Utils.escapeHtml(this.currentUser.name || this.currentUser.username || 'Reader')}</h4>
            <small>${isAdmin ? 'Administrator' : 'Community Reader'}</small>
          </div>
        </div>
        <button class="btn-logout" onclick="Auth.logout()">
          <span>🚪</span> Logout
        </button>
      </div>`;

    // Highlight active nav item
    this.highlightActiveNav();
  },

  /**
   * Highlight current page in nav
   */
  highlightActiveNav() {
    const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.dataset.page === currentPage) {
        item.classList.add('active');
      }
    });
  },

  /**
   * Setup mobile menu
   */
  setupMobileMenu() {
    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (toggle) {
      toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
      });
    }
    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
      });
    }
  },

  /**
   * Setup dark mode toggle
   */
  setupDarkModeToggle() {
    const btn = document.getElementById('darkModeToggle');
    if (!btn) return;
    btn.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
    btn.addEventListener('click', () => {
      Utils.toggleDarkMode();
      btn.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
    });
  },

  /**
   * Render student dashboard (async - calls API)
   */
  async renderStudentDashboard() {
    const user = this.currentUser;
    if (!user) return;

    // Get borrows from localStorage via Borrows module
    let allBorrows = [];
    try {
      allBorrows = await Borrows.getByUser(user.id);
    } catch (e) {
      allBorrows = JSON.parse(localStorage.getItem('vignan_borrows') || '[]').filter(b => b.userId === user.id);
    }

    const activeBorrows = allBorrows.filter(b => b.status === 'active');
    let dueSoon = 0;
    let overdueCount = 0;
    let totalFine = 0;

    activeBorrows.forEach(b => {
      const now = new Date();
      const due = new Date(b.dueDate);
      const daysLeft = Math.ceil((due - now) / (1000 * 60 * 60 * 24));
      if (daysLeft < 0) {
        overdueCount++;
        totalFine += Math.abs(daysLeft) * 2;
      } else if (daysLeft <= 5) {
        dueSoon++;
      }
    });

    // Stats
    document.getElementById('statBorrowed').textContent = activeBorrows.length;
    document.getElementById('statDueSoon').textContent = dueSoon;
    document.getElementById('statOverdue').textContent = overdueCount;
    document.getElementById('statFine').textContent = Utils.formatCurrency(totalFine);

    // Warning banners
    if (typeof Alerts !== 'undefined') {
      if (overdueCount > 0) {
        Alerts.showWarningBanner(`You have ${overdueCount} overdue book(s)! Total fine: ${Utils.formatCurrency(totalFine)}. Please return them immediately.`);
      } else if (dueSoon > 0) {
        Alerts.showWarningBanner(`${dueSoon} book(s) due within 5 days. Return soon to avoid fines!`);
      }
    }

    // Recent borrows
    const recentBorrows = allBorrows.slice(0, 5);
    const recentHtml = recentBorrows.map(b => {
      const st = b.status === 'active' ? Utils.getBorrowStatus(b.dueDate) : { label: 'Returned', class: 'status-returned' };
      return `
        <div class="recent-item">
          <div class="item-icon" style="background:var(--info-light);color:var(--info);">📖</div>
          <div class="item-info">
            <h4>${Utils.escapeHtml(b.bookTitle)}</h4>
            <p>Borrowed: ${Utils.formatDate(b.issueDate)} · <span class="badge badge-${st.class === 'status-overdue' ? 'danger' : st.class === 'status-due-soon' ? 'warning' : 'success'}">${st.label}</span></p>
          </div>
        </div>`;
    }).join('');
    document.getElementById('recentActivity').innerHTML = recentHtml || '<div class="no-data"><span>📭</span>No recent activity</div>';
  },

  /**
   * Render admin dashboard (async - calls API)
   */
  async renderAdminDashboard() {
    // Get data from localStorage
    const books = (typeof booksDatabase !== 'undefined') ? booksDatabase : [];
    let borrows = [];
    try {
      borrows = await Borrows.getAll();
    } catch (e) {
      borrows = JSON.parse(localStorage.getItem('vignan_borrows') || '[]');
    }

    const totalBooks = books.length;
    const totalStudents = '—';
    const activeBorrows = borrows.filter(b => b.status === 'active').length;
    const now = new Date();
    const overdueBooks = borrows.filter(b => b.status === 'active' && new Date(b.dueDate) < now).length;

    document.getElementById('statTotalBooks').textContent = totalBooks;
    document.getElementById('statTotalStudents').textContent = totalStudents;
    document.getElementById('statActiveBorrows').textContent = activeBorrows;
    document.getElementById('statOverdueBooks').textContent = overdueBooks;

    if (document.getElementById('statTopCategory')) {
      // Find most borrowed category
      const catCount = {};
      borrows.forEach(b => {
        const book = books.find(bk => bk.id === b.bookId);
        if (book) catCount[book.category] = (catCount[book.category] || 0) + 1;
      });
      const topCat = Object.entries(catCount).sort((a, b) => b[1] - a[1])[0];
      document.getElementById('statTopCategory').textContent = topCat ? topCat[0] : 'N/A';
    }

    // Recent activity
    const recentBorrows = borrows.slice(-8).reverse();
    const recentHtml = recentBorrows.map(b => {
      const action = b.status === 'returned' ? 'Returned' : 'Borrowed';
      const icon = b.status === 'returned' ? '↩️' : '📖';
      return `
        <div class="recent-item">
          <div class="item-icon" style="background:${b.status === 'returned' ? 'var(--success-light)' : 'var(--info-light)'};color:${b.status === 'returned' ? 'var(--success)' : 'var(--info)'};">${icon}</div>
          <div class="item-info">
            <h4>${Utils.escapeHtml(b.bookTitle)}</h4>
            <p>${action} · ${Utils.formatDate(b.issueDate)}</p>
          </div>
        </div>`;
    }).join('');
    document.getElementById('recentActivity').innerHTML = recentHtml || '<div class="no-data"><span>📭</span>No recent activity</div>';
  }
};
