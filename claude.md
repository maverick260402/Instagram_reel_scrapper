# Instagram Reel Scraper

A full-stack web application for scraping Instagram reel metadata with a modern, dark-themed user interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Frontend Guide](#frontend-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This application allows users to scrape Instagram reel metadata from multiple accounts with a sleek, user-friendly interface. The backend uses FastAPI for high performance, while the frontend provides an intuitive experience with a black, purple, and white color scheme.

## ✨ Features

### Backend Features
- **FastAPI Server** - High-performance async API
- **Pagination Support** - Efficiently fetch large numbers of reels
- **Multi-User Scraping** - Process multiple Instagram accounts in one request
- **Data Export** - Automatically saves data as JSON and CSV
- **Error Handling** - Robust error management with detailed feedback
- **Rate Limiting Protection** - Built-in delays to avoid Instagram rate limits

### Frontend Features
- **Dual Input Modes**:
  - Single username input with "Add" button
  - Bulk username input via textarea (one per line)
- **Interactive Username Management** - Add, view, and remove usernames dynamically
- **Configurable Reel Count** - Specify how many reels to scrape per account
- **Real-time Progress Tracking** - Visual progress bar during scraping
- **Results Dashboard** - Detailed success/failure status for each account
- **Dark Theme UI** - Black background, white text, purple accents
- **Responsive Design** - Works on desktop and mobile devices

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Requests** - HTTP library for API calls
- **Pandas** - Data manipulation and CSV export
- **Zstandard** - Compression handling
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with animations
- **HTML5** - Semantic markup
- **Fetch API** - Backend communication

## 📁 Project Structure

```
Instagram_reel_scrapper/
├── Backend/
│   ├── Scripts/
│   │   └── pipeline.py          # Core scraping logic
│   ├── app.py                    # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   └── output_json/              # Generated data (created at runtime)
│       └── {username}/
│           ├── meta_data.json    # Raw Instagram API response
│           └── scrapped_data.csv # Extracted reel metadata
│
└── Frontend/
    ├── index.html                # Main application page
    ├── styles.css                # UI styling
    └── script.js                 # Frontend logic
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser

### Step 1: Clone or Navigate to Project
```bash
cd "d:\ThunderBolts\Project Tres\Script_Based_Solution\Instagram_reel_scrapper"
```

### Step 2: Install Backend Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import fastapi, uvicorn, pandas; print('All dependencies installed!')"
```

## 📖 Usage

### Starting the Application

1. **Start the Backend Server**:
   ```bash
   cd Backend
   python app.py
   ```
   The server will start on `http://localhost:8000`

2. **Open the Frontend**:
   - Open `Frontend/index.html` in your web browser
   - Or visit `http://localhost:8000` if configured to serve frontend

### Using the Web Interface

#### Method 1: Single Username Entry
1. Enter an Instagram username in the "Add Single Username" field
2. Click the "Add" button
3. Repeat for multiple accounts
4. View added usernames as purple tags
5. Remove individual usernames by clicking the "×" button

#### Method 2: Bulk Username Entry
1. Click in the "Add Multiple Usernames" textarea
2. Enter usernames, one per line:
   ```
   username1
   username2
   username3
   ```
3. Click "Submit All" to add all usernames at once

#### Scraping Reels
1. Add usernames using either method
2. Set the "Number of Reels" (default: 20)
3. Click "Start Scraping"
4. Monitor progress in the progress bar
5. View results when complete

### Output Files

For each username, the system creates:
- `Backend/output_json/{username}/meta_data.json` - Complete Instagram API response
- `Backend/output_json/{username}/scrapped_data.csv` - Extracted data with columns:
  - `pk` - Post ID
  - `code` - Short code
  - `play_count` - Number of plays
  - `comment_count` - Number of comments
  - `like_count` - Number of likes
  - `url` - Direct URL to the reel

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET `/`
Serves the main application page.

**Response**: HTML page

---

#### POST `/api/scrape`
Scrapes Instagram reels for specified usernames.

**Request Body**:
```json
{
  "usernames": ["username1", "username2"],
  "reel_count": 20
}
```

**Response**:
```json
{
  "status": "completed",
  "results": [
    {
      "username": "username1",
      "status": "success",
      "reels_scraped": 20,
      "csv_path": "path/to/scrapped_data.csv",
      "json_path": "path/to/meta_data.json"
    }
  ]
}
```

**Error Response**:
```json
{
  "username": "username1",
  "status": "failed",
  "error": "Error message"
}
```

## 🎨 Frontend Guide

### Color Scheme
- **Background**: `#000000` (Black)
- **Text**: `#FFFFFF` (White)
- **Primary Accent**: `#9333ea` (Purple)
- **Hover State**: `#a855f7` (Light Purple)
- **Success**: `#10b981` (Green)
- **Error**: `#ef4444` (Red)

### Key Components

#### Username Tags
- Display added usernames as purple pill-shaped tags
- Click "×" to remove individual usernames
- Animated entry with slide-in effect

#### Progress Bar
- Gradient purple fill
- Smooth width transitions
- Percentage display when active

#### Results Display
- Color-coded status badges (green for success, red for error)
- File paths in monospace font
- Collapsible details per username

### Customization

To modify the API endpoint, edit `Frontend/script.js`:
```javascript
const API_URL = 'http://localhost:8000'; // Change this
```

## ⚙️ Configuration

### Backend Configuration

Edit `Backend/app.py` to customize:

**Server Port**:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

**CORS Settings**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Scraping Configuration

Edit `Backend/Scripts/pipeline.py` for:

**Sleep Between Requests** (avoid rate limiting):
```python
fetch_reels_paginated(..., sleep_seconds=3.0)  # Adjust timing
```

**Max Reels Per Page**:
```python
fetch_reels_paginated(..., max_per_page=50)  # Change batch size
```

**Session Cookies**:
Update the `cookie` field in headers with your Instagram session cookie for authenticated requests.

## 🔧 Troubleshooting

### Common Issues

**1. "Could not find target_id" Error**
- **Cause**: Invalid username or Instagram changed their HTML structure
- **Solution**: Verify username exists, check if account is public, update session cookie

**2. Rate Limiting / Blocked Requests**
- **Cause**: Too many requests to Instagram
- **Solution**: Increase `sleep_seconds` parameter, use valid session cookies

**3. CORS Errors in Browser**
- **Cause**: Frontend trying to access backend from different origin
- **Solution**: Ensure CORS is enabled in `app.py`, or serve frontend from same server

**4. Empty Results**
- **Cause**: Private account or no reels available
- **Solution**: Verify account has public reels, check account privacy settings

**5. Server Won't Start**
- **Cause**: Port already in use or missing dependencies
- **Solution**:
  ```bash
  # Check port usage
  netstat -ano | findstr :8000

  # Reinstall dependencies
  pip install -r requirements.txt --force-reinstall
  ```

### Debug Mode

Enable FastAPI debug mode in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="debug")
```

View console logs in:
- **Backend**: Terminal where `python app.py` is running
- **Frontend**: Browser Developer Tools (F12) → Console tab

## 📝 Notes

- **Instagram Session**: For better reliability, provide a valid Instagram session cookie in the headers
- **Rate Limits**: Instagram may rate limit requests. Adjust sleep timings as needed
- **Data Privacy**: Be mindful of Instagram's Terms of Service when scraping data
- **Session Expiry**: Cookies expire periodically and need to be refreshed

---

## 🚀 Phase 1: Multi-User System (NEW)

**Status**: ✅ Implemented
**Date**: December 2025

### Overview

Phase 1 adds multi-user support with intelligent Instagram account rotation, credit-based usage limits, and comprehensive activity tracking. The system can now handle multiple users scraping simultaneously using a pool of Instagram accounts.

### New Features

#### 1. Instagram Account Pool & Rotation
- **Multiple Instagram Accounts**: System maintains a pool of Instagram accounts for scraping
- **Intelligent Rotation**: Automatically selects the least-used Instagram account for each job
- **Usage Tracking**: Tracks daily and lifetime usage statistics per account
- **Health Monitoring**: Monitors cookie freshness and account status

#### 2. Credit System
- **Daily Quotas**: Each user has a configurable daily credit limit (default: 2000 reels)
- **1 Credit = 1 Reel**: Credits are consumed for each successfully scraped reel
- **Automatic Reset**: Credits reset daily at midnight
- **Admin Control**: Admins can set custom limits per user

#### 3. Activity Logging
- **Comprehensive Logging**: All scraping events, account rotations, and admin actions are logged
- **Debugging**: Detailed logs help troubleshoot issues
- **Analytics**: Track usage patterns and system health

#### 4. Database Enhancements
- **New Tables**: `instagram_accounts`, `api_keys`, `admin_users`, `activity_logs`
- **Enhanced Tracking**: Jobs and reels now linked to Instagram accounts used
- **Better Analytics**: More detailed usage tracking

### Database Schema Changes

#### New Tables

**instagram_accounts** - Pool of Instagram accounts
- id, username, email, password
- cookies, cookie_string, x_csrf_token
- is_active, is_paused
- daily_scrape_count, total_scrapes, success_count, failure_count
- Usage tracking timestamps

**api_keys** - Authentication for remote cookie updates
- id, key_name, api_key (hashed)
- is_active, permissions
- last_used_at

**admin_users** - Admin panel authentication
- id, username, email, password_hash
- is_active, last_login

**activity_logs** - Event logging
- id, event_type, user_id, instagram_account_id, job_id
- details (JSONB), created_at

#### Modified Tables

**users** - Added credit system fields
- daily_credit_limit (default: 2000)
- credits_used_today
- last_credit_reset_date

**scraping_jobs** - Added Instagram account tracking
- instagram_account_id (which account was used)
- credits_consumed (total credits used by job)

**scraped_reels** - Added Instagram account tracking
- instagram_account_id

### New Backend Modules

#### [account_rotation.py](Backend/account_rotation.py)
Handles intelligent account selection and rotation.

**Key Functions**:
- `get_least_used_account()` - Select least-used active account
- `increment_account_usage()` - Update usage statistics
- `reset_daily_counts()` - Reset counters at midnight
- `mark_account_failed()` - Track failures and pause if needed
- `get_account_stats()` - Get account statistics

**Usage**:
```python
from account_rotation import get_least_used_account, increment_account_usage

