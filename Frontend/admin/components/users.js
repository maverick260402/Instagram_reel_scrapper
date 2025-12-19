/**
 * Users Management Component
 * Handles user list, editing, and statistics
 */

const UsersComponent = {
    currentUsers: [],
    currentFilter: 'all',
    currentEditUserId: null,

    /**
     * Initialize users component
     */
    async init() {
        this.attachEventListeners();
        await this.loadUsers();
    },

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Search input
        const searchInput = document.getElementById('userSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterUsers(e.target.value));
        }

        // Status filter
        const statusFilter = document.getElementById('userStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.loadUsers();
            });
        }

        // Modal close buttons
        document.querySelectorAll('[data-modal="userEditModal"]').forEach(btn => {
            btn.addEventListener('click', () => this.closeEditModal());
        });

        // Save user button
        const saveBtn = document.getElementById('saveUserBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveUser());
        }
    },

    /**
     * Load users from API
     */
    async loadUsers() {
        try {
            const params = {};

            if (this.currentFilter === 'active') {
                params.is_active = true;
            } else if (this.currentFilter === 'inactive') {
                params.is_active = false;
            }

            const data = await api.getUsers(params);
            this.currentUsers = data.users;
            this.renderUsersTable();
        } catch (error) {
            console.error('Failed to load users:', error);
            this.showError('Failed to load users');
        }
    },

    /**
     * Render users table
     */
    renderUsersTable() {
        const container = document.getElementById('usersTableContainer');
        if (!container) return;

        if (this.currentUsers.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <div class="empty-state-text">No users found</div>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Username</th>
                        <th>Credits</th>
                        <th>Usage</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.currentUsers.map(user => this.renderUserRow(user)).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
        this.attachTableEventListeners();
    },

    /**
     * Render single user row
     */
    renderUserRow(user) {
        const statusBadge = user.is_active
            ? '<span class="table-badge success">Active</span>'
            : '<span class="table-badge error">Inactive</span>';

        const createdDate = new Date(user.created_at).toLocaleDateString();

        return `
            <tr>
                <td>${user.email}</td>
                <td>${user.username}</td>
                <td>${user.credits_used_today} / ${user.daily_credit_limit}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="flex: 1; background: #262626; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="width: ${user.usage_percent}%; height: 100%; background: #8b5cf6;"></div>
                        </div>
                        <span style="font-size: 0.85rem;">${user.usage_percent}%</span>
                    </div>
                </td>
                <td>${statusBadge}</td>
                <td>${createdDate}</td>
                <td>
                    <div class="table-actions">
                        <button class="table-action-btn" onclick="UsersComponent.openEditModal(${user.id})">Edit</button>
                        <button class="table-action-btn" onclick="UsersComponent.viewUserDetails(${user.id})">Details</button>
                    </div>
                </td>
            </tr>
        `;
    },

    /**
     * Attach event listeners to table action buttons
     */
    attachTableEventListeners() {
        // Event listeners are attached via onclick in HTML for simplicity
    },

    /**
     * Filter users by search term
     */
    filterUsers(searchTerm) {
        const filtered = this.currentUsers.filter(user => {
            const term = searchTerm.toLowerCase();
            return user.email.toLowerCase().includes(term) ||
                   user.username.toLowerCase().includes(term);
        });

        // Re-render with filtered users
        const container = document.getElementById('usersTableContainer');
        if (!container) return;

        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Username</th>
                        <th>Credits</th>
                        <th>Usage</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${filtered.map(user => this.renderUserRow(user)).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
    },

    /**
     * Open edit modal for user
     */
    async openEditModal(userId) {
        try {
            const user = this.currentUsers.find(u => u.id === userId);
            if (!user) return;

            this.currentEditUserId = userId;

            // Populate modal fields
            document.getElementById('editUserEmail').value = user.email;
            document.getElementById('editUserUsername').value = user.username;
            document.getElementById('editUserCreditLimit').value = user.daily_credit_limit;
            document.getElementById('editUserActive').checked = user.is_active;

            // Show modal
            const modal = document.getElementById('userEditModal');
            modal.classList.add('show');
        } catch (error) {
            console.error('Failed to open edit modal:', error);
            this.showError('Failed to load user data');
        }
    },

    /**
     * Close edit modal
     */
    closeEditModal() {
        const modal = document.getElementById('userEditModal');
        modal.classList.remove('show');
        this.currentEditUserId = null;
    },

    /**
     * Save user changes
     */
    async saveUser() {
        try {
            const creditLimit = parseInt(document.getElementById('editUserCreditLimit').value);
            const isActive = document.getElementById('editUserActive').checked;

            const updates = {
                daily_credit_limit: creditLimit,
                is_active: isActive
            };

            await api.updateUser(this.currentEditUserId, updates);

            this.closeEditModal();
            await this.loadUsers();
            this.showSuccess('User updated successfully');
        } catch (error) {
            console.error('Failed to save user:', error);
            this.showError('Failed to save user changes');
        }
    },

    /**
     * View detailed user statistics
     */
    async viewUserDetails(userId) {
        try {
            const details = await api.getUserDetails(userId);

            alert(`User Details:\n\nEmail: ${details.user.email}\nUsername: ${details.user.username}\nTotal Jobs: ${details.statistics.total_jobs}\nSuccessful Jobs: ${details.statistics.successful_jobs}\nTotal Reels: ${details.statistics.total_reels_scraped}\nSuccess Rate: ${details.statistics.success_rate}%`);
        } catch (error) {
            console.error('Failed to load user details:', error);
            this.showError('Failed to load user details');
        }
    },

    /**
     * Show success message
     */
    showSuccess(message) {
        // Simple alert for now (can be replaced with toast notification)
        alert(message);
    },

    /**
     * Show error message
     */
    showError(message) {
        alert(`Error: ${message}`);
    }
};
