// Track page lifecycle
console.log('🌟 SCRIPT STARTED - Page load or reload detected at:', new Date().toISOString());
console.log('Performance timing:', {
    loadType: performance.navigation.type, // 0=navigate, 1=reload, 2=back_forward
    redirectCount: performance.navigation.redirectCount
});

if (performance.navigation.type === 1) {
    console.warn('⚠️ PAGE WAS RELOADED (not initial load)');
} else if (performance.navigation.type === 0) {
    console.log('✅ Initial page navigation');
} else if (performance.navigation.type === 2) {
    console.log('↩️ Back/Forward navigation');
}

// API Configuration
// API_URL is declared in auth.js (loaded first)

// ==================== Authentication Check ====================
// Check if user is logged in
const authToken = window.authUtils?.getAuthToken();
const currentUser = window.authUtils?.getCurrentUser();

// Note: Authentication is optional for development
// If backend requires auth, uncomment the redirect below
if (!authToken || !currentUser) {
    console.warn('⚠️ No authentication found - running in development mode');
    // Uncomment the line below to enforce authentication:
    // window.location.href = '/';  // Root serves login page
} else {
    console.log('✅ User authenticated:', currentUser?.email);
}

// State management
let usernames = [];
let currentPage = localStorage.getItem('currentPage') || 'scraper';
let jobHistory = JSON.parse(localStorage.getItem('jobHistory')) || [];
let jobTrackerRefreshInterval = null;
let activePollingJobs = new Set(); // Track active polling jobs
let currentLoadedGroupId = null; // Track which group was loaded for usage tracking

// DOM Elements
const singleUsernameInput = document.getElementById('singleUsername');
const addUsernameBtn = document.getElementById('addUsernameBtn');
const multipleUsernamesTextarea = document.getElementById('multipleUsernames');
const addMultipleBtn = document.getElementById('addMultipleBtn');
const reelCountInput = document.getElementById('reelCount');
const scrapeBtn = document.getElementById('scrapeBtn');
const usernamesSection = document.getElementById('usernamesSection');
const usernamesList = document.getElementById('usernamesList');
const clearAllBtn = document.getElementById('clearAllBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

// Sidebar elements
const statTotalUsernames = document.getElementById('statTotalUsernames');
const statReelsCount = document.getElementById('statReelsCount');
const statStatus = document.getElementById('statStatus');
const statCredits = document.getElementById('statCredits');
const statCreditsProgress = document.getElementById('statCreditsProgress');
const statCreditsRemaining = document.getElementById('statCreditsRemaining');
const activityList = document.getElementById('activityList');

// Navigation elements
const navItems = document.querySelectorAll('.nav-item');
const scraperPage = document.getElementById('scraper-page');
const jobTrackerPage = document.getElementById('job-tracker-page');
const analyticsPage = document.getElementById('analytics-page');
const jobsList = document.getElementById('jobsList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

// User info elements
const userNameSpan = document.getElementById('userName');
const logoutBtn = document.getElementById('logoutBtn');

// Event Listeners
addUsernameBtn.addEventListener('click', handleAddSingleUsername);
singleUsernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleAddSingleUsername();
    }
});

addMultipleBtn.addEventListener('click', handleAddMultipleUsernames);
clearAllBtn.addEventListener('click', handleClearAll);
scrapeBtn.addEventListener('click', handleScrape);
reelCountInput.addEventListener('input', () => {
    updateSidebarStats();
});

// Navigation event listeners
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.dataset.page;
        navigateToPage(page);
    });
});

clearHistoryBtn.addEventListener('click', handleClearHistory);
refreshHistoryBtn.addEventListener('click', () => {
    // Reload job history from localStorage
    jobHistory = JSON.parse(localStorage.getItem('jobHistory')) || [];
    renderJobHistory();
    addActivity('Refreshed job history');
});

// Logout event listener
logoutBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to logout?')) {
        window.authUtils.clearAuth();
        window.location.href = '/';  // Root serves login page
    }
});

// Initialize user display
if (currentUser) {
    userNameSpan.textContent = currentUser.username || currentUser.email;
} else {
    userNameSpan.textContent = 'Guest User';
}

