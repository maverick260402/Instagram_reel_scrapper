/**
 * Activity Logs Component
 * Handles viewing and filtering activity logs
 */

const LogsComponent = {
    currentLogs: [],
    currentFilters: {
        event_type: 'all',
        start_date: null,
        end_date: null
    },

    /**
     * Initialize logs component
     */
    async init() {
        this.attachEventListeners();
        this.setDefaultDates();
        await this.loadLogs();
    },

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Date filters
        const startDate = document.getElementById('logsStartDate');
        const endDate = document.getElementById('logsEndDate');

        if (startDate) {
            startDate.addEventListener('change', (e) => {
                this.currentFilters.start_date = e.target.value;
                this.loadLogs();
            });
        }

        if (endDate) {
            endDate.addEventListener('change', (e) => {
                this.currentFilters.end_date = e.target.value;
                this.loadLogs();
            });
        }

        // Event type filter
        const eventFilter = document.getElementById('logsEventTypeFilter');
        if (eventFilter) {
            eventFilter.addEventListener('change', (e) => {
                this.currentFilters.event_type = e.target.value;
                this.loadLogs();
            });
        }

        // Export button
        const exportBtn = document.getElementById('exportLogsBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportLogs());
        }
    },

    /**
     * Set default date range (last 7 days)
     */
    setDefaultDates() {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 7);

        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };

        const startInput = document.getElementById('logsStartDate');
        const endInput = document.getElementById('logsEndDate');

        if (startInput) {
            startInput.value = formatDate(startDate);
            this.currentFilters.start_date = formatDate(startDate);
        }

        if (endInput) {
            endInput.value = formatDate(endDate);
            this.currentFilters.end_date = formatDate(endDate);
        }
    },

    /**
     * Load activity logs from API
     */
    async loadLogs() {
        try {
            const params = {};

            if (this.currentFilters.event_type !== 'all') {
                params.event_type = this.currentFilters.event_type;
            }

            if (this.currentFilters.start_date) {
                params.start_date = this.currentFilters.start_date + 'T00:00:00';
            }

            if (this.currentFilters.end_date) {
                params.end_date = this.currentFilters.end_date + 'T23:59:59';
            }

            params.limit = 100;

            const data = await api.getLogs(params);
            this.currentLogs = data.logs || [];
            this.renderLogsTable();
        } catch (error) {
            console.error('Failed to load logs:', error);
            this.showError('Failed to load activity logs');
        }
    },

    /**
     * Render logs table
     */
    renderLogsTable() {
        const container = document.getElementById('logsTableContainer');
        if (!container) return;

        if (this.currentLogs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-text">No activity logs found</div>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Event Type</th>
                        <th>User ID</th>
                        <th>Instagram Account</th>
                        <th>Job ID</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.currentLogs.map(log => this.renderLogRow(log)).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
    },

    /**
     * Render single log row
     */
    renderLogRow(log) {
        const timestamp = formatDateTimeDDMMYYYY(log.created_at);
        const eventBadge = this.getEventBadge(log.event_type);
        const details = log.details ? JSON.stringify(log.details, null, 2) : 'N/A';
        const shortDetails = details.length > 50 ? details.substring(0, 50) + '...' : details;

        return `
            <tr>
                <td style="font-size: 0.85rem;">${timestamp}</td>
                <td>${eventBadge}</td>
                <td>${log.user_id || 'N/A'}</td>
                <td>${log.instagram_account_id || 'N/A'}</td>
                <td style="font-size: 0.85rem;">${log.job_id || 'N/A'}</td>
                <td>
                    <span style="font-size: 0.85rem; font-family: monospace; color: #9ca3af;" title="${details}">
                        ${shortDetails}
                    </span>
                </td>
            </tr>
        `;
    },

    /**
     * Get event type badge
     */
    getEventBadge(eventType) {
        const badges = {
            'scrape_started': '<span class="table-badge">Scrape Started</span>',
            'scrape_success': '<span class="table-badge success">Scrape Success</span>',
            'scrape_failed': '<span class="table-badge error">Scrape Failed</span>',
            'user_created': '<span class="table-badge success">User Created</span>',
            'user_updated': '<span class="table-badge">User Updated</span>',
            'user_deleted': '<span class="table-badge error">User Deleted</span>',
            'cookies_updated': '<span class="table-badge success">Cookies Updated</span>',
            'bulk_cookies_updated': '<span class="table-badge success">Bulk Update</span>',
            'daily_reset': '<span class="table-badge">Daily Reset</span>',
            'account_rotation': '<span class="table-badge">Account Rotation</span>'
        };

        return badges[eventType] || `<span class="table-badge">${eventType}</span>`;
    },

    /**
     * Export logs as CSV
     */
    exportLogs() {
        if (this.currentLogs.length === 0) {
            alert('No logs to export');
            return;
        }

        // Create CSV content
        const headers = ['Timestamp', 'Event Type', 'User ID', 'Instagram Account ID', 'Job ID', 'Details'];
        const rows = this.currentLogs.map(log => [
            new Date(log.created_at).toISOString(),
            log.event_type,
            log.user_id || '',
            log.instagram_account_id || '',
            log.job_id || '',
            JSON.stringify(log.details || {})
        ]);

        let csvContent = headers.join(',') + '\n';
        rows.forEach(row => {
            csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
        });

        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `activity_logs_${Date.now()}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    },

    /**
     * Show error message
     */
    showError(message) {
        alert(`Error: ${message}`);
    }
};