# Get account for scraping
account = get_least_used_account(db)

# After scraping
increment_account_usage(db, account.id, reels_scraped=20, success=True)
```

#### [credit_system.py](Backend/credit_system.py)
Manages user credit quotas and consumption.

**Key Functions**:
- `check_user_credits()` - Validate if user has enough credits
- `deduct_credits()` - Consume credits after scraping
- `reset_all_daily_credits()` - Reset all users at midnight
- `get_user_credit_summary()` - Get credit info for user
- `update_user_credit_limit()` - Admin function to change limits

**Usage**:
```python
from credit_system import check_user_credits, deduct_credits

# Before scraping
if check_user_credits(db, user_id, required_credits=20):
    # Scrape reels
    deduct_credits(db, user_id, 20)
else:
    raise InsufficientCreditsError("Not enough credits")
```

### Database Migration

**Location**: `Backend/migrations/001_multi_user_system.sql`

**How to Run**:
```bash
# Option 1: Using psql
psql -U scraper_user -d instagram_scraper -f Backend/migrations/001_multi_user_system.sql

# Option 2: Using pgAdmin
# Open pgAdmin → Query Tool → Load and execute the SQL file
```

**What it does**:
1. Creates 4 new tables
2. Adds credit fields to users table
3. Adds Instagram account tracking to jobs and reels
4. Creates indexes for performance
5. Adds utility views for monitoring
6. Creates triggers for auto-updates
7. Inserts default admin user (username: admin, password: admin123)

### Testing Phase 1

**Test Script**: `Backend/test_phase1.py`

**Run Tests**:
```bash
cd Backend
python test_phase1.py
```

**Tests Include**:
1. Database connection
2. Table existence (all 8 tables)
3. New columns in modified tables
4. Instagram account CRUD operations
5. Account rotation logic
6. Credit system functionality
7. Activity logging
8. API key management
9. Admin user management

**Expected Output**:
```
╔════════════════════════════════════════════════════════╗
║               PHASE 1 TEST SUITE                       ║
╚════════════════════════════════════════════════════════╝

