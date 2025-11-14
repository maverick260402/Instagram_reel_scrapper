// User Groups JavaScript for Instagram Reel Scraper
// Handles group CRUD operations and group loading

// API_URL is declared in auth.js (loaded first)
const MAX_GROUPS = 10;

// ==================== DOM Elements ====================
const groupsList = document.getElementById('groupsList');
const newGroupBtn = document.getElementById('newGroupBtn');
const groupModal = document.getElementById('groupModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelGroupBtn = document.getElementById('cancelGroupBtn');
const groupForm = document.getElementById('groupForm');
const modalTitle = document.getElementById('modalTitle');
const groupNameInput = document.getElementById('groupName');
const groupUsernamesInput = document.getElementById('groupUsernames');
const saveGroupBtn = document.getElementById('saveGroupBtn');

// State
let currentEditingGroupId = null;
let userGroups = [];

// ==================== API Calls ====================

async function fetchGroups() {
    try {
        const token = window.authUtils.getAuthToken();
        if (!token) {
            console.error('No auth token found');
            window.location.href = '/static/login.html';
            return;
        }

        const response = await fetch(`${API_URL}/api/groups`, {
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
            throw new Error('Failed to fetch groups');
        }

        const groups = await response.json();
        userGroups = groups;
        displayGroups(groups);
        return groups;
    } catch (error) {
        console.error('Error fetching groups:', error);
        showError('Failed to load groups');
    }
}

async function createGroup(name, usernames) {
    try {
        const token = window.authUtils.getAuthToken();
        if (!token) {
            window.location.href = '/static/login.html';
            return;
        }

        const response = await fetch(`${API_URL}/api/groups`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                usernames: usernames
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create group');
        }

        const newGroup = await response.json();
        console.log('✅ Group created:', newGroup);
        return newGroup;
    } catch (error) {
        console.error('Error creating group:', error);
        throw error;
    }
}

async function updateGroup(groupId, name, usernames) {
    try {
        const token = window.authUtils.getAuthToken();
        if (!token) {
            window.location.href = '/static/login.html';
            return;
        }

        const response = await fetch(`${API_URL}/api/groups/${groupId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                usernames: usernames
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update group');
        }

        const updatedGroup = await response.json();
        console.log('✅ Group updated:', updatedGroup);
        return updatedGroup;
    } catch (error) {
        console.error('Error updating group:', error);
        throw error;
    }
}

async function deleteGroup(groupId) {
    try {
        const token = window.authUtils.getAuthToken();
        if (!token) {
            window.location.href = '/static/login.html';
            return;
        }

        const response = await fetch(`${API_URL}/api/groups/${groupId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete group');
        }

        console.log('✅ Group deleted');
        return true;
    } catch (error) {
        console.error('Error deleting group:', error);
        throw error;
    }
}

// ==================== UI Functions ====================

function displayGroups(groups) {
    if (!groups || groups.length === 0) {
        groupsList.innerHTML = '<div class="empty-state">No groups yet. Create your first group to save username collections.</div>';
        return;
    }

    groupsList.innerHTML = groups.map(group => `
        <div class="group-card" data-group-id="${group.id}">
            <div class="group-header">
                <h4 class="group-name">${escapeHtml(group.name)}</h4>
                <div class="group-actions">
                    <button class="btn-icon" onclick="handleEditGroup(${group.id})" title="Edit">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M11.333 2.00004C11.5081 1.82494 11.716 1.68605 11.9447 1.59129C12.1735 1.49653 12.4187 1.44775 12.6663 1.44775C12.914 1.44775 13.1592 1.49653 13.3879 1.59129C13.6167 1.68605 13.8246 1.82494 13.9997 2.00004C14.1748 2.17513 14.3137 2.383 14.4084 2.61178C14.5032 2.84055 14.552 3.08575 14.552 3.33337C14.552 3.58099 14.5032 3.82619 14.4084 4.05497C14.3137 4.28374 14.1748 4.49161 13.9997 4.66671L5.33301 13.3334L1.33301 14.6667L2.66634 10.6667L11.333 2.00004Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="btn-icon" onclick="handleDeleteGroup(${group.id}, '${escapeHtml(group.name)}')" title="Delete">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M2 4H3.33333H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M5.33301 4.00004V2.66671C5.33301 2.31309 5.47348 1.97395 5.72353 1.7239C5.97358 1.47385 6.31272 1.33337 6.66634 1.33337H9.33301C9.68663 1.33337 10.0258 1.47385 10.2758 1.7239C10.5259 1.97395 10.6663 2.31309 10.6663 2.66671V4.00004M12.6663 4.00004V13.3334C12.6663 13.687 12.5259 14.0261 12.2758 14.2762C12.0258 14.5262 11.6866 14.6667 11.333 14.6667H4.66634C4.31272 14.6667 3.97358 14.5262 3.72353 14.2762C3.47348 14.0261 3.33301 13.687 3.33301 13.3334V4.00004H12.6663Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="group-body">
                <div class="group-stats">
                    <span class="group-stat">${group.usernames.length} username${group.usernames.length !== 1 ? 's' : ''}</span>
                    ${group.times_used > 0 ? `<span class="group-stat">Used ${group.times_used} time${group.times_used !== 1 ? 's' : ''}</span>` : ''}
                </div>
                <div class="group-usernames-preview">
                    ${group.usernames.slice(0, 3).map(u => `<span class="username-tag-small">${escapeHtml(u)}</span>`).join('')}
                    ${group.usernames.length > 3 ? `<span class="username-tag-small">+${group.usernames.length - 3} more</span>` : ''}
                </div>
            </div>
            <div class="group-footer">
                <button class="btn btn-primary btn-sm" onclick="handleLoadGroup(${group.id})">Load Group</button>
            </div>
        </div>
    `).join('');
}

function showModal(isEdit = false, group = null) {
    // Check group limit when creating new group
    if (!isEdit && userGroups.length >= MAX_GROUPS) {
        showError(`You cannot create more than ${MAX_GROUPS} groups. Delete a group to create a new one.`);
        return;
    }

    modalTitle.textContent = isEdit ? 'Edit Group' : 'Create New Group';

    if (isEdit && group) {
        groupNameInput.value = group.name;
        groupUsernamesInput.value = group.usernames.join('\n');
        currentEditingGroupId = group.id;
    } else {
        groupNameInput.value = '';
        groupUsernamesInput.value = '';
        currentEditingGroupId = null;
    }

    groupModal.style.display = 'flex';
}

function hideModal() {
    groupModal.style.display = 'none';
    groupForm.reset();
    currentEditingGroupId = null;
}

function showError(message) {
    // If there's a global error display function, use it
    // Otherwise, use alert as fallback
    if (window.showError) {
        window.showError(message);
    } else {
        alert(message);
    }
}

function showSuccess(message) {
    // If there's a global success display function, use it
    if (window.showSuccess) {
        window.showSuccess(message);
    } else {
        console.log('✅', message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== Event Handlers ====================

newGroupBtn.addEventListener('click', () => {
    showModal(false);
});

closeModalBtn.addEventListener('click', hideModal);
cancelGroupBtn.addEventListener('click', hideModal);

// Close modal when clicking outside
groupModal.addEventListener('click', (e) => {
    if (e.target === groupModal) {
        hideModal();
    }
});

groupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = groupNameInput.value.trim();
    const usernamesText = groupUsernamesInput.value.trim();

    if (!name || !usernamesText) {
        showError('Please fill in all fields');
        return;
    }

    // Parse usernames (one per line)
    const usernames = usernamesText
        .split('\n')
        .map(u => u.trim())
        .filter(u => u.length > 0);

    if (usernames.length === 0) {
        showError('Please enter at least one username');
        return;
    }

    // Disable button during save
    saveGroupBtn.disabled = true;
    saveGroupBtn.textContent = 'Saving...';

    try {
        if (currentEditingGroupId) {
            // Update existing group
            await updateGroup(currentEditingGroupId, name, usernames);
            showSuccess('Group updated successfully');
        } else {
            // Create new group
            await createGroup(name, usernames);
            showSuccess('Group created successfully');
        }

        // Refresh groups list
        await fetchGroups();

        // Close modal
        hideModal();
    } catch (error) {
        showError(error.message || 'Failed to save group');
    } finally {
        saveGroupBtn.disabled = false;
        saveGroupBtn.textContent = 'Save Group';
    }
});

// Global handlers (called from onclick in HTML)
window.handleEditGroup = function(groupId) {
    const group = userGroups.find(g => g.id === groupId);
    if (group) {
        showModal(true, group);
    }
};

window.handleDeleteGroup = async function(groupId, groupName) {
    if (!confirm(`Are you sure you want to delete the group "${groupName}"?`)) {
        return;
    }

    try {
        await deleteGroup(groupId);
        showSuccess('Group deleted successfully');
        await fetchGroups();
    } catch (error) {
        showError(error.message || 'Failed to delete group');
    }
};

window.handleLoadGroup = function(groupId) {
    const group = userGroups.find(g => g.id === groupId);
    if (!group) {
        showError('Group not found');
        return;
    }

    // Load usernames into the scraper
    // This will be called from the main script.js file
    if (window.loadUsernamesFromGroup) {
        window.loadUsernamesFromGroup(group.usernames, groupId);
        showSuccess(`Loaded ${group.usernames.length} usernames from "${group.name}"`);
    } else {
        console.error('loadUsernamesFromGroup function not found in script.js');
    }
};

// ==================== Initialize ====================

// Fetch groups when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fetchGroups);
} else {
    fetchGroups();
}

// Export for use in other files
window.groupsUtils = {
    fetchGroups,
    createGroup,
    updateGroup,
    deleteGroup
};

console.log('✅ Groups module loaded');
