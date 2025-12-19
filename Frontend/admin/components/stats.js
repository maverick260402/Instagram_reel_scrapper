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
            const labels = trends.map(t => new Date(t.date).toLocaleDateString());
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
            'scrape_started': '▶',
            'scrape_success': '✓',
            'scrape_failed': '✗',
            'user_created': '•',
            'user_updated': '•',
            'cookies_updated': '↻',
            'daily_reset': '•'
        };
        return icons[eventType] || '•';
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

        return past.toLocaleDateString();
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