TEST 1: Database Connection
✓ Database connection successful

TEST 2: Table Existence
✓ Table 'users' exists
✓ Table 'instagram_accounts' exists
...

TEST SUMMARY
Tests Passed: 9/9 (100.0%)
✓ All tests PASSED! Phase 1 implementation is working correctly.
```

### Setup Instructions

#### Step 1: Install New Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

New dependency: `APScheduler==3.10.4` (for daily resets)

#### Step 2: Run Database Migration
```bash
psql -U scraper_user -d instagram_scraper -f migrations/001_multi_user_system.sql
```

#### Step 3: Verify Migration
```bash
python test_phase1.py
```

#### Step 4: Add Instagram Accounts to Pool
```python
# Using Python shell
from database import SessionLocal
from crud import create_instagram_account

db = SessionLocal()

# Add your Instagram accounts
account1 = create_instagram_account(
    db=db,
    username="insta_account_1",
    email="account1@gmail.com",
    password="your_password_here"
)

account2 = create_instagram_account(
    db=db,
    username="insta_account_2",
    email="account2@gmail.com",
    password="your_password_here"
)

db.close()
```

#### Step 5: Update Existing Users (Optional)
All existing users automatically get:
- `daily_credit_limit` = 2000
- `credits_used_today` = 0
- `last_credit_reset_date` = current date

No manual updates needed!

### How It Works

#### Scraping Flow with Account Rotation

1. **User makes scrape request** (e.g., 20 reels)
2. **System checks credits**: Does user have 20 credits available?
   - ✅ Yes → Continue
   - ❌ No → Return "Insufficient credits" error
3. **System selects Instagram account**: Get least-used active account from pool
4. **Scraping job created**: Links user, Instagram account, and job
5. **Reels scraped**: Using selected Instagram account's cookies
6. **Credits deducted**: 1 credit per successfully scraped reel
7. **Usage updated**: Instagram account's daily_scrape_count incremented
8. **Activity logged**: Event stored in activity_logs table

#### Account Selection Algorithm

```
SELECT * FROM instagram_accounts
WHERE is_active = TRUE AND is_paused = FALSE
ORDER BY daily_scrape_count ASC, last_used_at ASC NULLS FIRST
LIMIT 1
```

This ensures:
- Only active, non-paused accounts are used
- Least-used account selected first
- Accounts never used get priority

#### Credit Reset (Midnight Job)

- Runs daily at 00:00 server time
- Resets `credits_used_today` = 0 for all users
- Resets `daily_scrape_count` = 0 for all Instagram accounts
- Updates `last_reset_date` to current date
- Logged in activity_logs

### Configuration

#### Modify User Credit Limits
```python
from credit_system import update_user_credit_limit

# Give user 5000 credits per day
update_user_credit_limit(db, user_id=1, new_limit=5000)
```

#### Pause/Resume Instagram Accounts
```python
from account_rotation import pause_account, resume_account

# Temporarily disable an account
pause_account(db, account_id=1)

# Re-enable it
resume_account(db, account_id=1)
```

### Monitoring & Analytics

#### View Instagram Account Stats
```python
from account_rotation import get_all_account_stats

stats = get_all_account_stats(db)
for account in stats:
    print(f"{account['username']}: {account['daily_scrape_count']} scrapes today")
    print(f"  Success rate: {account['success_rate']}%")
    print(f"  Cookie health: {account['cookie_health']}")
```

#### View User Credit Usage
```python
from credit_system import get_user_credit_summary

summary = get_user_credit_summary(db, user_id=1)
print(f"Credits: {summary['remaining']}/{summary['daily_limit']}")
print(f"Usage: {summary['usage_percent']}%")
```

#### View Activity Logs
```python
from crud import get_activity_logs

# Get recent scrape successes
logs = get_activity_logs(db, event_type="scrape_success", limit=10)

# Get logs for specific user
user_logs = get_activity_logs(db, user_id=1, limit=20)
```

---

## 🚀 Phase 2: Enhanced API & Cookie Management (NEW)

**Status**: ✅ Implemented
**Date**: December 2025

### Overview

Phase 2 enhances the scraping system with automatic account rotation, credit validation, cookie update API endpoints, and a remote cookie updater script for automated cookie management.

### New Features

#### 1. Enhanced Scraping Endpoint
- **Automatic Credit Validation**: Checks user credits before starting job
- **Automatic Account Rotation**: Selects least-used Instagram account
- **Comprehensive Logging**: All scraping events logged to activity_logs
- **Better Error Handling**: Specific error codes for different failure types

#### 2. Cookie Update API Endpoints
- **Individual Cookie Updates**: Update cookies for specific Instagram accounts
- **Bulk Cookie Updates**: Update multiple accounts at once
- **API Key Authentication**: Secure endpoints with hashed API keys
- **Account Listing**: View all Instagram accounts in pool

#### 3. Remote Cookie Updater Script
- **Automated Cookie Extraction**: Uses Playwright to log in and extract cookies
- **Server Integration**: Automatically uploads cookies to server via API
- **Multi-Account Support**: Processes multiple Instagram accounts sequentially
- **Error Handling**: Robust error handling with detailed logging
- **Windows Task Scheduler Ready**: Designed to run as scheduled task

#### 4. Daily Reset Scheduler
- **Automatic Resets**: Runs daily at midnight
- **User Credits**: Resets all users' daily credits to 0
- **Account Counters**: Resets Instagram accounts' daily scrape counts
- **Activity Logging**: Logs reset events for monitoring

#### 5. API Key Management
- **Secure Generation**: Cryptographically secure random keys
- **Hashed Storage**: Keys stored as bcrypt hashes
- **Usage Tracking**: Last used timestamp tracked
- **Revocation Support**: Deactivate keys without deletion

### API Documentation (Phase 2)

#### Enhanced POST `/api/scrape`
Improved scraping endpoint with automatic rotation and credit validation.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "usernames": ["username1", "username2"],
  "reel_count": 20,
  "group_id": null  // Optional
}
```

