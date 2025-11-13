// API Configuration
const API_URL = 'http://localhost:8000';

// State management
let usernames = [];
let currentPage = localStorage.getItem('currentPage') || 'scraper';
let jobHistory = JSON.parse(localStorage.getItem('jobHistory')) || [];
let jobTrackerRefreshInterval = null;

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
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');

// Sidebar elements
const statTotalUsernames = document.getElementById('statTotalUsernames');
const statReelsCount = document.getElementById('statReelsCount');
const statStatus = document.getElementById('statStatus');
const activityList = document.getElementById('activityList');

// Navigation elements
const navItems = document.querySelectorAll('.nav-item');
const scraperPage = document.getElementById('scraper-page');
const jobTrackerPage = document.getElementById('job-tracker-page');
const jobsList = document.getElementById('jobsList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

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

        // Stop auto-refresh when leaving job tracker
        if (jobTrackerRefreshInterval) {
            clearInterval(jobTrackerRefreshInterval);
            jobTrackerRefreshInterval = null;
        }
    } else if (page === 'job-tracker') {
        // Hide progress and results sections when navigating away from scraper
        progressSection.style.display = 'none';
        resultsSection.style.display = 'none';

        // Reload job history from localStorage before showing
        const savedHistory = localStorage.getItem('jobHistory');
        jobHistory = savedHistory ? JSON.parse(savedHistory) : [];
        console.log('Loaded job history from localStorage:', jobHistory.length, 'jobs');

        scraperPage.style.display = 'none';
        jobTrackerPage.style.display = 'block';
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

            // Only re-render if history actually changed
            if (JSON.stringify(updatedHistory) !== JSON.stringify(jobHistory)) {
                jobHistory = updatedHistory;
                console.log('Auto-refreshed job history - found updates!');
                renderJobHistory();
            }
        }, 2000); // Check every 2 seconds
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

    // Create job record
    const jobId = Date.now();
    const job = {
        id: jobId,
        timestamp: new Date().toISOString(),
        usernames: [...usernames],
        reelCount: reelCount,
        status: 'running',
        results: [],
        startTime: Date.now(),
        progress: 0
    };

    addJobToHistory(job);

    // Store current job ID for tracking
    window.currentJobId = jobId;

    // Update status
    statStatus.textContent = 'Scraping...';
    statStatus.style.color = 'var(--warning-color)';
    addActivity(`Started scraping ${usernames.length} account(s)`);

    // Hide progress and results sections (progress only shown in Job Tracker)
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';

    // Disable inputs
    scrapeBtn.disabled = true;
    addUsernameBtn.disabled = true;
    addMultipleBtn.disabled = true;
    clearAllBtn.disabled = true;

    try {
        // Add keepalive and signal for long-running requests
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minute timeout

        console.log('🚀 Sending scrape request to backend...', {
            usernames: usernames,
            reel_count: reelCount,
            timestamp: new Date().toISOString(),
            estimated_time: `~${(usernames.length * 3 * (Math.ceil(reelCount / 50)))} seconds`
        });

        const response = await fetch(`${API_URL}/api/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                usernames: usernames,
                reel_count: reelCount
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        let data;
        try {
            data = await response.json();
            console.log('✅ Received response from backend:', {
                status: data.status,
                totalResults: data.results.length,
                successful: data.results.filter(r => r.status === 'success').length,
                failed: data.results.filter(r => r.status === 'failed').length,
                results: data.results
            });
        } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError);
            throw new Error(`Failed to parse response: ${parseError.message}`);
        }

        // Display results
        displayResults(data.results);

        // Update job status
        console.log('Looking for job with ID:', jobId);
        console.log('Current jobHistory:', jobHistory);
        const jobIndex = jobHistory.findIndex(j => j.id === jobId);
        console.log('Found job at index:', jobIndex);

        if (jobIndex !== -1) {
            console.log('Before update:', JSON.stringify(jobHistory[jobIndex]));
            jobHistory[jobIndex].status = 'success';
            jobHistory[jobIndex].results = data.results;
            jobHistory[jobIndex].endTime = Date.now();
            jobHistory[jobIndex].duration = jobHistory[jobIndex].endTime - jobHistory[jobIndex].startTime;
            jobHistory[jobIndex].progress = 100;
            console.log('After update:', JSON.stringify(jobHistory[jobIndex]));
            saveJobHistory();
            console.log('✅ Job updated to SUCCESS and saved to localStorage');
        } else {
            console.error('❌ Could not find job to update. JobId:', jobId);
            console.error('Available job IDs:', jobHistory.map(j => j.id));
        }

        // Update status
        statStatus.textContent = 'Completed';
        statStatus.style.color = 'var(--success-color)';
        addActivity(`Scraping completed successfully`);

        showNotification('Scraping completed successfully!', 'success');

    } catch (error) {
        console.error('Fetch error:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);

        let errorMessage = error.message;

        // Handle abort/timeout errors
        if (error.name === 'AbortError') {
            errorMessage = 'Request timed out after 10 minutes. The scraping may still be running on the server.';
        } else if (error.message === 'Failed to fetch') {
            errorMessage = 'Network error. Please check if the backend server is running on localhost:8000';
        }

        showNotification(`Error: ${errorMessage}`, 'error');
        statStatus.textContent = 'Error';
        statStatus.style.color = 'var(--error-color)';
        addActivity(`Scraping failed: ${errorMessage}`);

        // Update job status
        const jobIndex = jobHistory.findIndex(j => j.id === jobId);
        if (jobIndex !== -1) {
            jobHistory[jobIndex].status = 'failed';
            jobHistory[jobIndex].error = errorMessage;
            jobHistory[jobIndex].endTime = Date.now();
            jobHistory[jobIndex].duration = jobHistory[jobIndex].endTime - jobHistory[jobIndex].startTime;
            saveJobHistory();
            console.log('Job updated to FAILED:', jobHistory[jobIndex]);
        } else {
            console.error('Could not find job to update:', jobId);
        }
    } finally {
        // Re-enable inputs
        addUsernameBtn.disabled = false;
        addMultipleBtn.disabled = false;
        clearAllBtn.disabled = false;
        updateScrapeButton();
    }
}

function displayResults(results) {
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = '';

    results.forEach(result => {
        const resultDiv = document.createElement('div');
        resultDiv.className = `result-item ${result.status}`;

        let content = `
            <h4>@${result.username}</h4>
            <span class="status ${result.status}">${result.status}</span>
        `;

        if (result.status === 'success') {
            content += `
                <p><strong>Reels Scraped:</strong> ${result.reels_scraped}</p>
                <p><strong>CSV Path:</strong> <span class="file-path">${result.csv_path}</span></p>
                <p><strong>JSON Path:</strong> <span class="file-path">${result.json_path}</span></p>
            `;
        } else if (result.error) {
            content += `
                <p><strong>Error:</strong> ${result.error}</p>
            `;
        }

        resultDiv.innerHTML = content;
        resultsContainer.appendChild(resultDiv);
    });

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showNotification(message, type = 'info') {
    // Simple console notification for now
    // You can enhance this with a toast notification library
    console.log(`[${type.toUpperCase()}] ${message}`);
}

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
    console.log('Saved job history to localStorage:', jobHistory.length, 'jobs');
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
        const timestamp = new Date(job.timestamp).toLocaleString();
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

// Ensure progress and results sections are hidden on page load
progressSection.style.display = 'none';
resultsSection.style.display = 'none';

// Restore current page from localStorage
if (currentPage !== 'scraper') {
    navigateToPage(currentPage);
}

// Make removeUsername available globally
window.removeUsername = removeUsername;
