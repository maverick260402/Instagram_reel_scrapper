/**
 * Statistics Dashboard Component
 * Handles advanced statistics and charts
 */

const StatsComponent = {
    charts: {
        dailyTrend: null,
        creditUsage: null,
        accountUsage: null,
        hourlyUsage: null,
        successFailure: null
    },
    currentDays: 7,

    /**
     * Initialize stats component
     */
    async init() {
        this.attachEventListeners();
        await this.loadDashboardData();
    },

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Dashboard trend days filter
        const trendFilter = document.getElementById('trendDaysFilter');
        if (trendFilter) {
            trendFilter.addEventListener('change', (e) => {
                this.currentDays = parseInt(e.target.value);
                this.loadDailyTrend();
            });
        }

        // Statistics time range filter
        const statsFilter = document.getElementById('statsTimeRange');
        if (statsFilter) {
            statsFilter.addEventListener('change', (e) => {
                this.currentDays = parseInt(e.target.value);
                this.loadStatisticsCharts();
            });
        }
    },

    /**
     * Load dashboard data (for dashboard page)
     */
    async loadDashboardData() {
        try {
            // Load overview stats
            await this.loadOverviewStats();

            // Load charts
            await this.loadDailyTrend();
            await this.loadCreditUsage();

            // Load recent activity
            await this.loadRecentActivity();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    },

    /**
     * Load overview statistics cards
     */
    async loadOverviewStats() {
        try {
            const data = await api.getSystemOverview();

            // Update stat cards
            document.getElementById('totalUsers').textContent = data.users.total;
            document.getElementById('activeUsers').textContent = data.users.active;

            document.getElementById('totalAccounts').textContent = data.instagram_accounts.total;
            document.getElementById('activeAccounts').textContent = data.instagram_accounts.active;

            document.getElementById('todayReels').textContent = data.today.reels_scraped;
            document.getElementById('todayJobs').textContent = data.today.jobs_completed;

            document.getElementById('successRate').textContent = data.overall.success_rate + '%';
            document.getElementById('totalJobs').textContent = data.overall.total_jobs;
        } catch (error) {
            console.error('Failed to load overview stats:', error);
        }
    },

    /**
     * Load daily trend chart
     */
    async loadDailyTrend() {
        try {
            const data = await api.getUsageStatistics(this.currentDays);
            const trends = data.daily_trends;

            // Extract labels and data
            const labels = trends.map(t => formatDateDDMMYYYY(t.date));
            const reelsData = trends.map(t => t.reels_scraped);
            const usersData = trends.map(t => t.active_users);

            // Destroy existing chart
            if (this.charts.dailyTrend) {
                ChartHelper.destroyChart(this.charts.dailyTrend);
            }

            // Create new chart
            this.charts.dailyTrend = ChartHelper.createDailyTrendChart(
                'dailyTrendChart',
                labels,
                reelsData,
                usersData
            );
        } catch (error) {
            console.error('Failed to load daily trend:', error);
        }
    },

    /**
     * Load credit usage chart
     */
    async loadCreditUsage() {
        try {
            const data = await api.getUsageStatistics(this.currentDays);
            const topUsers = data.top_credit_consumers || [];

            // Extract labels and data
            const labels = topUsers.map(u => u.username);
            const creditsData = topUsers.map(u => u.credits_used);

            // Destroy existing chart
            if (this.charts.creditUsage) {
                ChartHelper.destroyChart(this.charts.creditUsage);
            }

            // Create new chart
            this.charts.creditUsage = ChartHelper.createCreditUsageChart(
                'creditUsageChart',
                labels,
                creditsData
            );
        } catch (error) {
            console.error('Failed to load credit usage:', error);
        }
    },

    /**
     * Load recent activity list
     */
    async loadRecentActivity() {
        try {
            const data = await api.getLogs({ limit: 10 });
            const logs = data.logs || [];

            const container = document.getElementById('recentActivityList');
            if (!container) return;

            if (logs.length === 0) {
                container.innerHTML = '<div class="empty-state-text">No recent activity</div>';
                return;
            }

            container.innerHTML = logs.map(log => this.renderActivityItem(log)).join('');
        } catch (error) {
            console.error('Failed to load recent activity:', error);
        }
    },

    /**
     * Render single activity item
     */
    renderActivityItem(log) {
        const icon = this.getActivityIcon(log.event_type);
        const title = this.getActivityTitle(log.event_type);
        const description = this.getActivityDescription(log);
        const time = this.formatRelativeTime(log.created_at);

        return `
            <div class="activity-item">
                <div class="activity-icon">${icon}</div>
                <div class="activity-details">
                    <div class="activity-title">${title}</div>
                    <div class="activity-description">${description}</div>
                    <div class="activity-time">${time}</div>
                </div>
            </div>
        `;
    },

    /**
     * Get icon for activity type
     */
    getActivityIcon(eventType) {
        const icons = {
            'scrape_started': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M8 5V19L19 12L8 5Z" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            'scrape_success': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.76489 14.1003 1.98232 16.07 2.86" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M22 4L12 14.01L9 11.01" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            'scrape_failed': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#ef4444" stroke-width="2"/><path d="M15 9L9 15M9 9L15 15" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/></svg>',
            'user_created': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12Z" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 20C20 16.13 16.42 13 12 13C7.58 13 4 16.13 4 20" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            'user_updated': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M18.5 2.50023C18.8978 2.1024 19.4374 1.87891 20 1.87891C20.5626 1.87891 21.1022 2.1024 21.5 2.50023C21.8978 2.89805 22.1213 3.43762 22.1213 4.00023C22.1213 4.56284 21.8978 5.1024 21.5 5.50023L12 15.0002L8 16.0002L9 12.0002L18.5 2.50023Z" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            'cookies_updated': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M21.5 2V6M21.5 6V10M21.5 6H17.5M21.5 6H25.5" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 10C19 14.4183 15.4183 18 11 18C6.58172 18 3 14.4183 3 10C3 5.58172 6.58172 2 11 2" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            'account_rotated': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M23 4V10H17" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20.49 15C19.9828 16.5048 19.0552 17.8467 17.8052 18.8729C16.5552 19.899 15.0318 20.5656 13.4058 20.7972C11.7798 21.0287 10.1183 20.8157 8.60585 20.1799C7.09335 19.544 5.78555 18.5091 4.82086 17.1849C3.85617 15.8607 3.26964 14.2976 3.12293 12.6623C2.97622 11.027 3.27472 9.37954 4.0003 7.90086C4.72588 6.42218 5.84687 5.16855 7.24114 4.27723C8.63541 3.38591 10.247 2.89206 11.9 2.84998" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M23 10C23 8.68678 22.7413 7.38642 22.2388 6.17317C21.7362 4.95991 20.9997 3.85752 20.0711 2.92893C19.1425 2.00035 18.0401 1.26375 16.8268 0.761205C15.6136 0.258658 14.3132 0 13 0V10H23Z" fill="#8b5cf6" opacity="0.2"/></svg>',
            'daily_reset': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 6V12L16 14" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="10" stroke="#8b5cf6" stroke-width="2"/></svg>',
            'credits_deducted': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 17L12 22L22 17" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12L12 17L22 12" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            'account_created': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="20" height="20" rx="2" stroke="#10b981" stroke-width="2"/><circle cx="12" cy="10" r="3" stroke="#10b981" stroke-width="2"/><path d="M7 18.5C7 16.5 9 15 12 15C15 15 17 16.5 17 18.5" stroke="#10b981" stroke-width="2" stroke-linecap="round"/></svg>'
        };
        return icons[eventType] || '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="3" stroke="#9ca3af" stroke-width="2"/></svg>';
    },

    /**
     * Get title for activity type
     */
    getActivityTitle(eventType) {
        const titles = {
            'scrape_started': 'Scraping Job Started',
            'scrape_success': 'Scraping Completed Successfully',
            'scrape_failed': 'Scraping Job Failed',
            'user_created': 'New User Registered',
            'user_updated': 'User Settings Updated',
            'cookies_updated': 'Cookies Refreshed',
            'daily_reset': 'Daily Reset Completed'
        };
        return titles[eventType] || eventType.replace(/_/g, ' ').toUpperCase();
    },

    /**
     * Get description from log details
     */
    getActivityDescription(log) {
        if (!log.details) return 'No details available';

        const details = log.details;

        switch (log.event_type) {
            case 'scrape_success':
                return `Scraped ${details.reels_count || 0} reels using account ${details.instagram_account_username || 'N/A'}`;
            case 'scrape_failed':
                return details.error || 'Unknown error';
            case 'user_created':
                return `New user: ${details.username || 'N/A'}`;
            case 'cookies_updated':
                return `Updated ${details.cookies_count || 0} cookies for ${details.account_username || 'account'}`;
            default:
                return JSON.stringify(details).substring(0, 100);
        }
    },

    /**
     * Format relative time
     */
    formatRelativeTime(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        const diffMs = now - past;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

        return formatDateDDMMYYYY(timestamp);
    },

    /**
     * Load statistics page charts
     */
    async loadStatisticsCharts() {
        try {
            await this.loadAccountUsageChart();
            await this.loadHourlyUsageChart();
            await this.loadSuccessFailureChart();
        } catch (error) {
            console.error('Failed to load statistics charts:', error);
        }
    },

    /**
     * Load account usage distribution chart
     */
    async loadAccountUsageChart() {
        try {
            const data = await api.getPerformanceMetrics();
            const accounts = data.account_distribution || [];

            // Extract labels and data
            const labels = accounts.map(a => a.username);
            const usageData = accounts.map(a => a.daily_usage);

            // Destroy existing chart
            if (this.charts.accountUsage) {
                ChartHelper.destroyChart(this.charts.accountUsage);
            }

            // Create new chart
            this.charts.accountUsage = ChartHelper.createAccountUsageChart(
                'accountUsageChart',
                labels,
                usageData
            );
        } catch (error) {
            console.error('Failed to load account usage chart:', error);
        }
    },

    /**
     * Load hourly usage pattern chart
     */
    async loadHourlyUsageChart() {
        try {
            // For now, create mock data (will need backend endpoint)
            const hours = Array.from({ length: 24 }, (_, i) => i);
            const reelCounts = hours.map(() => Math.floor(Math.random() * 100));

            // Destroy existing chart
            if (this.charts.hourlyUsage) {
                ChartHelper.destroyChart(this.charts.hourlyUsage);
            }

            // Create new chart
            this.charts.hourlyUsage = ChartHelper.createHourlyUsageChart(
                'hourlyUsageChart',
                hours,
                reelCounts
            );
        } catch (error) {
            console.error('Failed to load hourly usage chart:', error);
        }
    },

    /**
     * Load success/failure chart
     */
    async loadSuccessFailureChart() {
        try {
            const data = await api.getSystemOverview();

            const successCount = data.overall.successful_jobs;
            const failureCount = data.overall.failed_jobs;

            // Destroy existing chart
            if (this.charts.successFailure) {
                ChartHelper.destroyChart(this.charts.successFailure);
            }

            // Create new chart
            this.charts.successFailure = ChartHelper.createSuccessFailureChart(
                'successFailureChart',
                successCount,
                failureCount
            );
        } catch (error) {
            console.error('Failed to load success/failure chart:', error);
        }
    }
};