**Success Response** (200):
```json
{
  "job_id": "job_20251218_143022_123456",
  "status": "started",
  "message": "Scraping job started using Instagram account insta_account_1. Use /api/job/{job_id} to check status"
}
```

**Error Responses**:
- **403 Forbidden** - Insufficient credits
  ```json
  {
    "detail": "Insufficient credits. Remaining: 50, Required: 100"
  }
  ```

- **503 Service Unavailable** - No Instagram accounts available
  ```json
  {
    "detail": "All Instagram accounts are exhausted. Try again later."
  }
  ```

#### POST `/api/admin/instagram-accounts/{account_id}/cookies`
Update cookies for a specific Instagram account.

**Authentication**: API Key (X-API-Key header)

**Headers**:
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body**:
```json
{
  "sessionid": "abc123...",
  "csrftoken": "xyz789...",
  "ds_user_id": "12345678",
  "ig_did": "ABCD-1234...",
  "mid": "Y1Z2X3...",
  "datr": "pqr456...",
  "rur": "ATN",
  "wd": "1920x1080",
  "ig_nrcb": "1"
}
```

**Success Response** (200):
```json
{
  "status": "success",
  "message": "Cookies updated for account insta_account_1",
  "account_id": 1,
  "account_username": "insta_account_1",
  "updated_at": "2025-12-18T14:30:22.123456"
}
```

**Error Responses**:
- **401 Unauthorized** - Invalid API key
- **404 Not Found** - Instagram account doesn't exist
- **400 Bad Request** - Empty cookies

#### POST `/api/admin/instagram-accounts/bulk-update-cookies`
Update cookies for multiple Instagram accounts at once.

**Authentication**: API Key (X-API-Key header)

**Request Body**:
```json
[
  {
    "account_id": 1,
    "cookies": {
      "sessionid": "abc123...",
      "csrftoken": "xyz789..."
    }
  },
  {
    "account_id": 2,
    "cookies": {
      "sessionid": "def456...",
      "csrftoken": "uvw012..."
    }
  }
]
```

**Success Response** (200):
```json
{
  "status": "completed",
  "successful_updates": 2,
  "failed_updates": 0,
  "results": [
    {
      "account_id": 1,
      "account_username": "insta_account_1",
      "status": "success"
    },
    {
      "account_id": 2,
      "account_username": "insta_account_2",
      "status": "success"
    }
  ],
  "errors": []
}
```

#### GET `/api/admin/instagram-accounts`
List all Instagram accounts in the pool.

**Authentication**: API Key (X-API-Key header)

**Success Response** (200):
```json
{
  "status": "success",
  "count": 3,
  "accounts": [
    {
      "id": 1,
      "username": "insta_account_1",
      "email": "account1@gmail.com",
      "is_active": true,
      "is_paused": false,
      "daily_scrape_count": 150,
      "total_scrapes": 2500,
      "success_count": 2450,
      "failure_count": 50,
      "cookies_updated_at": "2025-12-18T14:30:22.123456",
      "last_used_at": "2025-12-18T15:00:00.000000"
    }
  ]
}
```

### New Backend Modules (Phase 2)

#### [scheduler.py](Backend/scheduler.py)
Background scheduler for daily reset jobs.

**Key Functions**:
- `start_scheduler()` - Initialize and start the scheduler
- `stop_scheduler()` - Gracefully stop the scheduler
- `daily_reset_job()` - Async function that runs at midnight
- `run_manual_reset()` - Manually trigger reset for testing
- `get_scheduler_status()` - Check scheduler status and next run time

**Automatic Startup**:
The scheduler automatically starts when the FastAPI app starts and stops on shutdown.

**Manual Testing**:
```bash
cd Backend
python scheduler.py
```

**Expected Output**:
```
============================================================
Daily Reset Scheduler - Manual Test
============================================================
Starting daily reset job at 2025-12-18 23:59:59
============================================================
Resetting user credits...
[OK] Reset credits for 15 user(s)
Resetting Instagram account daily counts...
[OK] Reset daily counts for 3 Instagram account(s)
[OK] Daily reset completed successfully at 2025-12-18 00:00:05
============================================================
```

#### [generate_api_key.py](Backend/generate_api_key.py)
Utility for managing API keys.

**Commands**:

**Create New API Key**:
```bash
python generate_api_key.py create "Cookie Updater - Windows PC"
```

**Output**:
```
======================================================================
API KEY GENERATED SUCCESSFULLY
======================================================================
Key Name: Cookie Updater - Windows PC
Key ID: 1
Created At: 2025-12-18 14:30:22.123456

IMPORTANT: Save this API key securely. It will not be shown again!
----------------------------------------------------------------------
API Key: xYz123AbC456DeF789GhI012JkL345MnO678PqR901StU234VwX567
----------------------------------------------------------------------

Use this key in the 'X-API-Key' header when calling admin endpoints.
======================================================================
```

**List All API Keys**:
```bash
python generate_api_key.py list
```

**Revoke an API Key**:
```bash
python generate_api_key.py revoke 1
```

#### [remote_cookie_updater.py](Backend/Scripts/remote_cookie_updater.py)
Automated cookie extraction and server update script.

**Setup**:

1. Install Playwright:
   ```bash
   pip install playwright
   playwright install firefox
   ```

