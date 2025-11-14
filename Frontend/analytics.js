// Analytics JavaScript for Instagram Reel Scraper
// Handles analytics data fetching, filtering, and display

// API_URL is declared in auth.js (loaded first)

// ==================== DOM Elements ====================
const filterUsername = document.getElementById('filterUsername');
const filterMinPlays = document.getElementById('filterMinPlays');
const filterMinLikes = document.getElementById('filterMinLikes');
const filterMinComments = document.getElementById('filterMinComments');
const sortBy = document.getElementById('sortBy');
const sortOrder = document.getElementById('sortOrder');
const applyFiltersBtn = document.getElementById('applyFiltersBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');
const analyticsTableBody = document.getElementById('analyticsTableBody');
const totalReelsSpan = document.getElementById('totalReels');
const currentPageSpan = document.getElementById('currentPage');
const totalPagesSpan = document.getElementById('totalPages');
const paginationControls = document.getElementById('paginationControls');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');

// State
let analyticsCurrentPage = 1;
let totalPages = 1;
let totalReels = 0;
let currentFilters = {};

// ==================== API Calls ====================

async function fetchAnalytics(page = 1, filters = {}) {
    try {
        const token = window.authUtils.getAuthToken();
        if (!token) {
            console.error('No auth token found');
            window.location.href = '/static/login.html';
            return;
        }

        // Build query parameters
        const params = new URLSearchParams();
        params.append('page', page);

        if (filters.username) {
            params.append('username', filters.username);
        }
        if (filters.min_play_count) {
            params.append('min_play_count', filters.min_play_count);
        }
        if (filters.min_like_count) {
            params.append('min_like_count', filters.min_like_count);
        }
        if (filters.min_comment_count) {
            params.append('min_comment_count', filters.min_comment_count);
        }
        if (filters.sort_by) {
            params.append('sort_by', filters.sort_by);
        }
        if (filters.sort_order) {
            params.append('sort_order', filters.sort_order);
        }

        const response = await fetch(`${API_URL}/api/analytics?${params.toString()}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            console.error('Unauthorized - redirecting to login');
            window.authUtils.clearAuth();
            window.location.href = '/static/login.html';
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to fetch analytics');
        }

        const data = await response.json();
        console.log('✅ Analytics fetched:', data);
        return data;
    } catch (error) {
        console.error('Error fetching analytics:', error);
        showError('Failed to load analytics data');
        return null;
    }
}

async function exportAnalyticsCsv() {
    try {
        const token = window.authUtils.getAuthToken();
        if (!token) {
            window.location.href = '/static/login.html';
            return;
        }

        // Build query parameters for export (same filters, no pagination)
        const params = new URLSearchParams();

        if (currentFilters.username) {
            params.append('username', currentFilters.username);
        }
        if (currentFilters.min_play_count) {
            params.append('min_play_count', currentFilters.min_play_count);
        }
        if (currentFilters.min_like_count) {
            params.append('min_like_count', currentFilters.min_like_count);
        }
        if (currentFilters.min_comment_count) {
            params.append('min_comment_count', currentFilters.min_comment_count);
        }
        if (currentFilters.sort_by) {
            params.append('sort_by', currentFilters.sort_by);
        }
        if (currentFilters.sort_order) {
            params.append('sort_order', currentFilters.sort_order);
        }

        const response = await fetch(`${API_URL}/api/analytics/export?${params.toString()}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to export CSV');
        }

        // Download the CSV file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `analytics_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showSuccess('CSV exported successfully');
    } catch (error) {
        console.error('Error exporting CSV:', error);
        showError('Failed to export CSV');
    }
}

// ==================== UI Functions ====================

