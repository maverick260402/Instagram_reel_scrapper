/**
 * API Client for Admin Panel
 * Handles all HTTP requests to the backend
 */

const API_BASE_URL = 'http://167.71.224.203';

class AdminAPI {
    constructor() {
        this.token = localStorage.getItem('admin_token');
    }

    /**
     * Set authentication token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('admin_token', token);
    }

    /**
     * Clear authentication token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('admin_token');
    }

    /**
     * Get authorization headers
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired, redirect to admin login
                    this.clearToken();
                    window.location.href = '/static/admin/login.html';
                    throw new Error('Authentication required');
                }
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // ==================== AUTHENTICATION ====================

    async login(email, password) {
        const response = await this.request('/api/admin/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        this.setToken(response.access_token);
        return response;
    }

    async getProfile() {
        return await this.request('/api/admin/auth/me');
    }

    // ==================== USERS ====================

    async getUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/api/admin/users${queryString ? '?' + queryString : ''}`;
        return await this.request(endpoint);
    }

    async getUserDetails(userId) {
        return await this.request(`/api/admin/users/${userId}`);
    }

    async updateUser(userId, updates) {
        return await this.request(`/api/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    }

    async deleteUser(userId) {
        return await this.request(`/api/admin/users/${userId}`, {
            method: 'DELETE'
        });
    }

    async getUserStats(userId) {
        return await this.request(`/api/admin/users/${userId}/stats`);
    }

    // ==================== INSTAGRAM ACCOUNTS ====================

    async getInstagramAccounts() {
        return await this.request('/api/admin/instagram-accounts');
    }

    async createInstagramAccount(accountData) {
        return await this.request('/api/admin/instagram-accounts', {
            method: 'POST',
            body: JSON.stringify(accountData)
        });
    }

    async updateInstagramAccountCookies(accountId, cookies) {
        return await this.request(`/api/admin/instagram-accounts/${accountId}/cookies`, {
            method: 'PUT',
            body: JSON.stringify(cookies)
        });
    }

    async updateInstagramAccountStatus(accountId, statusUpdates) {
        return await this.request(`/api/admin/instagram-accounts/${accountId}/status`, {
            method: 'PATCH',
            body: JSON.stringify(statusUpdates)
        });
    }

    // ==================== ACTIVITY LOGS ====================

    async getLogs(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/api/admin/logs${queryString ? '?' + queryString : ''}`;
        return await this.request(endpoint);
    }

    async getLogStats() {
        return await this.request('/api/admin/logs/stats');
    }

    // ==================== STATISTICS ====================

    async getSystemOverview() {
        return await this.request('/api/admin/stats/overview');
    }

    async getUsageStatistics(days = 7) {
        return await this.request(`/api/admin/stats/usage?days=${days}`);
    }

    async getPerformanceMetrics() {
        return await this.request('/api/admin/stats/performance');
    }
}

// Create global instance
const api = new AdminAPI();