2. Configure the script:
   Edit `remote_cookie_updater.py` and update:
   ```python
   SERVER_URL = "https://your-server.com"  # Your server URL
   API_KEY = "your-api-key-here"  # From generate_api_key.py

   INSTAGRAM_ACCOUNTS = [
       {
           "id": 2,  # Database ID from instagram_accounts table
           "email": "account1@gmail.com",
           "password": "your_password"
       },
       {
           "id": 3,
           "email": "account2@gmail.com",
           "password": "your_password"
       }
   ]
   ```

3. Test server connection:
   ```bash
   python remote_cookie_updater.py test
   ```

4. Run manually:
   ```bash
   python remote_cookie_updater.py
   ```

**Expected Output**:
```
======================================================================
INSTAGRAM COOKIE UPDATER
======================================================================
Server: https://your-server.com
Accounts to update: 2
Started at: 2025-12-18 14:30:22
======================================================================

[1/2] Processing Account ID: 2
Email: account1@gmail.com
----------------------------------------------------------------------
  [1/4] Launching browser...
  [2/4] Navigating to Instagram login...
  [3/4] Logging in...
  [3/4] Login successful!
  [4/4] Extracting cookies...
  [OK] Extracted 9 essential cookies
  [UPLOAD] Sending cookies to server...
  [OK] Server updated successfully!
       Account: insta_account_1
       Updated at: 2025-12-18T14:32:15.123456

  [WAIT] Waiting 15 seconds before next account...

[2/2] Processing Account ID: 3
...

======================================================================
COOKIE UPDATE SUMMARY
======================================================================
Total Accounts: 2
Successful:     2
Failed:         0
Completed at:   2025-12-18 14:35:30
======================================================================
[SUCCESS] All accounts updated successfully!
```

**Windows Task Scheduler Setup**:

1. Open Task Scheduler
2. Create Basic Task:
   - Name: "Instagram Cookie Update"
   - Trigger: Repeat every 5 days
   - Time: 2:00 AM (low traffic time)
3. Action: Start a program
   - Program: `C:\Python\python.exe`
   - Arguments: `C:\path\to\remote_cookie_updater.py`
   - Start in: `C:\path\to\Backend\Scripts\`
4. Settings:
   - Allow task to run on demand
   - Stop if runs longer than 1 hour
   - Run whether user is logged on or not

### Testing Phase 2

**Test Script**: `Backend/test_phase2.py`

**Run Tests**:
```bash
cd Backend
python test_phase2.py
```

**Tests Include**:
1. Account Rotation Logic - Verify least-used selection
2. Credit System - Validation, deduction, and reset
3. API Key Management - Creation and retrieval
4. Activity Logging - Log creation and verification
5. Instagram Account Management - Cookie updates
6. Daily Reset Functions - User and account resets
7. Job-Account Linkage - Verify job creation with Instagram account

**Expected Output**:
```
============================================================
PHASE 2 TESTING - ENHANCED FEATURES
============================================================
Started at: 2025-12-18 14:30:22
============================================================

============================================================
TEST: Account Rotation System
============================================================
[OK] Selected account: insta_account_1 (ID: 2)
     Daily count: 0
     Total scrapes: 0
[OK] Usage incremented correctly: 0 -> 5

============================================================
TEST: Credit System
============================================================
Testing with user: user@example.com (ID: 1)
Current credits: 0/2000
[OK] Credit validation passed. Remaining: 2000
[OK] Credits deducted correctly: 0 -> 10
[OK] Correctly rejected excessive request: Insufficient credits...
[OK] Credits reset successfully to 0

...

============================================================
TEST SUMMARY
============================================================
[OK] Account Rotation Logic
[OK] Credit System
[OK] API Key Management
[OK] Activity Logging
[OK] Instagram Account Management
[OK] Daily Reset Functions
[OK] Job-Account Linkage
============================================================
Tests Passed: 7/7 (100.0%)
[OK] All tests PASSED!
============================================================
```

### Setup Instructions (Phase 2)

Phase 2 builds on Phase 1, so ensure Phase 1 is completed first.

#### Step 1: Verify Phase 1
```bash
cd Backend
python test_phase1.py
```

All Phase 1 tests should pass.

#### Step 2: No New Dependencies
Phase 2 uses the same dependencies from Phase 1. No additional installations needed.

#### Step 3: Generate API Key
```bash
python generate_api_key.py create "Cookie Updater - Main"
```

Save the API key securely - you'll need it for the remote cookie updater.

#### Step 4: Test Enhanced Scraping Endpoint

The scraping endpoint now automatically validates credits and selects Instagram accounts. No code changes needed in your frontend!

**Before Phase 2**:
- Manual cookie management
- No credit validation
- No account rotation

**After Phase 2**:
- Automatic credit check before scraping
- Automatic selection of least-used Instagram account
- Comprehensive activity logging
- Cookies can be updated remotely via API

#### Step 5: Set Up Remote Cookie Updater (Optional)

Only needed if you want automated cookie updates every 5 days.

1. Install Playwright on Windows PC:
   ```bash
   pip install playwright
   playwright install firefox
   ```

2. Configure `remote_cookie_updater.py` with your server URL and API key

3. Test connection:
   ```bash
   python remote_cookie_updater.py test
   ```

4. Run manually once to verify:
   ```bash
   python remote_cookie_updater.py
   ```

5. Set up Windows Task Scheduler (see instructions above)

### How It Works (Phase 2)

#### Enhanced Scraping Flow

```
User requests scrape
  ↓
System validates user credits
  ├─ Insufficient credits → Return 403 error
  └─ Credits OK → Continue
      ↓
System selects least-used Instagram account
  ├─ No accounts available → Return 503 error
  └─ Account selected → Continue
      ↓
Job created with user + Instagram account linkage
      ↓
Background task starts scraping
      ↓
For each successfully scraped reel:
  - Deduct 1 credit from user
  - Save reel to database with instagram_account_id
      ↓
After job completes:
  - Update Instagram account usage counters
  - Log activity (success/failure)
      ↓
Return job status to user
```

#### Cookie Update Flow

```
Windows PC (runs every 5 days)
  ↓
Playwright launches browser
  ↓
Logs into each Instagram account
  ↓
