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
                    notificationList.innerHTML = '<div class="notification-empty">No recent notifications</div>';
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
            <div class="notification-item">
                <div class="notification-item-icon">${icon}</div>
                <div class="notification-item-content">
                    <div class="notification-item-title">${title}</div>
                    <div class="notification-item-time">${time}</div>
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

    // Select appropriate icon (SVG)
    const icons = {
        success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.76489 14.1003 1.98232 16.07 2.86" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M22 4L12 14.01L9 11.01" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#ef4444" stroke-width="2"/><path d="M15 9L9 15M9 9L15 15" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/></svg>',
        warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M10.29 3.86L1.82 18C1.64537 18.3024 1.55299 18.6453 1.55201 18.9945C1.55103 19.3437 1.64149 19.6871 1.81442 19.9905C1.98735 20.2939 2.23672 20.5467 2.53771 20.7239C2.83869 20.9011 3.18077 20.9962 3.53 21H20.47C20.8192 20.9962 21.1613 20.9011 21.4623 20.7239C21.7633 20.5467 22.0126 20.2939 22.1856 19.9905C22.3585 19.6871 22.449 19.3437 22.448 18.9945C22.447 18.6453 22.3546 18.3024 22.18 18L13.71 3.86C13.5317 3.56611 13.2807 3.32312 12.9812 3.15448C12.6817 2.98585 12.3437 2.89725 12 2.89725C11.6563 2.89725 11.3183 2.98585 11.0188 3.15448C10.7193 3.32312 10.4683 3.56611 10.29 3.86Z" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 9V13" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="17" r="1" fill="#f59e0b"/></svg>',
        info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#8b5cf6" stroke-width="2"/><path d="M12 16V12M12 8H12.01" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
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
