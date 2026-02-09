// Authentication JavaScript for Instagram Reel Scraper
// Handles login, signup, and token management

const API_URL = '';

// ==================== DOM Elements ====================
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const formTabs = document.querySelectorAll('.form-tab');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// Login form elements
const loginEmail = document.getElementById('loginEmail');
const loginPassword = document.getElementById('loginPassword');
const loginBtn = document.getElementById('loginBtn');

// Signup form elements
const signupUsername = document.getElementById('signupUsername');
const signupEmail = document.getElementById('signupEmail');
const signupPassword = document.getElementById('signupPassword');
const signupPasswordConfirm = document.getElementById('signupPasswordConfirm');
const signupBtn = document.getElementById('signupBtn');

// ==================== Utility Functions ====================

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    successMessage.classList.remove('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.classList.add('show');
    errorMessage.classList.remove('show');
    setTimeout(() => {
        successMessage.classList.remove('show');
    }, 5000);
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = button.textContent + '<span class="loading"></span>';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

function saveAuthToken(token) {
    localStorage.setItem('authToken', token);
    console.log('✅ Auth token saved to localStorage');
}

function saveUserInfo(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
    console.log('✅ User info saved:', user);
}

function getAuthToken() {
    return localStorage.getItem('authToken');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
}

function clearAuth() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    console.log('🔒 Auth cleared');
}

function redirectToApp() {
    window.location.href = '/static/index.html';
}

// ==================== Form Tab Switching ====================

// Only attach event listeners if elements exist (login page)
if (formTabs && formTabs.length > 0) {
    formTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Update active tab
            formTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show/hide forms
            if (tabName === 'login') {
                loginForm.style.display = 'block';
                signupForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                signupForm.style.display = 'block';
            }

            // Clear messages
            errorMessage.classList.remove('show');
            successMessage.classList.remove('show');
        });
    });
}

// ==================== Login Handler ====================

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = loginEmail.value.trim();
        const password = loginPassword.value;

        if (!email || !password) {
            showError('Please enter both email and password');
            return;
        }

        setLoading(loginBtn, true);

        try {
            console.log('🔐 Attempting login for:', email);

            const response = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            console.log('✅ Login successful:', data);

            // Save token and user info
            saveAuthToken(data.access_token);
            saveUserInfo(data.user);

            showSuccess('Login successful! Redirecting...');

            // Redirect to app after short delay
            setTimeout(() => {
                redirectToApp();
            }, 1000);

        } catch (error) {
            console.error('❌ Login error:', error);
            showError(error.message || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(loginBtn, false);
        }
    });
}

// ==================== Signup Handler ====================

if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = signupUsername.value.trim();
        const email = signupEmail.value.trim();
        const password = signupPassword.value;
        const passwordConfirm = signupPasswordConfirm.value;

        // Validation
        if (!username || !email || !password || !passwordConfirm) {
            showError('Please fill in all fields');
            return;
        }

        if (username.length < 3) {
            showError('Username must be at least 3 characters');
            return;
        }

        if (password.length < 8) {
            showError('Password must be at least 8 characters');
            return;
        }

        if (!/[0-9]/.test(password) || !/[a-zA-Z]/.test(password)) {
            showError('Password must contain both letters and numbers');
            return;
        }

        if (password !== passwordConfirm) {
            showError('Passwords do not match');
            return;
        }

        setLoading(signupBtn, true);

        try {
            console.log('📝 Attempting signup for:', email);

            const response = await fetch(`${API_URL}/api/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Signup failed');
            }

            console.log('✅ Signup successful:', data);

            showSuccess('Account created successfully! Please login.');

            // Switch to login tab after short delay
            setTimeout(() => {
                document.querySelector('[data-tab="login"]').click();
                loginEmail.value = email;
                loginPassword.value = password;
            }, 1500);

        } catch (error) {
            console.error('❌ Signup error:', error);
            showError(error.message || 'Signup failed. Please try again.');
        } finally {
            setLoading(signupBtn, false);
        }
    });
}

// ==================== Password Confirmation Validation ====================

if (signupPasswordConfirm) {
    signupPasswordConfirm.addEventListener('input', () => {
        const password = signupPassword.value;
        const confirmPassword = signupPasswordConfirm.value;

        if (confirmPassword && password !== confirmPassword) {
            signupPasswordConfirm.setCustomValidity('Passwords do not match');
        } else {
            signupPasswordConfirm.setCustomValidity('');
        }
    });
}

// ==================== Check if Already Logged In ====================

function checkAuthStatus() {
    const token = getAuthToken();
    const user = getCurrentUser();

    // Only redirect if we're on the login page
    if (token && user && window.location.pathname.includes('login.html')) {
        console.log('✅ User already logged in:', user.email);
        console.log('🔄 Redirecting to app...');
        redirectToApp();
    }
}

// Check auth status on page load
checkAuthStatus();

// ==================== Export for use in other files ====================

window.authUtils = {
    getAuthToken,
    getCurrentUser,
    clearAuth,
    saveAuthToken,
    saveUserInfo
};

console.log('✅ Auth module loaded');