Extracts essential cookies
  ↓
Sends cookies to server via API
  ├─ Authentication: X-API-Key header
  ├─ Endpoint: POST /api/admin/instagram-accounts/{id}/cookies
  └─ Server validates API key
      ↓
Server updates instagram_accounts table
  - Stores cookies as JSONB
  - Updates cookie_string for headers
  - Extracts and stores CSRF token
  - Sets cookies_updated_at timestamp
      ↓
Activity logged
      ↓
Instagram account ready for scraping
```

#### Daily Reset Flow

```
Scheduler (runs at 00:00 daily)
  ↓
Reset all users:
  - credits_used_today = 0
  - last_credit_reset_date = today
      ↓
Reset all Instagram accounts:
  - daily_scrape_count = 0
  - last_reset_date = today
      ↓
Log reset event in activity_logs
      ↓
System ready for new day
```

### Configuration (Phase 2)

#### Change Daily Reset Time

Edit `Backend/scheduler.py`:
```python
scheduler.add_job(
    daily_reset_job,
    trigger=CronTrigger(hour=2, minute=30),  # 2:30 AM instead of midnight
    id='daily_reset',
    name='Daily Credit and Usage Counter Reset',
    replace_existing=True
)
```

#### Change Cookie Update Frequency

Edit Windows Task Scheduler trigger:
- Every 3 days: More cookie refreshes, more automation overhead
- Every 7 days: Less frequent updates, cookies may expire sooner
- Recommended: 5 days (balanced)

#### Modify Essential Cookies List

Edit `Backend/Scripts/remote_cookie_updater.py`:
```python
ESSENTIAL_COOKIES = [
    'sessionid',     # Required - user session
    'csrftoken',     # Required - CSRF protection
    'ds_user_id',    # Required - user ID
    'ig_did',        # Required - device ID
    'mid',           # Recommended
    'datr',          # Recommended
    'rur',           # Optional - routing
    'wd',            # Optional - window dimensions
    'ig_nrcb'        # Optional - non-robot callback
]
```

### Monitoring (Phase 2)

#### Check Scheduler Status
```python
from scheduler import get_scheduler_status

status = get_scheduler_status()
print(f"Scheduler: {status['status']}")
for job in status['jobs']:
    print(f"  Next run: {job['next_run']}")
```

#### View Recent Cookie Updates
```python
from crud import get_activity_logs

logs = get_activity_logs(db, event_type="cookies_updated", limit=10)
for log in logs:
    print(f"Account {log.instagram_account_id} updated at {log.created_at}")
    print(f"  By API key: {log.details['updated_by_api_key']}")
```

#### Check Instagram Account Cookie Health
```python
from datetime import datetime, timedelta

accounts = get_all_instagram_accounts(db)
for account in accounts:
    if account.cookies_updated_at:
        age = datetime.now() - account.cookies_updated_at
        if age > timedelta(days=7):
            print(f"[WARNING] {account.username} cookies are {age.days} days old")
        else:
            print(f"[OK] {account.username} cookies updated {age.days} days ago")
    else:
        print(f"[ERROR] {account.username} has no cookies!")
```

### Troubleshooting Phase 2

#### Scheduler not running
Check startup logs:
```
[OK] Database initialized successfully
[OK] Daily reset scheduler started
```

If missing, check `Backend/app.py` startup event.

#### Cookie update fails with 401
- API key invalid or revoked
- Check API key exists: `python generate_api_key.py list`
- Generate new key: `python generate_api_key.py create "New Key"`

#### Remote script can't connect to server
- Check `SERVER_URL` in `remote_cookie_updater.py`
- Test server accessibility: `curl http://your-server.com/health`
- Check firewall rules
- Verify server is running

#### Playwright login fails
- Instagram detected automation (use `headless=False` to debug)
- Password incorrect
- Account requires 2FA (not supported yet)
- Instagram changed login flow (update selectors)

#### Credits not being deducted
Check if scraping succeeded:
```python
# Credits only deducted for successfully scraped reels
# Check job results
job = get_job_by_id(db, job_id)
print(f"Status: {job.status}")
print(f"Credits consumed: {job.credits_consumed}")
```

#### Account rotation not working
All accounts paused or inactive:
```python
accounts = get_all_instagram_accounts(db)
active = [a for a in accounts if a.is_active and not a.is_paused]
print(f"Active accounts: {len(active)}")
```

#### Scraping fails - No reels scraped
**Symptom**: Scraping job starts but returns 0 reels, no errors in logs

**Cause**: Instagram account has invalid/test cookies

**Diagnosis**:
```python
from database import SessionLocal
from crud import get_all_instagram_accounts

db = SessionLocal()
accounts = get_all_instagram_accounts(db)

for account in accounts:
    cookie_len = len(account.cookie_string) if account.cookie_string else 0
    print(f"ID: {account.id}, Username: {account.username}")
    print(f"  Cookie length: {cookie_len}")
    print(f"  Active: {account.is_active}, Paused: {account.is_paused}")

    # Check if cookies look valid (should be >300 chars for real cookies)
    if cookie_len < 100:
        print(f"  ⚠️ WARNING: Cookies appear invalid (too short)")

db.close()
```

**Solution**:
1. **Option 1** - Pause accounts with invalid cookies:
   ```python
   from account_rotation import pause_account
   pause_account(db, account_id=1)  # Replace with actual account ID
   ```

2. **Option 2** - Update cookies using remote_cookie_updater:
   ```bash
   # Configure the account in remote_cookie_updater.py
   # Then run it to extract fresh cookies
   python Backend/Scripts/remote_cookie_updater.py
   ```

3. **Option 3** - Manually update via API:
   ```python
   import requests

   cookies = {
       "sessionid": "valid_session_id_here",
       "csrftoken": "valid_csrf_token_here",
       # ... other cookies
   }

   response = requests.post(
       "http://localhost:8080/api/admin/instagram-accounts/1/cookies",
       headers={"X-API-Key": "your-api-key"},
       json=cookies
   )
   print(response.json())
   ```