function displayAnalytics(data) {
    if (!data || !data.items || data.items.length === 0) {
        analyticsTableBody.innerHTML = '<tr><td colspan="7" class="empty-state">No data yet. Start scraping to see analytics.</td></tr>';
        paginationControls.style.display = 'none';
        totalReelsSpan.textContent = '0';
        currentPageSpan.textContent = '1';
        totalPagesSpan.textContent = '1';
        return;
    }

    // Update stats
    totalReels = data.total;
    totalPages = data.pages;
    analyticsCurrentPage = data.page;

    totalReelsSpan.textContent = totalReels.toLocaleString();
    currentPageSpan.textContent = analyticsCurrentPage;
    totalPagesSpan.textContent = totalPages;

    // Display table rows
    analyticsTableBody.innerHTML = data.items.map(reel => `
        <tr>
            <td class="username-cell">${escapeHtml(reel.instagram_username)}</td>
            <td class="code-cell"><code>${escapeHtml(reel.reel_code || 'N/A')}</code></td>
            <td class="text-right number-cell">${formatNumber(reel.play_count)}</td>
            <td class="text-right number-cell">${formatNumber(reel.like_count)}</td>
            <td class="text-right number-cell">${formatNumber(reel.comment_count)}</td>
            <td class="url-cell">
                ${reel.reel_url ? `<a href="${escapeHtml(reel.reel_url)}" target="_blank" class="reel-link">View Reel</a>` : 'N/A'}
            </td>
            <td class="date-cell">${formatDate(reel.scraped_at)}</td>
        </tr>
    `).join('');

    // Show pagination controls if needed
    if (totalPages > 1) {
        paginationControls.style.display = 'flex';
        prevPageBtn.disabled = analyticsCurrentPage === 1;
        nextPageBtn.disabled = analyticsCurrentPage === totalPages;
    } else {
        paginationControls.style.display = 'none';
    }
}

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString();
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    // Use the global showError from script.js if available
    if (typeof window.showError === 'function' && window.showError !== showError) {
        window.showError(message);
    } else {
        // Fallback to alert if global function not available
        console.error('❌', message);
        alert(message);
    }
}

function showSuccess(message) {
    // Use the global showSuccess from script.js if available
    if (typeof window.showSuccess === 'function' && window.showSuccess !== showSuccess) {
        window.showSuccess(message);
    } else {
        // Fallback to console log if global function not available
        console.log('✅', message);
    }
}

async function loadAnalytics(page = 1) {
    const data = await fetchAnalytics(page, currentFilters);
    if (data) {
        displayAnalytics(data);
    }
}

// ==================== Event Handlers ====================

applyFiltersBtn.addEventListener('click', async () => {
    // Build filters object
    currentFilters = {};

    const username = filterUsername.value.trim();
    const minPlays = parseInt(filterMinPlays.value);
    const minLikes = parseInt(filterMinLikes.value);
    const minComments = parseInt(filterMinComments.value);
    const sortByValue = sortBy.value;
    const sortOrderValue = sortOrder.value;

    if (username) currentFilters.username = username;
    if (!isNaN(minPlays) && minPlays > 0) currentFilters.min_play_count = minPlays;
    if (!isNaN(minLikes) && minLikes > 0) currentFilters.min_like_count = minLikes;
    if (!isNaN(minComments) && minComments > 0) currentFilters.min_comment_count = minComments;
    if (sortByValue) currentFilters.sort_by = sortByValue;
    if (sortOrderValue) currentFilters.sort_order = sortOrderValue;

    console.log('Applying filters:', currentFilters);

    // Reset to page 1 and load
    await loadAnalytics(1);
});

exportCsvBtn.addEventListener('click', async () => {
    exportCsvBtn.disabled = true;
    exportCsvBtn.textContent = 'Exporting...';

    await exportAnalyticsCsv();

    exportCsvBtn.disabled = false;
    exportCsvBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="vertical-align: middle; margin-right: 0.25rem;">
            <path d="M8 11L3 6H6V2H10V6H13L8 11ZM2 13H14V15H2V13Z" fill="currentColor"/>
        </svg>
        Export CSV
    `;
});

prevPageBtn.addEventListener('click', async () => {
    if (analyticsCurrentPage > 1) {
        await loadAnalytics(analyticsCurrentPage - 1);
    }
});

nextPageBtn.addEventListener('click', async () => {
    if (analyticsCurrentPage < totalPages) {
        await loadAnalytics(analyticsCurrentPage + 1);
    }
});

// Also allow pressing Enter in filter fields to apply filters
[filterUsername, filterMinPlays, filterMinLikes, filterMinComments].forEach(input => {
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            applyFiltersBtn.click();
        }
    });
});

// ==================== Initialize ====================

// Function to refresh analytics (can be called from other modules)
window.refreshAnalytics = async function() {
    console.log('Refreshing analytics...');
    await loadAnalytics(analyticsCurrentPage);
};

// Load analytics when the analytics page is shown
// This will be called from the main script.js when switching to analytics page
window.initAnalytics = async function() {
    console.log('Initializing analytics...');
    // Set default sort to play_count descending
    currentFilters = {
        sort_by: sortBy.value,
        sort_order: sortOrder.value
    };
    await loadAnalytics(1);
};

// Export for use in other files
window.analyticsUtils = {
    fetchAnalytics,
    exportAnalyticsCsv,
    refreshAnalytics: window.refreshAnalytics,
    initAnalytics: window.initAnalytics
};

console.log('✅ Analytics module loaded');
