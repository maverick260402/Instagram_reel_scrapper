/**
 * Date Formatting Utilities
 * Provides consistent DD-MM-YYYY formatting across the application
 * Global functions (not ES6 modules) for compatibility
 */

/**
 * Format date as DD-MM-YYYY
 * @param {string|Date} dateInput - ISO string or Date object
 * @returns {string} Formatted date or 'N/A'
 * @example
 * formatDateDDMMYYYY('2025-12-25T14:30:00') // Returns: "25-12-2025"
 */
function formatDateDDMMYYYY(dateInput) {
    if (!dateInput) return 'N/A';
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();

    return `${day}-${month}-${year}`;
}

/**
 * Format datetime as DD-MM-YYYY HH:MM:SS (24-hour format)
 * @param {string|Date} dateInput - ISO string or Date object
 * @returns {string} Formatted datetime or 'N/A'
 * @example
 * formatDateTimeDDMMYYYY('2025-12-25T14:30:45') // Returns: "25-12-2025 14:30:45"
 */
function formatDateTimeDDMMYYYY(dateInput) {
    if (!dateInput) return 'N/A';
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
}

/**
 * Format relative time (e.g., "2 hours ago")
 * Falls back to DD-MM-YYYY for dates > 7 days old
 * @param {string|Date} dateInput - ISO string or Date object
 * @returns {string} Relative time or formatted date
 * @example
 * formatRelativeTime(new Date(Date.now() - 3600000)) // Returns: "1 hour ago"
 * formatRelativeTime('2025-01-01T10:00:00') // Returns: "25-01-2025" (if > 7 days old)
 */
function formatRelativeTime(dateInput) {
    if (!dateInput) return 'N/A';
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';

    const now = new Date();
    const diffMs = now - date;
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    // Fallback to DD-MM-YYYY for older dates
    return formatDateDDMMYYYY(date);
}
