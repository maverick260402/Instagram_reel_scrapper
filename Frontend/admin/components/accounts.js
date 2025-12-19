/**
 * Instagram Accounts Management Component
 * Handles account pool monitoring and management
 */

const AccountsComponent = {
    currentAccounts: [],
    currentFilter: 'all',

    /**
     * Initialize accounts component
     */
    async init() {
        this.attachEventListeners();
        await this.loadAccounts();
    },

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Status filter
        const statusFilter = document.getElementById('accountStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.renderFilteredAccounts();
            });
        }
    },

    /**
     * Load Instagram accounts from API
     */
    async loadAccounts() {
        try {
            const data = await api.getInstagramAccounts();
            this.currentAccounts = data.accounts || [];
            this.renderAccountsTable();
        } catch (error) {
            console.error('Failed to load Instagram accounts:', error);
            this.showError('Failed to load Instagram accounts');
        }
    },

    /**
     * Render accounts table
     */
    renderAccountsTable() {
        const container = document.getElementById('accountsTableContainer');
        if (!container) return;

        if (this.currentAccounts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📱</div>
                    <div class="empty-state-text">No Instagram accounts in pool</div>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Cookie Health</th>
                        <th>Daily Usage</th>
                        <th>Total Scrapes</th>
                        <th>Success Rate</th>
                        <th>Last Used</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.currentAccounts.map(account => this.renderAccountRow(account)).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
    },

    /**
     * Render single account row
     */
    renderAccountRow(account) {
        // Status badge
        let statusBadge;
        if (!account.is_active) {
            statusBadge = '<span class="table-badge error">Inactive</span>';
        } else if (account.is_paused) {
            statusBadge = '<span class="table-badge warning">Paused</span>';
        } else {
            statusBadge = '<span class="table-badge success">Active</span>';
        }

        // Cookie health
        const cookieAge = this.getCookieAge(account.cookies_updated_at);
        const cookieHealth = this.getCookieHealthBadge(cookieAge);

        // Success rate
        const successRate = account.success_count + account.failure_count > 0
            ? Math.round((account.success_count / (account.success_count + account.failure_count)) * 100)
            : 0;

        // Last used
        const lastUsed = account.last_used_at
            ? new Date(account.last_used_at).toLocaleDateString() + ' ' + new Date(account.last_used_at).toLocaleTimeString()
            : 'Never';

        return `
            <tr>
                <td>${account.username}</td>
                <td>${account.email}</td>
                <td>${statusBadge}</td>
                <td>${cookieHealth}</td>
                <td>${account.daily_scrape_count}</td>
                <td>${account.total_scrapes}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="flex: 1; background: #262626; height: 8px; border-radius: 4px; overflow: hidden; max-width: 100px;">
                            <div style="width: ${successRate}%; height: 100%; background: #10b981;"></div>
                        </div>
                        <span style="font-size: 0.85rem;">${successRate}%</span>
                    </div>
                </td>
                <td style="font-size: 0.85rem;">${lastUsed}</td>
                <td>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <button class="table-action-btn" onclick="AccountsComponent.openCookieModal(${account.id}, '${account.username}')" title="Update account cookies">
                            🔑 Cookies
                        </button>
                        <button class="table-action-btn ${account.is_active ? 'active' : 'inactive'}"
                                onclick="AccountsComponent.toggleActive(${account.id}, ${!account.is_active})"
                                title="${account.is_active ? 'Deactivate account' : 'Activate account'}">
                            ${account.is_active ? '✓ Active' : '✕ Inactive'}
                        </button>
                        <button class="table-action-btn ${account.is_paused ? 'paused' : ''}"
                                onclick="AccountsComponent.togglePause(${account.id}, ${!account.is_paused})"
                                title="${account.is_paused ? 'Resume account' : 'Pause account'}">
                            ${account.is_paused ? '▶ Resume' : '⏸ Pause'}
                        </button>
                    </div>
                </td>
            </tr>
        `;
    },

    /**
     * Get cookie age in days
     */
    getCookieAge(cookieUpdatedAt) {
        if (!cookieUpdatedAt) return null;

        const updatedDate = new Date(cookieUpdatedAt);
        const now = new Date();
        const ageMs = now - updatedDate;
        const ageDays = Math.floor(ageMs / (1000 * 60 * 60 * 24));

        return ageDays;
    },

    /**
     * Get cookie health badge based on age
     */
    getCookieHealthBadge(ageDays) {
        if (ageDays === null) {
            return '<span class="table-badge error">No Cookies</span>';
        } else if (ageDays > 7) {
            return `<span class="table-badge error">Expired (${ageDays}d)</span>`;
        } else if (ageDays > 5) {
            return `<span class="table-badge warning">Expiring (${ageDays}d)</span>`;
        } else {
            return `<span class="table-badge success">Healthy (${ageDays}d)</span>`;
        }
    },

    /**
     * Render filtered accounts based on current filter
     */
    renderFilteredAccounts() {
        let filtered = this.currentAccounts;

        switch (this.currentFilter) {
            case 'active':
                filtered = this.currentAccounts.filter(a => a.is_active && !a.is_paused);
                break;
            case 'paused':
                filtered = this.currentAccounts.filter(a => a.is_paused);
                break;
            case 'healthy':
                filtered = this.currentAccounts.filter(a => {
                    const age = this.getCookieAge(a.cookies_updated_at);
                    return age !== null && age <= 5;
                });
                break;
            case 'expired':
                filtered = this.currentAccounts.filter(a => {
                    const age = this.getCookieAge(a.cookies_updated_at);
                    return age === null || age > 7;
                });
                break;
        }

        const container = document.getElementById('accountsTableContainer');
        if (!container) return;

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📱</div>
                    <div class="empty-state-text">No accounts match the filter</div>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Cookie Health</th>
                        <th>Daily Usage</th>
                        <th>Total Scrapes</th>
                        <th>Success Rate</th>
                        <th>Last Used</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${filtered.map(account => this.renderAccountRow(account)).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
    },

    /**
     * Open cookie update modal
     */
    openCookieModal(accountId, accountUsername) {
        // Populate account info
        document.getElementById('cookieModalAccountId').value = accountId;
        document.getElementById('cookieModalAccountName').textContent = accountUsername;

        // Find account in current accounts array to get existing cookies
        const account = this.currentAccounts.find(acc => acc.id === accountId);
        const existingCookies = account && account.cookies ? account.cookies : {};

        // Pre-populate fields with existing cookie values (or empty if not set)
        document.getElementById('cookieSessionId').value = existingCookies.sessionid || '';
        document.getElementById('cookieCsrfToken').value = existingCookies.csrftoken || '';
        document.getElementById('cookieDsUserId').value = existingCookies.ds_user_id || '';
        document.getElementById('cookieIgDid').value = existingCookies.ig_did || '';
        document.getElementById('cookieMid').value = existingCookies.mid || '';
        document.getElementById('cookieDatr').value = existingCookies.datr || '';
        document.getElementById('cookieRur').value = existingCookies.rur || '';
        document.getElementById('cookieWd').value = existingCookies.wd || '';
        document.getElementById('cookieIgNrcb').value = existingCookies.ig_nrcb || '';

        // Show modal
        document.getElementById('cookieUpdateModal').classList.add('show');
    },

    /**
     * Close cookie update modal
     */
    closeCookieModal() {
        document.getElementById('cookieUpdateModal').classList.remove('show');
    },

    /**
     * Save cookie update
     */
    async saveCookieUpdate() {
        const accountId = document.getElementById('cookieModalAccountId').value;

        // Build cookies object
        const cookies = {
            sessionid: document.getElementById('cookieSessionId').value.trim(),
            csrftoken: document.getElementById('cookieCsrfToken').value.trim(),
            ds_user_id: document.getElementById('cookieDsUserId').value.trim(),
            ig_did: document.getElementById('cookieIgDid').value.trim(),
            mid: document.getElementById('cookieMid').value.trim(),
            datr: document.getElementById('cookieDatr').value.trim(),
            rur: document.getElementById('cookieRur').value.trim(),
            wd: document.getElementById('cookieWd').value.trim(),
            ig_nrcb: document.getElementById('cookieIgNrcb').value.trim()
        };

        // Validate required fields
        if (!cookies.sessionid || !cookies.csrftoken || !cookies.ds_user_id || !cookies.ig_did) {
            showNotification('Please fill in all required fields (Session ID, CSRF Token, DS User ID, IG DID)', 'warning');
            return;
        }

        // Remove empty optional fields
        Object.keys(cookies).forEach(key => {
            if (!cookies[key]) delete cookies[key];
        });

        try {
            const result = await api.updateInstagramAccountCookies(accountId, cookies);

            if (result.status === 'success') {
                showNotification(`✓ Cookies updated successfully for ${result.account_username}`, 'success');
                this.closeCookieModal();
                await this.loadAccounts(); // Reload accounts table
            } else {
                showNotification('Failed to update cookies. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error updating cookies:', error);
            showNotification(`Error: ${error.message || 'Failed to update cookies'}`, 'error');
        }
    },

    /**
     * Toggle account active status
     */
    async toggleActive(accountId, newActiveState) {
        const account = this.currentAccounts.find(acc => acc.id === accountId);
        const accountName = account ? account.username : 'account';

        try {
            const result = await api.updateInstagramAccountStatus(accountId, {
                is_active: newActiveState
            });

            if (result.status === 'success') {
                const statusText = newActiveState ? 'activated' : 'deactivated';
                showNotification(`✓ Account ${accountName} ${statusText} successfully`, 'success');
                await this.loadAccounts(); // Reload accounts table
            } else {
                showNotification('Failed to update account status', 'error');
            }
        } catch (error) {
            console.error('Error updating account status:', error);
            showNotification(`Error: ${error.message || 'Failed to update status'}`, 'error');
        }
    },

    /**
     * Toggle account paused status
     */
    async togglePause(accountId, newPausedState) {
        const account = this.currentAccounts.find(acc => acc.id === accountId);
        const accountName = account ? account.username : 'account';

        try {
            const result = await api.updateInstagramAccountStatus(accountId, {
                is_paused: newPausedState
            });

            if (result.status === 'success') {
                const statusText = newPausedState ? 'paused' : 'resumed';
                showNotification(`✓ Account ${accountName} ${statusText} successfully`, 'success');
                await this.loadAccounts(); // Reload accounts table
            } else {
                showNotification('Failed to update account status', 'error');
            }
        } catch (error) {
            console.error('Error updating account status:', error);
            showNotification(`Error: ${error.message || 'Failed to update status'}`, 'error');
        }
    },

    /**
     * Show error message
     */
    showError(message) {
        alert(`Error: ${message}`);
    }
};
