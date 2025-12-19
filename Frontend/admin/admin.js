/**
 * Main Admin Panel Controller
 * Handles navigation, authentication, and component initialization
 */

const AdminPanel = {
    currentPage: 'dashboard',
    isAuthenticated: false,
    adminProfile: null,

    /**
     * Initialize admin panel
     */
    async init() {
        // Check authentication
        this.checkAuth();

        // Load admin profile
        await this.loadProfile();

        // Attach navigation listeners
        this.attachNavigationListeners();

        // Attach notification listeners
        this.attachNotificationListeners();

        // Initialize dashboard by default
        await this.loadPage('dashboard');

        // Start polling for notifications (every 30 seconds)
        this.startNotificationPolling();
    },

    /**
     * Check if user is authenticated
     */
    checkAuth() {
        const token = localStorage.getItem('admin_token');

        if (!token) {
            // No token, redirect to admin login
            window.location.href = '/static/admin/login.html';
            return;
        }

        this.isAuthenticated = true;
    },

    /**
     * Load admin profile
     */
    async loadProfile() {
        try {
            const profile = await api.getProfile();
            this.adminProfile = profile;

            // Update UI
            document.getElementById('adminName').textContent = profile.username;
            document.getElementById('adminEmail').textContent = profile.email;
        } catch (error) {
            console.error('Failed to load profile:', error);
            // Token might be invalid, redirect to login
            localStorage.removeItem('admin_token');
            window.location.href = '/static/login.html';
        }
    },

    /**
     * Attach navigation event listeners
     */
    attachNavigationListeners() {
        // Sidebar navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.getAttribute('data-page');
                this.navigateToPage(page);
            });
        });

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    },

    /**
     * Attach notification listeners
     */
    attachNotificationListeners() {
        const notificationBtn = document.getElementById('notificationBtn');
        const notificationPanel = document.getElementById('notificationPanel');

        if (notificationBtn && notificationPanel) {
            notificationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                notificationPanel.classList.toggle('show');
            });

            // Close panel when clicking outside
            document.addEventListener('click', (e) => {
                if (!notificationPanel.contains(e.target) && !notificationBtn.contains(e.target)) {
                    notificationPanel.classList.remove('show');
                }
            });
        }
    },

    /**
     * Navigate to a specific page
     */
    async navigateToPage(page) {
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            if (item.getAttribute('data-page') === page) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Update page title
        const titles = {
            'dashboard': 'Dashboard',
            'users': 'User Management',
            'accounts': 'Instagram Accounts',
            'logs': 'Activity Logs',
            'statistics': 'Statistics'
        };
        document.getElementById('pageTitle').textContent = titles[page] || 'Admin Panel';

        // Show appropriate page content
        document.querySelectorAll('.page-content').forEach(content => {
            content.classList.remove('active');
        });

        const pageElement = document.getElementById(`page-${page}`);
        if (pageElement) {
            pageElement.classList.add('active');
        }

        // Load page data
        await this.loadPage(page);

        this.currentPage = page;
    },

    /**
     * Load page-specific data
     */
    async loadPage(page) {
        switch (page) {
            case 'dashboard':
                await StatsComponent.loadDashboardData();
                break;

            case 'users':
                await UsersComponent.init();
                break;

            case 'accounts':
                await AccountsComponent.init();
                break;

            case 'logs':
                await LogsComponent.init();
                break;

            case 'statistics':
                await StatsComponent.loadStatisticsCharts();
                break;
        }
    },

    /**
     * Start polling for notifications
     */
    startNotificationPolling() {
        // Load notifications immediately
        this.loadNotifications();

        // Poll every 30 seconds
        setInterval(() => {
            this.loadNotifications();
        }, 30000);
    },

    /**
     * Load notifications
     */
    async loadNotifications() {
        try {
            const data = await api.getLogs({ limit: 10 });
            const logs = data.logs || [];

            // Update notification count
            const badge = document.getElementById('notificationBadge');
            if (badge) {
                // Count logs from last hour as "new"
                const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
                const newLogs = logs.filter(log => new Date(log.created_at) > oneHourAgo);
                badge.textContent = newLogs.length;

                if (newLogs.length > 0) {
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            }

            // Update notification list
            const notificationList = document.getElementById('notificationList');
            if (notificationList) {
                if (logs.length === 0) {
                    notificationList.innerHTML = '<div style="padding: 1rem; text-align: center; color: #9ca3af;">No notifications</div>';
                } else {
                    notificationList.innerHTML = logs.map(log => this.renderNotificationItem(log)).join('');
                }
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    },

    /**
     * Render single notification item
     */
    renderNotificationItem(log) {
        const icon = StatsComponent.getActivityIcon(log.event_type);
        const title = StatsComponent.getActivityTitle(log.event_type);
        const time = StatsComponent.formatRelativeTime(log.created_at);

        return `
            <div style="padding: 0.75rem; border-bottom: 1px solid #262626; cursor: pointer;"
                 onmouseover="this.style.background='#0a0a0a'"
                 onmouseout="this.style.background='transparent'">
                <div style="display: flex; gap: 0.75rem; align-items: start;">
                    <div style="font-size: 1.25rem;">${icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 0.25rem;">${title}</div>
                        <div style="font-size: 0.85rem; color: #9ca3af;">${time}</div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Logout
     */
    logout() {
        if (confirm('Are you sure you want to logout?')) {
            api.clearToken();
            window.location.href = '/static/admin/login.html';
        }
    }
};

/**
 * Global Toast Notification System
 */
function showNotification(message, type = 'info', duration = 4000) {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Select appropriate icon
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    const icon = icons[type] || icons.info;

    // Build toast HTML
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    // Add to container
    container.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Initialize admin panel when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AdminPanel.init();
});