**Prevention**: Always verify new Instagram accounts have valid cookies before activating them. Test cookies are for development only!

---

## 🚀 Phase 3: Admin Panel & Advanced Features (NEW)

**Status**: ✅ Implemented
**Date**: December 18, 2025

### Overview

Phase 3 adds a comprehensive admin panel with web-based user management, Instagram account monitoring, activity logs viewer, system statistics dashboard, and real-time notifications.

### New Features

#### 1. Admin Panel Web UI
- **Modern Dark Theme**: Matches existing design language (black/purple/white)
- **Responsive Layout**: Works on desktop and mobile devices
- **Sidebar Navigation**: Easy access to all admin features
- **Real-time Updates**: Notification system for live events

#### 2. User Management Interface
- **User List**: View all users with credit usage and status
- **Search & Filter**: Find users by email/username, filter by status
- **Edit Users**: Modify credit limits and activate/deactivate accounts
- **User Details**: View detailed statistics and recent jobs
- **Usage Tracking**: Visual progress bars for credit consumption

#### 3. Instagram Account Management
- **Account Pool Monitoring**: View all Instagram accounts
- **Cookie Health Status**: Visual indicators for cookie freshness
- **Usage Statistics**: Daily and lifetime scrape counts
- **Success Rates**: Track account performance
- **Filter by Status**: Active, paused, healthy cookies, expired cookies

#### 4. Activity Logs Viewer
- **Comprehensive Logging**: All system events in one place
- **Advanced Filtering**: By date range, event type, user, account
- **Export to CSV**: Download logs for external analysis
- **Real-time Updates**: See events as they happen

#### 5. System Statistics Dashboard
- **Overview Cards**: Total users, accounts, today's reels, success rate
- **Daily Trends Chart**: Reels scraped and active users over time
- **Credit Usage Chart**: Top consumers visualization
- **Account Distribution**: Pie chart of account usage
- **Hourly Patterns**: Identify peak usage times
- **Success/Failure Rates**: Donut chart visualization

#### 6. Performance Optimizations
- **Database Indexes**: Faster queries on activity_logs, scraped_reels, scraping_jobs
- **Database Views**: Precomputed statistics for quick access
- **Efficient Queries**: Optimized SQL for large datasets

### Admin Panel Structure

```
Frontend/admin/
├── index.html           # Main admin dashboard page
├── admin.css            # Admin panel styles (dark theme)
├── admin.js             # Main controller and navigation
├── components/
│   ├── users.js         # User management component
│   ├── accounts.js      # Instagram account management
│   ├── logs.js          # Activity logs viewer
│   └── stats.js         # Statistics dashboard
└── utils/
    ├── api.js           # API client for backend communication
    └── charts.js        # Chart.js helper utilities
```

### Setup Instructions (Phase 3)

#### Step 1: Run Database Migration

The migration adds performance indexes and useful database views:

**Option 1: Using Python script**
```bash
cd Backend
python run_migration.py migrations/002_phase3_indexes_views.sql
```

**Option 2: Using psql directly**
```bash
psql -U scraper_user -d instagram_scraper -f Backend/migrations/002_phase3_indexes_views.sql
```

This creates:
- 10 indexes for faster queries
- 6 database views for complex statistics
- Performance optimizations for large datasets

#### Step 2: Create Admin User

Admin users are separate from regular users and have special permissions:

```python
from database import SessionLocal
from models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Create admin user
admin = AdminUser(
    username="admin",
    email="admin@example.com",
    password_hash=pwd_context.hash("your_secure_password"),
    is_active=True
)
db.add(admin)
db.commit()
db.close()
```