// Navigation Functions
function navigateToPage(page) {
    currentPage = page;

    // Save current page to localStorage
    localStorage.setItem('currentPage', page);

    // Update active nav item
    navItems.forEach(item => {
        if (item.dataset.page === page) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Show/hide pages
    if (page === 'scraper') {
        scraperPage.style.display = 'block';
        jobTrackerPage.style.display = 'none';
        if (analyticsPage) analyticsPage.style.display = 'none';

        // Stop auto-refresh when leaving job tracker
        if (jobTrackerRefreshInterval) {
            clearInterval(jobTrackerRefreshInterval);
            jobTrackerRefreshInterval = null;
        }
    } else if (page === 'job-tracker') {
        // Hide progress section when navigating away from scraper
        progressSection.style.display = 'none';

        // Reload job history from localStorage before showing
        const savedHistory = localStorage.getItem('jobHistory');
        jobHistory = savedHistory ? JSON.parse(savedHistory) : [];
        console.log('Loaded job history from localStorage:', jobHistory.length, 'jobs');

        scraperPage.style.display = 'none';
        jobTrackerPage.style.display = 'block';
        if (analyticsPage) analyticsPage.style.display = 'none';
        renderJobHistory();

        // Start auto-refresh every 2 seconds to check for job updates
        if (jobTrackerRefreshInterval) {
            clearInterval(jobTrackerRefreshInterval);
        }
        jobTrackerRefreshInterval = setInterval(() => {
            const savedHistory = localStorage.getItem('jobHistory');
            const updatedHistory = savedHistory ? JSON.parse(savedHistory) : [];

            console.log('Auto-refresh checking...', {
                currentJobs: jobHistory.length,
                updatedJobs: updatedHistory.length,
                currentStatuses: jobHistory.map(j => ({ id: j.id, status: j.status })),
                updatedStatuses: updatedHistory.map(j => ({ id: j.id, status: j.status }))
            });

            // Check if history actually changed using a more reliable comparison
            let hasChanges = false;

            // Different number of jobs
            if (updatedHistory.length !== jobHistory.length) {
                hasChanges = true;
                console.log('Change detected: Different job counts');
            } else {
                // Compare each job's key properties
                for (let i = 0; i < updatedHistory.length; i++) {
                    const updated = updatedHistory[i];
                    const current = jobHistory[i];

                    if (updated.id !== current.id ||
                        updated.status !== current.status ||
                        updated.progress !== current.progress ||
                        (updated.results && !current.results) ||
                        (updated.results && current.results && updated.results.length !== current.results.length)) {
                        hasChanges = true;
                        console.log(`Change detected in job ${updated.id}:`, {
                            oldStatus: current.status,
                            newStatus: updated.status,
                            oldProgress: current.progress,
                            newProgress: updated.progress
                        });
                        break;
                    }
                }
            }

            if (hasChanges) {
                jobHistory = updatedHistory;
                console.log('✅ Auto-refreshed job history - found updates!');
                renderJobHistory();
            }
        }, 2000); // Check every 2 seconds
    } else if (page === 'analytics') {
        // Hide progress section
        progressSection.style.display = 'none';

        // Stop auto-refresh when leaving job tracker
        if (jobTrackerRefreshInterval) {
            clearInterval(jobTrackerRefreshInterval);
            jobTrackerRefreshInterval = null;
        }

        scraperPage.style.display = 'none';
        jobTrackerPage.style.display = 'none';
        if (analyticsPage) {
            analyticsPage.style.display = 'block';

            // Initialize analytics if available
            if (window.initAnalytics) {
                window.initAnalytics();
            }
        }
    }
}

// Functions
function handleAddSingleUsername() {
    const username = singleUsernameInput.value.trim();

    if (!username) {
        showNotification('Please enter a username', 'error');
        return;
    }

    if (usernames.includes(username)) {
        showNotification('Username already added', 'error');
        return;
    }

    usernames.push(username);
    singleUsernameInput.value = '';
    updateUsernamesList();
    updateScrapeButton();
    addActivity(`Added username: @${username}`);
    showNotification(`Added: ${username}`, 'success');
}

function handleAddMultipleUsernames() {
    const text = multipleUsernamesTextarea.value.trim();

    if (!text) {
        showNotification('Please enter usernames', 'error');
        return;
    }

    const newUsernames = text
        .split('\n')
        .map(u => u.trim())
        .filter(u => u && !usernames.includes(u));

    if (newUsernames.length === 0) {
        showNotification('No new usernames to add', 'error');
        return;
    }

    usernames.push(...newUsernames);
    multipleUsernamesTextarea.value = '';
    updateUsernamesList();
    updateScrapeButton();
    addActivity(`Added ${newUsernames.length} usernames in bulk`);
    showNotification(`Added ${newUsernames.length} username(s)`, 'success');
}

function removeUsername(username) {
    usernames = usernames.filter(u => u !== username);
    updateUsernamesList();
    updateScrapeButton();
    addActivity(`Removed username: @${username}`);
    showNotification(`Removed: ${username}`, 'success');
}

function handleClearAll() {
    if (usernames.length === 0) return;

    if (confirm(`Clear all ${usernames.length} username(s)?`)) {
        const count = usernames.length;
        usernames = [];
        updateUsernamesList();
        updateScrapeButton();
        addActivity(`Cleared all ${count} usernames`);
        showNotification('All usernames cleared', 'success');
    }
}

function updateUsernamesList() {
    if (usernames.length === 0) {
        usernamesSection.style.display = 'none';
        usernamesList.innerHTML = '';
        return;
    }

    usernamesSection.style.display = 'block';
    usernamesList.innerHTML = usernames
        .map(username => `
            <div class="username-tag">
                <span>@${username}</span>
                <button class="remove-btn" onclick="removeUsername('${username}')" title="Remove">
                    ×
                </button>
            </div>
        `)
        .join('');
}

function updateScrapeButton() {
    scrapeBtn.disabled = usernames.length === 0;
    updateSidebarStats();
}

// Function to load usernames from a group (called from groups.js)
window.loadUsernamesFromGroup = function(groupUsernames, groupId) {
    console.log('Loading usernames from group:', groupId, groupUsernames);

    // Clear existing usernames
    usernames = [];

    // Add group usernames
    usernames.push(...groupUsernames);

    // Store the group ID for usage tracking when scraping
    currentLoadedGroupId = groupId;

    // Update UI
    updateUsernamesList();
    updateScrapeButton();
    addActivity(`Loaded ${groupUsernames.length} usernames from group`);

    // Switch to scraper page if not already there
    if (currentPage !== 'scraper') {
        navigateToPage('scraper');
    }

    // Scroll to usernames section
    usernamesSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

function updateSidebarStats() {
    // Update total usernames
    statTotalUsernames.textContent = usernames.length;

    // Update reels count
    const reelCount = parseInt(reelCountInput.value) || 20;
    statReelsCount.textContent = reelCount;

    // Update status
    if (usernames.length === 0) {
        statStatus.textContent = 'Ready';
        statStatus.style.color = 'var(--success-color)';
    } else {
        statStatus.textContent = `${usernames.length} Ready`;
        statStatus.style.color = 'var(--accent-purple)';
    }
}

function addActivity(message, type = 'info') {
    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';

    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    activityItem.innerHTML = `
        <div>${message}</div>
        <div class="activity-time">${timeStr}</div>
    `;

    // Remove empty state if it exists
    const emptyState = activityList.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    // Add to top of list
    activityList.insertBefore(activityItem, activityList.firstChild);

    // Keep only last 10 activities
    const items = activityList.querySelectorAll('.activity-item');
    if (items.length > 10) {
        items[items.length - 1].remove();
    }
}

async function pollJobStatus(backendJobId, localJobId) {
    // Track this polling job
    activePollingJobs.add(backendJobId);

    console.log('🎯 STARTING POLLING:', {
        backendJobId,
        localJobId,
        timestamp: new Date().toISOString(),
        activePollingCount: activePollingJobs.size
    });

    // Store in window for debugging
    window.currentPollingJob = {
        backendJobId,
        localJobId,
        startTime: Date.now()
    };

    // Poll the backend for job status updates
    const pollInterval = 2000; // Poll every 2 seconds
    let attempts = 0;
    const maxAttempts = 300; // 10 minutes max (300 * 2 seconds)

    const poll = async () => {
        try {
            attempts++;

            console.log(`\n${'='.repeat(60)}`);
            console.log(`📊 POLLING ATTEMPT #${attempts}`);
            console.log(`   Backend Job ID: ${backendJobId}`);
            console.log(`   Local Job ID: ${localJobId}`);
            console.log(`   Time: ${new Date().toLocaleTimeString()}`);
            console.log(`${'='.repeat(60)}\n`);

            const headers = {
                'Content-Type': 'application/json'
            };

            // Add auth token if available
            if (authToken) {
                headers['Authorization'] = `Bearer ${authToken}`;
            }

            const response = await fetch(`${API_URL}/api/job/${backendJobId}`, {
                method: 'GET',
                headers: headers,
                cache: 'no-cache' // Prevent caching
            });

            console.log('Response received:', {
                ok: response.ok,
                status: response.status,
                statusText: response.statusText
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Bad response:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const jobData = await response.json();

            console.log('✅ Job data received:', {
                status: jobData.status,
                progress: jobData.progress,
                current_username: jobData.current_username,
                results_count: jobData.results ? jobData.results.length : 0
            });

            // CRITICAL: Reload jobHistory from localStorage to get the latest version
            const latestHistory = localStorage.getItem('jobHistory');
            if (latestHistory) {
                jobHistory = JSON.parse(latestHistory);
                console.log('📥 Reloaded jobHistory from localStorage:', jobHistory.length, 'jobs');
            }

            // Update local job with backend data
            const jobIndex = jobHistory.findIndex(j => j.id === localJobId);
            console.log('Looking for local job:', {
                localJobId,
                foundAtIndex: jobIndex,
                totalJobs: jobHistory.length
            });

            if (jobIndex !== -1) {
                console.log('Before update:', {
                    status: jobHistory[jobIndex].status,
                    progress: jobHistory[jobIndex].progress
                });

                jobHistory[jobIndex].progress = jobData.progress || 0;
                jobHistory[jobIndex].backendJobId = backendJobId;

                if (jobData.status === 'completed') {
                    console.log('🎉 JOB COMPLETED! Updating status...');

                    jobHistory[jobIndex].status = 'success';
                    jobHistory[jobIndex].results = jobData.results;
                    jobHistory[jobIndex].endTime = Date.now();
                    jobHistory[jobIndex].duration = jobData.duration ? jobData.duration * 1000 : (Date.now() - jobHistory[jobIndex].startTime);
                    jobHistory[jobIndex].progress = 100;

                    console.log('After update:', {
                        status: jobHistory[jobIndex].status,
                        progress: jobHistory[jobIndex].progress,
                        results: jobHistory[jobIndex].results.length
                    });

                    saveJobHistory();

                    console.log('✅ Job status saved to localStorage');
                    console.log('✅ POLLING COMPLETE - JOB FINISHED SUCCESSFULLY');

                    // Remove from active polling
                    activePollingJobs.delete(backendJobId);
                    console.log('📊 Active polling jobs:', activePollingJobs.size);

                    // Update UI
                    statStatus.textContent = 'Completed';
                    statStatus.style.color = 'var(--success-color)';
                    addActivity(`Scraping completed successfully`);
                    showNotification('Scraping completed successfully!', 'success');

                    // Refresh credit info
                    loadCreditInfo();

                    // Re-enable inputs
                    addUsernameBtn.disabled = false;
                    addMultipleBtn.disabled = false;
                    clearAllBtn.disabled = false;
                    updateScrapeButton();

                    return; // Stop polling
                } else if (jobData.status === 'running') {
                    console.log('⏳ Job still running, will poll again in 2 seconds...');
                    jobHistory[jobIndex].progress = jobData.progress || 0;
                    saveJobHistory();

                    // Continue polling
                    if (attempts < maxAttempts) {
                        setTimeout(poll, pollInterval);
                    } else {
                        console.error('❌ Polling timed out after maximum attempts');
                        throw new Error('Job polling timed out');
                    }
                } else {
                    console.warn('⚠️ Unexpected job status:', jobData.status);
                    saveJobHistory();
                }
            } else {
                console.error('❌ Could not find job in jobHistory!', {
                    lookingFor: localJobId,
                    availableIds: jobHistory.map(j => j.id)
                });
            }

        } catch (error) {
            console.error('\n❌❌❌ POLLING ERROR ❌❌❌');
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                attempt: attempts
            });

            // Remove from active polling
            activePollingJobs.delete(backendJobId);
            console.log('📊 Active polling jobs after error:', activePollingJobs.size);

            // Reload jobHistory before updating
            const latestHistory = localStorage.getItem('jobHistory');
            if (latestHistory) {
                jobHistory = JSON.parse(latestHistory);
            }

            const jobIndex = jobHistory.findIndex(j => j.id === localJobId);
            if (jobIndex !== -1) {
                jobHistory[jobIndex].status = 'failed';
                jobHistory[jobIndex].error = error.message;
                jobHistory[jobIndex].endTime = Date.now();
                jobHistory[jobIndex].duration = Date.now() - jobHistory[jobIndex].startTime;
                saveJobHistory();
                console.log('💾 Saved failed job status to localStorage');
            }

            statStatus.textContent = 'Error';
            statStatus.style.color = 'var(--error-color)';
            addActivity(`Scraping failed: ${error.message}`);
            showNotification(`Error: ${error.message}`, 'error');

            // Re-enable inputs
            addUsernameBtn.disabled = false;
            addMultipleBtn.disabled = false;
            clearAllBtn.disabled = false;
            updateScrapeButton();
        }
    };

    // Start polling
    console.log('⏰ Scheduling first poll in 2 seconds...');
    setTimeout(poll, pollInterval);
}

async function handleScrape() {
    const reelCount = parseInt(reelCountInput.value) || 20;

    if (reelCount < 1) {
        showNotification('Please enter a valid number of reels', 'error');
        return;
    }

    if (usernames.length === 0) {
        showNotification('Please add at least one username', 'error');
        return;
    }

    // Create local job record
    const localJobId = Date.now();
    const job = {
        id: localJobId,
        timestamp: new Date().toISOString(),
        usernames: [...usernames],
        reelCount: reelCount,
        status: 'running',
        results: [],
        startTime: Date.now(),
        progress: 0,
        backendJobId: null
    };

    addJobToHistory(job);

    // Store current job ID for tracking
    window.currentJobId = localJobId;

    // Update status
    statStatus.textContent = 'Scraping...';
    statStatus.style.color = 'var(--warning-color)';
    addActivity(`Started scraping ${usernames.length} account(s)`);

    // Hide progress section
    progressSection.style.display = 'none';

    // Disable inputs
    scrapeBtn.disabled = true;
    addUsernameBtn.disabled = true;
    addMultipleBtn.disabled = true;
    clearAllBtn.disabled = true;

    try {
        console.log('🚀 Sending scrape request to backend...', {
            usernames: usernames,
            reel_count: reelCount,
            group_id: currentLoadedGroupId,
            timestamp: new Date().toISOString()
        });

        // Prepare request body
        const requestBody = {
            usernames: usernames,
            reel_count: reelCount
        };

        // Include group_id if usernames were loaded from a group
        if (currentLoadedGroupId) {
            requestBody.group_id = currentLoadedGroupId;
        }

        // Prepare headers
        const headers = {
            'Content-Type': 'application/json'
        };

        // Add auth token if available
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        // Send request to start job (returns immediately)
        const response = await fetch(`${API_URL}/api/scrape`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(requestBody)
        });

        // Clear the loaded group ID after scraping starts
        currentLoadedGroupId = null;

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const data = await response.json();
        console.log('✅ Job started:', data);

        if (data.job_id) {
            // Update local job with backend job ID
            const jobIndex = jobHistory.findIndex(j => j.id === localJobId);
            if (jobIndex !== -1) {
                jobHistory[jobIndex].backendJobId = data.job_id;
                saveJobHistory();
                console.log('💾 Updated job with backend job ID:', data.job_id);
            } else {
                console.error('❌ Could not find local job to update with backend job ID!');
            }

            // Start polling for status
            console.log('🚀 ABOUT TO START POLLING...');
            try {
                pollJobStatus(data.job_id, localJobId);
                console.log('✅ Polling function called successfully');
            } catch (pollError) {
                console.error('❌ ERROR calling pollJobStatus:', pollError);
                throw pollError;
            }

            showNotification('Scraping job started! Check Job Tracker for progress.', 'success');
        } else {
            throw new Error('No job_id received from server');
        }

    } catch (error) {
        console.error('Fetch error:', error);

        let errorMessage = error.message || 'Unknown error';

        if (error.message === 'Failed to fetch') {
            errorMessage = 'Network error. Please check if the backend server is running on localhost:8080';
        }

        showNotification(`Error: ${errorMessage}`, 'error');
        statStatus.textContent = 'Error';
        statStatus.style.color = 'var(--error-color)';
        addActivity(`Scraping failed: ${errorMessage}`);

        // Update job status
        const jobIndex = jobHistory.findIndex(j => j.id === localJobId);
        if (jobIndex !== -1) {
            jobHistory[jobIndex].status = 'failed';
            jobHistory[jobIndex].error = errorMessage;
            jobHistory[jobIndex].endTime = Date.now();
            jobHistory[jobIndex].duration = Date.now() - jobHistory[jobIndex].startTime;
            saveJobHistory();
        }

        // Re-enable inputs
        addUsernameBtn.disabled = false;
        addMultipleBtn.disabled = false;
        clearAllBtn.disabled = false;
        updateScrapeButton();
    }
}

function showNotification(message, type = 'info') {
    // Simple console notification for now
    // You can enhance this with a toast notification library
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Global error and success notification functions (used by groups.js and analytics.js)
window.showError = function(message) {
    showNotification(message, 'error');
    console.error('❌', message);
};

window.showSuccess = function(message) {
    showNotification(message, 'success');
    console.log('✅', message);
};

// Job History Management
function addJobToHistory(job) {
    jobHistory.unshift(job); // Add to beginning
    saveJobHistory();
}

function saveJobHistory() {
    // Keep only last 50 jobs
    if (jobHistory.length > 50) {
        jobHistory = jobHistory.slice(0, 50);
    }
    const jsonData = JSON.stringify(jobHistory);
    localStorage.setItem('jobHistory', jsonData);
    console.log('💾 Saved job history to localStorage:', jobHistory.length, 'jobs');

    // Verify save was successful
    const verification = localStorage.getItem('jobHistory');
    if (verification !== jsonData) {
        console.error('❌ LocalStorage save verification failed! Retrying...');
        localStorage.setItem('jobHistory', jsonData);
    } else {
        console.log('✅ LocalStorage save verified successfully');
    }
}

function handleClearHistory() {
    if (jobHistory.length === 0) return;

    if (confirm(`Clear all ${jobHistory.length} job(s) from history?`)) {
        jobHistory = [];
        localStorage.removeItem('jobHistory');
        renderJobHistory();
        addActivity('Cleared job history');
    }
}

function renderJobHistory() {
    if (jobHistory.length === 0) {
        jobsList.innerHTML = '<div class="empty-state">No jobs yet. Start scraping to see job history.</div>';
        return;
    }

    jobsList.innerHTML = jobHistory.map(job => {
        const timestamp = formatDateTimeDDMMYYYY(job.timestamp);
        const duration = job.duration ? formatDuration(job.duration) : 'N/A';
        const successCount = job.results ? job.results.filter(r => r.status === 'success').length : 0;
        const failedCount = job.results ? job.results.filter(r => r.status === 'failed').length : 0;

        return `
            <div class="job-card ${job.status}">
                <div class="job-header">
                    <div>
                        <div class="job-title">Job #${job.id}</div>
                        <div class="job-timestamp">${timestamp}</div>
                    </div>
                    <span class="job-status-badge ${job.status}">${job.status}</span>
                </div>

                ${job.status === 'running' ? `
                    <div class="job-progress">
                        <div class="job-progress-bar">
                            <div class="job-progress-fill"></div>
                        </div>
                        <div class="job-progress-text">Scraping in progress... Please check back later</div>
                    </div>
                ` : ''}

                <div class="job-details">
                    <div class="job-detail-item">
                        <div class="job-detail-label">Accounts</div>
                        <div class="job-detail-value">${job.usernames.length}</div>
                    </div>
                    <div class="job-detail-item">
                        <div class="job-detail-label">Reels per Account</div>
                        <div class="job-detail-value">${job.reelCount}</div>
                    </div>
                    <div class="job-detail-item">
                        <div class="job-detail-label">Duration</div>
                        <div class="job-detail-value">${duration}</div>
                    </div>
                    ${job.status === 'success' ? `
                        <div class="job-detail-item">
                            <div class="job-detail-label">Success</div>
                            <div class="job-detail-value" style="color: var(--success-color)">${successCount}</div>
                        </div>
                        <div class="job-detail-item">
                            <div class="job-detail-label">Failed</div>
                            <div class="job-detail-value" style="color: var(--error-color)">${failedCount}</div>
                        </div>
                    ` : ''}
                    ${job.status === 'failed' && job.error ? `
                        <div class="job-detail-item">
                            <div class="job-detail-label">Error</div>
                            <div class="job-detail-value" style="color: var(--error-color)">${job.error}</div>
                        </div>
                    ` : ''}
                </div>

                <div class="job-accounts">
                    <div class="job-accounts-title">Target Accounts</div>
                    <div class="job-accounts-list">
                        ${job.usernames.map(u => `<span class="account-badge">@${u}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
}

// Initialize
updateScrapeButton();
updateSidebarStats();

// Ensure progress section is hidden on page load
progressSection.style.display = 'none';

// Restore current page from localStorage
if (currentPage !== 'scraper') {
    navigateToPage(currentPage);
}

// CRITICAL: Check for running jobs on page load and resume polling
console.log('🔄 PAGE LOADED - Checking for running jobs...');
const runningJobs = jobHistory.filter(job => job.status === 'running' && job.backendJobId);
console.log('Found running jobs:', runningJobs.length);

if (runningJobs.length > 0) {
    console.log('⚠️ RESUMING POLLING for running jobs:', runningJobs.map(j => ({
        localId: j.id,
        backendId: j.backendJobId,
        usernames: j.usernames
    })));

    runningJobs.forEach(job => {
        console.log(`🔄 Resuming polling for job: ${job.backendJobId}`);
        pollJobStatus(job.backendJobId, job.id);
    });

    // Update UI to show scraping in progress
    statStatus.textContent = 'Scraping...';
    statStatus.style.color = 'var(--warning-color)';
    addActivity('Resumed monitoring active scraping jobs');
}

// Prevent accidental page reloads
window.addEventListener('beforeunload', (e) => {
    const activeJobs = jobHistory.filter(j => j.status === 'running');
    if (activeJobs.length > 0) {
        console.log('⚠️ USER ATTEMPTING TO LEAVE PAGE with active jobs!');
        // Don't actually prevent leaving - just log it
        // e.preventDefault();
        // e.returnValue = '';
    }
});

// Log any unhandled errors that might cause reloads
window.addEventListener('error', (e) => {
    console.error('🚨 UNHANDLED ERROR DETECTED:', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error
    });
});

// Log any unhandled promise rejections
window.addEventListener('unhandledrejection', (e) => {
    console.error('🚨 UNHANDLED PROMISE REJECTION:', {
        reason: e.reason,
        promise: e.promise
    });
});

// Make removeUsername available globally
window.removeUsername = removeUsername;

// ==================== Credit Information ====================

async function loadCreditInfo() {
    try {
        // Use the correct token key - authToken, not access_token
        const token = window.authUtils?.getAuthToken();
        if (!token) {
            console.warn('⚠️ No access token found, skipping credit load');
            return;
        }

        console.log('📊 Loading credit info...');
        const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const user = await response.json();
            console.log('✓ Credit info loaded:', {
                used: user.credits_used_today,
                limit: user.daily_credit_limit,
                remaining: user.daily_credit_limit - user.credits_used_today
            });
            updateCreditDisplay(user);
        } else {
            const errorText = await response.text();
            console.error('❌ Failed to load credit info:', response.status, errorText);
        }
    } catch (error) {
        console.error('❌ Exception loading credit info:', error);
    }
}

function updateCreditDisplay(user) {
    const creditsUsed = user.credits_used_today || 0;
    const creditLimit = user.daily_credit_limit || 2000;
    const creditsRemaining = creditLimit - creditsUsed;
    const usagePercent = creditLimit > 0 ? (creditsUsed / creditLimit) * 100 : 0;

    // Update text values
    statCredits.textContent = `${creditsUsed} / ${creditLimit}`;
    statCreditsRemaining.textContent = `${creditsRemaining} left`;

    // Update progress bar
    statCreditsProgress.style.width = `${usagePercent}%`;

    // Apply warning/danger colors based on usage
    statCreditsProgress.classList.remove('warning', 'danger');
    statCreditsRemaining.classList.remove('warning', 'danger');

    if (usagePercent >= 90) {
        statCreditsProgress.classList.add('danger');
        statCreditsRemaining.classList.add('danger');
    } else if (usagePercent >= 75) {
        statCreditsProgress.classList.add('warning');
        statCreditsRemaining.classList.add('warning');
    }
}

// Load credit info on page load
loadCreditInfo();

// Refresh credit info every 30 seconds
setInterval(loadCreditInfo, 30000);

console.log('✅ Application initialized successfully');
