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

### Next Steps: Phase 2

Phase 2 will add:
- Admin panel web UI
- Cookie update API endpoints
- Remote cookie updater script
- Enhanced scraping endpoints with rotation
- Daily reset scheduler

**See**: [Implementation Plan](https://claude.com/plans/distributed-spinning-tarjan.md)

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