**Default Admin** (from Phase 1 migration):
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`
- ⚠️ **Change this password immediately for production!**

#### Step 3: Access Admin Panel

1. Start the server:
   ```bash
   cd Backend
   python app.py
   ```

2. Navigate to admin panel:
   ```
   http://localhost:8080/static/admin/index.html
   ```

3. Login with admin credentials

### Admin Panel Pages

#### Dashboard Page

**Overview Cards:**
- Total Users (active/inactive count)
- Instagram Accounts (active/paused count)
- Today's Reels (jobs completed count)
- Success Rate (percentage with total jobs)

**Charts:**
- Daily Scraping Trends (line chart, last 7/14/30 days)
- Top Credit Consumers (bar chart)

**Recent Activity:**
- Last 10 system events with icons and timestamps

#### User Management Page

**Features:**
- Search users by email/username
- Filter by status (all/active/inactive)
- View user details (jobs, reels, success rate)
- Edit credit limits
- Activate/deactivate users

**User Table Columns:**
- Email, Username
- Credits (used/limit with progress bar)
- Usage percentage
- Status badge
- Created date
- Actions (Edit, Details)

#### Instagram Accounts Page

**Features:**
- Filter by status (all/active/paused/healthy/expired)
- Cookie health monitoring
- Usage statistics per account
- Success rate tracking

**Account Table Columns:**
- Username, Email
- Status (active/paused/inactive badge)
- Cookie Health (healthy/expiring/expired with age)
- Daily Usage count
- Total Scrapes count
- Success Rate (with progress bar)
- Last Used timestamp

#### Activity Logs Page

**Features:**
- Date range filter (start/end date pickers)
- Event type filter (scrape_started, scrape_success, scrape_failed, etc.)
- Export logs to CSV
- Detailed log information

**Log Table Columns:**
- Timestamp
- Event Type (with colored badge)
- User ID
- Instagram Account ID
- Job ID
- Details (JSON formatted)

#### Statistics Page

**Advanced Charts:**
- Account Usage Distribution (pie chart)
- Hourly Usage Pattern (bar chart showing peak hours)
- Success vs Failure Rates (donut chart)

**Time Range Filter:**
- Last 7/14/30/90 days

### Database Views Added

#### `v_daily_stats`
Aggregates daily scraping metrics:
- Date, total reels, active users, accounts used
- Average plays, likes, comments

#### `v_user_summary`
User statistics with credit usage:
- User info, credit limits, usage percent
- Total jobs, successful jobs, total reels scraped

#### `v_instagram_account_health`
Account status and cookie health:
- Account info, status flags
- Success rate calculation
- Cookie health status (HEALTHY/EXPIRING_SOON/EXPIRED/NO_COOKIES)
- Cookie age in days

#### `v_recent_activity`
Recent system activity with joined details:
- Activity log with user/account usernames
- Job IDs and event details

#### `v_job_performance`
Job performance metrics:
- Job details with user and account info
- Duration in seconds
- Reels scraped and credits consumed

#### `v_hourly_usage_pattern`
Usage patterns by hour:
- Hour of day (0-23)
- Total reels, unique users, average plays

### API Endpoints (Phase 3)

All endpoints require admin authentication (`Authorization: Bearer <token>`)

#### Authentication
```
POST /api/admin/auth/login
GET  /api/admin/auth/me
```

#### User Management
```
GET    /api/admin/users                    # List users with filters
GET    /api/admin/users/{user_id}          # User details
PUT    /api/admin/users/{user_id}          # Update user
DELETE /api/admin/users/{user_id}          # Deactivate user
GET    /api/admin/users/{user_id}/stats    # User statistics
```

#### Activity Logs
```
GET /api/admin/logs              # List logs with filters
GET /api/admin/logs/stats        # Log statistics
```

#### System Statistics
```
GET /api/admin/stats/overview       # System overview
GET /api/admin/stats/usage          # Usage over time
GET /api/admin/stats/performance    # Performance metrics
```

### Configuration

#### Admin Panel Settings

No additional configuration needed! The admin panel uses the same authentication system as the main app.

#### Customize Chart Time Ranges

Edit `Frontend/admin/components/stats.js`:
```javascript
// Change default days for charts
currentDays: 7  // Change to 14, 30, etc.
```

#### Customize Notification Polling Interval

Edit `Frontend/admin/admin.js`:
```javascript
// Default: 30 seconds
setInterval(() => {
    this.loadNotifications();
}, 30000);  // Change to desired interval in milliseconds
```

### Using the Admin Panel

#### Managing Users

1. **View all users**: Navigate to "Users" page
2. **Search for user**: Type email/username in search box
3. **Edit credit limit**:
   - Click "Edit" button next to user
   - Modify "Daily Credit Limit" field
   - Click "Save Changes"
4. **Deactivate user**:
   - Click "Edit" button
   - Uncheck "Active" checkbox
   - Click "Save Changes"

#### Monitoring Instagram Accounts

1. **View account health**: Navigate to "Instagram Accounts" page
2. **Check cookie status**: Look at "Cookie Health" column
   - 🟢 Healthy (0-5 days old)
   - 🟡 Expiring (5-7 days old)
   - 🔴 Expired (>7 days old)
3. **Filter accounts**: Use status dropdown
   - Active: Only active, non-paused accounts
   - Paused: Only paused accounts
   - Healthy: Accounts with fresh cookies (0-5 days)
   - Expired: Accounts needing cookie refresh (>7 days)

#### Viewing Activity Logs

1. **Set date range**: Use start/end date pickers (default: last 7 days)
2. **Filter by event type**: Select from dropdown
3. **Export logs**: Click "Export CSV" button
4. **View details**: Hover over details column to see full JSON

#### Analyzing Statistics

1. **Dashboard overview**: View real-time metrics on Dashboard page
2. **Advanced statistics**: Navigate to "Statistics" page
3. **Change time range**: Use dropdown filter (7/14/30/90 days)
4. **Identify trends**: Look at daily trends chart
5. **Find top users**: Check credit usage bar chart
6. **Monitor success rate**: View donut chart

### Troubleshooting Phase 3

#### Admin panel won't load

**Symptom**: Blank page or "Failed to load profile" error

**Solutions**:
1. Check if backend is running: `python app.py`
2. Verify admin user exists in database
3. Check browser console for errors
4. Clear browser cache and localStorage

#### "Invalid or inactive API key" when accessing admin endpoints

**Cause**: Admin authentication not working

**Solutions**:
1. Login again at `/static/login.html`
2. Check if admin user exists in `admin_users` table
3. Verify token is being sent in Authorization header

#### Charts not displaying

**Symptom**: Empty chart areas

**Solutions**:
1. Check browser console for Chart.js errors
2. Verify Chart.js CDN is accessible: `https://cdn.jsdelivr.net/npm/chart.js`
3. Check if data endpoints are returning valid JSON
4. Inspect network tab for failed API calls

#### Database migration fails

**Error**: `column "created_at" does not exist`

**Solution**: Migration may have syntax issues. Run migrations manually:
```sql
-- Connect to database
psql -U scraper_user -d instagram_scraper

-- Create indexes manually
CREATE INDEX idx_activity_logs_event_type ON activity_logs(event_type);
CREATE INDEX idx_scraped_reels_scraped_at ON scraped_reels(scraped_at DESC);
-- ... etc
```

---

### Troubleshooting Phase 1

#### "Table already exists" errors
The migration uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times.

#### Credits not resetting
Check if the daily reset job is running. For now, manually reset:
```python
from credit_system import reset_all_daily_credits
reset_all_daily_credits(db)
```

#### No Instagram accounts available
Add Instagram accounts to the pool:
```python
create_instagram_account(db, username="...", email="...", password="...")
```

#### Account rotation not working
Check account status:
```python
accounts = get_all_instagram_accounts(db)
for acc in accounts:
    print(f"{acc.username}: active={acc.is_active}, paused={acc.is_paused}")
```

---

## 🤝 Contributing

When modifying the code:
1. Test thoroughly with various usernames
2. Handle edge cases (private accounts, deleted accounts, etc.)
3. Update this documentation for new features
4. Follow the existing code style

## 📄 License

This project is for educational purposes. Respect Instagram's Terms of Service and robots.txt when using this tool.

---

**Created with Claude Code** 🤖
