# Instagram Reel Scraper - Complete Documentation

**Version:** 3.0.4 (IST Timezone & Date Format Fixes)
**Last Updated:** December 25, 2025
**Status:** Production Ready ✅

**Recent Updates (v3.0.4):**
- ✅ **CRITICAL FIX:** Daily reset now runs at IST midnight (Indian Standard Time)
- ✅ All dates now display in DD-MM-YYYY format (Indian standard)
- ✅ Timestamps show in 24-hour format (DD-MM-YYYY HH:MM:SS)
- ✅ Fixed timezone mismatch causing incorrect daily usage tracking
- ✅ Added manual reset command for immediate testing
- ✅ Consistent date formatting across entire application

**Previous Updates (v3.0.3):**
- ✅ Replaced all emoji icons with professional SVG graphics
- ✅ Removed empty logo circle above Admin Panel title
- ✅ Fixed notification panel visibility with proper styling
- ✅ Added color-coded SVG icons for all activity types
- ✅ Improved notification bell visibility (white icon)
- ✅ Enhanced sidebar navigation with proper icons
- ✅ Updated toast notifications with SVG icons
- ✅ Consistent design language matching user dashboard

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Phase 1: Multi-User System](#phase-1-multi-user-system)
- [Phase 2: Enhanced API & Cookie Management](#phase-2-enhanced-api--cookie-management)
- [Phase 3: Admin Panel](#phase-3-admin-panel)
- [API Documentation](#api-documentation)
- [User Dashboard Guide](#user-dashboard-guide)
- [Admin Panel Guide](#admin-panel-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Contributing](#contributing)
- [Changelog](#changelog)

---

## 🎯 Overview

Instagram Reel Scraper is a full-stack web application designed for scraping Instagram reel metadata with enterprise-grade features including multi-user support, credit-based usage limits, intelligent Instagram account rotation, and comprehensive admin controls.

### What It Does

- Scrapes Instagram reel metadata (plays, likes, comments, URLs)
- Manages multiple users with individual credit quotas
- Rotates Instagram accounts automatically for optimal performance
- Tracks usage statistics and generates analytics
- Provides admin dashboard for system monitoring

### Use Cases

- Social media analytics and research
- Content performance tracking
- Competitive analysis
- Educational data science projects

---

## ✨ Features

### User Features
- **JWT Authentication** - Secure login with 7-day token expiration
- **Group Management** - Organize Instagram usernames into reusable groups
- **Credit System** - Daily quota management (default: 2000 reels/day)
- **Job Tracking** - Real-time progress monitoring with history
- **Analytics Dashboard** - View and filter scraped data
- **Data Export** - Download data as CSV

### Admin Features
- **User Management** - View, edit, activate/deactivate users
- **Instagram Account Pool** - Monitor cookie health and usage
- **Activity Logs** - Comprehensive event logging with filters
- **System Statistics** - Charts and metrics for system health
- **Credit Control** - Adjust user limits dynamically

### Technical Features
- **Account Rotation** - Intelligent selection of least-used Instagram account
- **Cookie Management** - Automated cookie refresh every 5 days
- **Daily Resets** - Automatic credit and counter reset at midnight IST (Indian Standard Time)
- **IST Timezone Support** - Scheduler configured for Asia/Kolkata timezone
- **DD-MM-YYYY Date Format** - Indian standard date formatting throughout application
- **Rate Limiting** - Built-in protection against Instagram blocks
- **Database Views** - Optimized queries for analytics

---

## 🛠 Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.109.0 | Modern async Python web framework |
| **PostgreSQL** | 15+ | Relational database |
| **SQLAlchemy** | 2.0.36 | ORM for database operations |
| **Uvicorn** | 0.27.0 | ASGI server |
| **JWT** | python-jose 3.3.0 | Secure authentication |
| **Bcrypt** | passlib 1.7.4 | Password hashing |
| **Pandas** | 2.3.3 | Data manipulation |
| **APScheduler** | 3.10.4 | Daily reset automation |
| **Playwright** | Latest | Cookie extraction (optional) |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Vanilla JavaScript** | No framework dependencies |
| **HTML5/CSS3** | Modern responsive design |
| **Fetch API** | Backend communication |
| **Chart.js** | Admin panel visualizations |

### Database
- **PostgreSQL 15+** - ACID compliance, JSONB support
- **8 Tables** - Normalized schema with foreign keys
- **9 Views** - Precomputed statistics
- **Indexes** - Optimized for analytics queries

---

## 🚀 Quick Start

Get up and running in 10 minutes!

### Prerequisites
- Python 3.8+
- Docker Desktop (for PostgreSQL)

### Steps

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Navigate to Backend
cd Backend

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.example .env

# 5. Generate secret key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env

# 6. Run Phase 1 migration
psql -U scraper_user -d instagram_scraper -f migrations/001_multi_user_system.sql

# 7. Run Phase 3 migration
psql -U scraper_user -d instagram_scraper -f migrations/002_phase3_indexes_views.sql

# 8. Start the server
python app.py

# 9. Open browser
# Navigate to: http://localhost:8080
```

### First Use

1. Click **"Sign Up"**
2. Create account (email, username, password)
3. Login with credentials
4. Start scraping!

---

## 📦 Installation

### Detailed Installation Steps

#### 1. Clone Repository

```bash
git clone <your-repository-url>
cd Instagram_reel_scrapper
```

#### 2. Set Up PostgreSQL

**Option A: Docker Compose (Recommended)**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: instagram_scraper_db
    environment:
      POSTGRES_USER: scraper_user
      POSTGRES_PASSWORD: scraper_password_123
      POSTGRES_DB: instagram_scraper
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

Start database:

```bash
docker-compose up -d
```

**Option B: Docker CLI**

```bash
docker run -d \
  --name instagram_scraper_db \
  -e POSTGRES_USER=scraper_user \
  -e POSTGRES_PASSWORD=scraper_password_123 \
  -e POSTGRES_DB=instagram_scraper \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

#### 3. Install Python Dependencies

```bash
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy template
cp .env.example .env
```

Edit `.env`:

```env
# Database
DATABASE_URL=postgresql://scraper_user:scraper_password_123@localhost:5432/instagram_scraper

# JWT (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Settings
MAX_GROUPS_PER_USER=100
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

#### 5. Run Database Migrations

```bash
# Phase 1: Multi-user system
psql -U scraper_user -d instagram_scraper -f migrations/001_multi_user_system.sql

# Phase 3: Indexes and views
psql -U scraper_user -d instagram_scraper -f migrations/002_phase3_indexes_views.sql
```

#### 6. Verify Installation

```bash
cd Backend
python test_phase1.py
python test_phase2.py
```

All tests should pass ✅

#### 7. Start Application

```bash
python app.py
```

Access at: http://localhost:8080

---

## 📁 Project Structure

```
Instagram_reel_scrapper/
├── Backend/
│   ├── Scripts/
│   │   ├── pipeline.py                  # Core scraping logic
│   │   └── remote_cookie_updater.py     # Automated cookie refresh
│   ├── migrations/
│   │   ├── 001_multi_user_system.sql    # Phase 1 database setup
│   │   └── 002_phase3_indexes_views.sql # Phase 3 optimizations
│   ├── app.py                            # FastAPI application
│   ├── auth.py                           # JWT authentication
│   ├── config.py                         # Configuration management
│   ├── database.py                       # Database connection
│   ├── models.py                         # SQLAlchemy models
│   ├── schemas.py                        # Pydantic validation
│   ├── crud.py                           # Database operations
│   ├── account_rotation.py               # Instagram account selection
│   ├── credit_system.py                  # User credit management
│   ├── scheduler.py                      # Daily reset automation
│   ├── generate_api_key.py               # API key management utility
│   ├── test_phase1.py                    # Phase 1 tests
│   ├── test_phase2.py                    # Phase 2 tests
│   ├── requirements.txt                  # Python dependencies
│   ├── .env                              # Environment variables (create this)
│   ├── .env.example                      # Environment template
│   └── output_json/                      # Scraped data (generated)
│
├── Frontend/
│   ├── index.html                        # User dashboard
│   ├── login.html                        # Login/signup page
│   ├── script.js                         # Main application logic
│   ├── auth.js                           # Authentication handler
│   ├── groups.js                         # Group management
│   ├── analytics.js                      # Analytics dashboard
│   ├── styles.css                        # User dashboard styles
│   └── admin/
│       ├── index.html                    # Admin panel main page
│       ├── login.html                    # Admin login page
│       ├── admin.css                     # Admin panel styles
│       ├── admin.js                      # Admin controller
│       ├── components/
│       │   ├── users.js                  # User management component
│       │   ├── accounts.js               # Instagram account management
│       │   ├── logs.js                   # Activity logs viewer
│       │   └── stats.js                  # Statistics dashboard
│       └── utils/
│           ├── api.js                    # API client
│           └── charts.js                 # Chart.js utilities
│
├── docker-compose.yml                    # PostgreSQL setup (create this)
├── .gitignore                            # Git ignore rules
└── DOCUMENTATION.md                      # This file
```

---

## 🗄 Database Schema

**Total Tables:** 8
**Total Views:** 9

### Table: users

**Purpose:** Store user accounts with credit system

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| email | varchar(255) | NO | - | User email (unique) |
| username | varchar(100) | NO | - | Display name (unique) |
| password_hash | varchar(255) | NO | - | Bcrypt hashed password |
| is_active | boolean | NO | - | Account status |
| created_at | timestamp | NO | now() | Account creation time |
| daily_credit_limit | integer | YES | 2000 | Max reels per day |
| credits_used_today | integer | YES | 0 | Credits consumed today |
| last_credit_reset_date | date | YES | CURRENT_DATE | Last reset date |

**Primary Key:** id
**Unique Constraints:** email, username

---

### Table: instagram_accounts

**Purpose:** Pool of Instagram accounts for scraping with cookie management

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| username | varchar(100) | NO | - | Instagram username |
| email | varchar(255) | NO | - | Instagram email |
| password | varchar(255) | NO | - | Instagram password |
| cookies | jsonb | YES | - | Full cookie object |
| cookie_string | text | YES | - | Formatted cookie header |
| x_csrf_token | varchar(255) | YES | - | Extracted CSRF token |
| is_active | boolean | YES | true | Account enabled |
| is_paused | boolean | YES | false | Temporarily disabled |
| daily_scrape_count | integer | YES | 0 | Reels scraped today |
| last_reset_date | date | YES | CURRENT_DATE | Last counter reset |
| total_scrapes | integer | YES | 0 | Lifetime scrapes |
| success_count | integer | YES | 0 | Successful scrapes |
| failure_count | integer | YES | 0 | Failed scrapes |
| last_used_at | timestamp | YES | - | Last usage time |
| cookies_updated_at | timestamp | YES | - | Last cookie refresh |
| created_at | timestamp | YES | now() | Account added |
| updated_at | timestamp | YES | now() | Last modification |

**Primary Key:** id
**Unique Constraints:** username, email

---

### Table: scraping_jobs

**Purpose:** Track all scraping jobs with progress and status

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| job_id | varchar(100) | NO | - | Unique job identifier |
| user_id | integer | NO | - | FK to users |
| usernames | ARRAY | NO | - | Target Instagram usernames |
| reel_count | integer | NO | - | Reels requested per user |
| status | varchar(50) | NO | - | running/completed/failed |
| progress | float | NO | - | Percentage (0-100) |
| start_time | timestamp | NO | now() | Job start time |
| end_time | timestamp | YES | - | Job end time |
| duration | float | YES | - | Execution time (seconds) |
| error_message | text | YES | - | Error details if failed |
| instagram_account_id | integer | YES | - | FK to instagram_accounts |
| credits_consumed | integer | YES | 0 | Total credits deducted |

**Primary Key:** id
**Unique Constraints:** job_id
**Foreign Keys:**
- user_id → users(id)
- instagram_account_id → instagram_accounts(id)

---

### Table: scraped_reels

**Purpose:** Store individual reel metadata

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| job_id | varchar(100) | NO | - | FK to scraping_jobs |
| user_id | integer | NO | - | FK to users |
| instagram_username | varchar(100) | NO | - | Instagram account scraped |
| reel_pk | varchar(100) | NO | - | Instagram reel ID |
| reel_code | varchar(50) | YES | - | Instagram short code |
| play_count | bigint | NO | - | Number of plays |
| comment_count | integer | NO | - | Number of comments |
| like_count | bigint | NO | - | Number of likes |
| is_reel_pinned | varchar(3) | YES | - | Yes/No |
| reel_url | text | YES | - | Direct URL to reel |
| scraped_at | timestamp | NO | now() | Scrape timestamp |
| raw_data | jsonb | YES | - | Full Instagram API response |
| instagram_account_id | integer | YES | - | FK to instagram_accounts |

**Primary Key:** id
**Foreign Keys:**
- job_id → scraping_jobs(job_id)
- user_id → users(id)
- instagram_account_id → instagram_accounts(id)

**Indexes:**
- idx_scraped_reels_user_id
- idx_scraped_reels_scraped_at (DESC)
- idx_scraped_reels_play_count
- idx_scraped_reels_like_count
- idx_scraped_reels_comment_count

---

### Table: user_groups

**Purpose:** Store user-created groups of Instagram usernames

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| user_id | integer | NO | - | FK to users |
| name | varchar(100) | NO | - | Group name |
| usernames | ARRAY | NO | - | Instagram usernames |
| created_at | timestamp | NO | now() | Group creation time |
| updated_at | timestamp | NO | now() | Last modification |
| last_used | timestamp | YES | - | Last loaded for scraping |
| times_used | integer | NO | - | Usage counter |

**Primary Key:** id
**Foreign Keys:**
- user_id → users(id)

**Unique Constraints:** (user_id, name)

---

### Table: activity_logs

**Purpose:** Comprehensive event logging

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| event_type | varchar(50) | NO | - | Event category |
| user_id | integer | YES | - | FK to users (optional) |
| instagram_account_id | integer | YES | - | FK to instagram_accounts |
| job_id | varchar(100) | YES | - | Related job ID |
| details | jsonb | YES | - | Additional event data |
| created_at | timestamp | YES | now() | Event timestamp |

**Primary Key:** id
**Foreign Keys:**
- user_id → users(id)
- instagram_account_id → instagram_accounts(id)

**Indexes:**
- idx_activity_logs_event_type
- idx_activity_logs_created_at (DESC)
- idx_activity_logs_user_id

**Event Types:**
- account_created
- scrape_started
- scrape_success
- scrape_failed
- credits_deducted
- credits_reset
- cookies_updated
- account_selected
- admin_action

---

### Table: api_keys

**Purpose:** API authentication for cookie updates

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| key_name | varchar(100) | NO | - | Descriptive name |
| api_key | varchar(255) | NO | - | Bcrypt hashed key |
| is_active | boolean | YES | true | Key status |
| permissions | jsonb | YES | ["update_cookies"] | Allowed operations |
| last_used_at | timestamp | YES | - | Last usage time |
| created_at | timestamp | YES | now() | Key creation time |

**Primary Key:** id
**Unique Constraints:** api_key

---

### Table: admin_users

**Purpose:** Admin panel authentication (separate from regular users)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | Auto | Primary key |
| username | varchar(100) | NO | - | Admin username |
| email | varchar(255) | NO | - | Admin email |
| password_hash | varchar(255) | NO | - | Bcrypt hashed password |
| is_active | boolean | YES | true | Account status |
| created_at | timestamp | YES | now() | Account creation |
| last_login | timestamp | YES | - | Last login time |

**Primary Key:** id
**Unique Constraints:** username, email

**Default Admin:**
- Username: admin
- Email: admin@example.com
- Password: admin123 (CHANGE IMMEDIATELY!)

---

### Database Views

The system includes 9 optimized views for analytics:

| View Name | Purpose |
|-----------|---------|
| v_user_summary | User statistics with credit usage |
| v_instagram_account_health | Cookie health and success rates |
| v_daily_stats | Daily scraping metrics |
| v_recent_activity | Recent events with details |
| v_job_performance | Job duration and success rates |
| v_hourly_usage_pattern | Usage patterns by hour |
| v_user_credits_summary | Credit usage breakdown |
| v_instagram_accounts_status | Account status overview |
| v_daily_activity_summary | Daily activity aggregation |

---

## 🚀 Phase 1: Multi-User System

**Status:** ✅ Implemented
**Date:** December 2025

### Overview

Phase 1 adds multi-user support with intelligent Instagram account rotation, credit-based usage limits, and comprehensive activity tracking.

### Key Features

#### 1. Instagram Account Pool & Rotation
- **Multiple Accounts:** System maintains a pool of Instagram accounts
- **Intelligent Selection:** Automatically chooses least-used active account
- **Usage Tracking:** Daily and lifetime statistics per account
- **Health Monitoring:** Cookie freshness and success rate tracking

#### 2. Credit System
- **Daily Quotas:** Each user has configurable daily limit (default: 2000 reels)
- **1 Credit = 1 Reel:** Credits consumed for each successfully scraped reel
- **Automatic Reset:** Credits reset daily at midnight
- **Admin Control:** Custom limits per user

#### 3. Activity Logging
- **Comprehensive:** All scraping events, rotations, admin actions logged
- **Debugging:** Detailed logs for troubleshooting
- **Analytics:** Track usage patterns and system health

### New Backend Modules

#### account_rotation.py

Handles intelligent account selection.

**Key Functions:**
- `get_least_used_account(db)` - Select least-used active account
- `increment_account_usage(db, account_id, reels_scraped, success)` - Update stats
- `reset_daily_counts(db)` - Reset counters at midnight
- `mark_account_failed(db, account_id)` - Track failures
- `pause_account(db, account_id)` - Temporarily disable account
- `resume_account(db, account_id)` - Re-enable account
- `get_account_stats(db, account_id)` - Get statistics
- `get_all_account_stats(db)` - Get all accounts stats

**Usage Example:**

```python
from account_rotation import get_least_used_account, increment_account_usage

# Get account for scraping
account = get_least_used_account(db)

# After scraping
increment_account_usage(db, account.id, reels_scraped=20, success=True)
```

#### credit_system.py

Manages user credit quotas.

**Key Functions:**
- `check_user_credits(db, user_id, required_credits)` - Validate credits
- `deduct_credits(db, user_id, credits)` - Consume credits
- `reset_all_daily_credits(db)` - Reset all users at midnight
- `get_user_credit_summary(db, user_id)` - Get credit info
- `update_user_credit_limit(db, user_id, new_limit)` - Admin: change limit

**Usage Example:**

```python
from credit_system import check_user_credits, deduct_credits

# Before scraping
if check_user_credits(db, user_id, required_credits=20):
    # Scrape reels
    deduct_credits(db, user_id, 20)
else:
    raise InsufficientCreditsError("Not enough credits")
```

### Setup Instructions

#### Step 1: Run Migration

```bash
psql -U scraper_user -d instagram_scraper -f Backend/migrations/001_multi_user_system.sql
```

This creates:
- 4 new tables (instagram_accounts, api_keys, admin_users, activity_logs)
- Adds credit fields to users table
- Adds Instagram account tracking to jobs and reels
- Creates indexes for performance
- Inserts default admin user

#### Step 2: Add Instagram Accounts

```python
from database import SessionLocal
from crud import create_instagram_account

db = SessionLocal()

account1 = create_instagram_account(
    db=db,
    username="insta_account_1",
    email="account1@gmail.com",
    password="your_password_here"
)

db.close()
```

#### Step 3: Test

```bash
cd Backend
python test_phase1.py
```

Expected: All tests pass ✅

### How It Works

#### Scraping Flow

1. User makes scrape request (e.g., 20 reels)
2. System checks credits: Does user have 20 credits?
   - ✅ Yes → Continue
   - ❌ No → Return "Insufficient credits" error
3. System selects Instagram account: Get least-used active account
4. Scraping job created: Links user, Instagram account, and job
5. Reels scraped: Using selected account's cookies
6. Credits deducted: 1 credit per successfully scraped reel
7. Usage updated: Instagram account's daily_scrape_count incremented
8. Activity logged: Event stored in activity_logs

#### Account Selection Algorithm

```sql
SELECT * FROM instagram_accounts
WHERE is_active = TRUE AND is_paused = FALSE
ORDER BY daily_scrape_count ASC, last_used_at ASC NULLS FIRST
LIMIT 1
```

This ensures:
- Only active, non-paused accounts used
- Least-used account selected first
- Never-used accounts get priority

---

## 🔧 Phase 2: Enhanced API & Cookie Management

**Status:** ✅ Implemented
**Date:** December 2025

### Overview

Phase 2 enhances scraping with automatic rotation, credit validation, cookie update endpoints, and remote cookie updater script.

### New Features

#### 1. Enhanced Scraping Endpoint
- **Automatic Credit Validation:** Checks credits before starting job
- **Automatic Account Rotation:** Selects least-used Instagram account
- **Comprehensive Logging:** All events logged to activity_logs
- **Better Error Handling:** Specific error codes

#### 2. Cookie Update API Endpoints
- **Individual Updates:** Update cookies for specific accounts
- **Bulk Updates:** Update multiple accounts at once
- **API Key Authentication:** Secure endpoints with hashed keys
- **Account Listing:** View all Instagram accounts

#### 3. Remote Cookie Updater Script
- **Automated Extraction:** Uses Playwright to login and extract cookies
- **Server Integration:** Automatically uploads to server via API
- **Multi-Account Support:** Processes multiple accounts sequentially
- **Windows Task Scheduler Ready:** Designed for scheduled execution

#### 4. Daily Reset Scheduler
- **Automatic Resets:** Runs daily at midnight
- **User Credits:** Resets all users' daily credits
- **Account Counters:** Resets Instagram accounts' daily scrape counts
- **Activity Logging:** Logs reset events

### New Backend Modules

#### scheduler.py

Background scheduler for daily resets.

**Key Functions:**
- `start_scheduler()` - Initialize scheduler
- `stop_scheduler()` - Gracefully stop
- `daily_reset_job()` - Async midnight job
- `run_manual_reset()` - Manual trigger for testing
- `get_scheduler_status()` - Check status and next run

**Automatic Startup:**
Scheduler automatically starts with FastAPI app.

**Manual Test:**

```bash
cd Backend
python scheduler.py
```

#### generate_api_key.py

Utility for API key management.

**Commands:**

```bash
# Create new API key
python generate_api_key.py create "Cookie Updater - Windows PC"

# List all API keys
python generate_api_key.py list

# Revoke an API key
python generate_api_key.py revoke 1
```

#### remote_cookie_updater.py

Automated cookie extraction script.

**Setup:**

1. Install Playwright:
```bash
pip install playwright
playwright install firefox
```

2. Configure script:
```python
SERVER_URL = "https://your-server.com"
API_KEY = "your-api-key-here"

INSTAGRAM_ACCOUNTS = [
    {
        "id": 2,
        "email": "account1@gmail.com",
        "password": "your_password"
    }
]
```

3. Test connection:
```bash
python remote_cookie_updater.py test
```

4. Run manually:
```bash
python remote_cookie_updater.py
```

**Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task:
   - Name: "Instagram Cookie Update"
   - Trigger: Repeat every 5 days at 2:00 AM
3. Action: Start a program
   - Program: `C:\Python\python.exe`
   - Arguments: `C:\path\to\remote_cookie_updater.py`
4. Settings:
   - Allow task to run on demand
   - Stop if runs longer than 1 hour

### API Endpoints (Phase 2)

#### POST /api/admin/instagram-accounts

Create new Instagram account in the pool.

**Headers:**
```
Authorization: Bearer <admin-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "new_instagram_account",
  "email": "newaccount@gmail.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Instagram account 'new_instagram_account' created successfully",
  "account": {
    "id": 4,
    "username": "new_instagram_account",
    "email": "newaccount@gmail.com",
    "is_active": true,
    "is_paused": false,
    "daily_scrape_count": 0,
    "total_scrapes": 0,
    "success_count": 0,
    "failure_count": 0,
    "cookies_updated_at": null,
    "created_at": "2025-12-24T10:30:00"
  }
}
```

**Error (409):**
```json
{
  "detail": "Instagram account with username 'new_instagram_account' already exists"
}
```

**Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

#### POST /api/admin/instagram-accounts/{account_id}/cookies

Update cookies for specific Instagram account.

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
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

**Response (200):**
```json
{
  "status": "success",
  "message": "Cookies updated for account insta_account_1",
  "account_id": 1,
  "account_username": "insta_account_1",
  "updated_at": "2025-12-18T14:30:22.123456"
}
```

#### POST /api/admin/instagram-accounts/bulk-update-cookies

Update cookies for multiple accounts.

**Request Body:**
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

**Response (200):**
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
    }
  ],
  "errors": []
}
```

#### GET /api/admin/instagram-accounts

List all Instagram accounts.

**Headers:**
```
X-API-Key: your-api-key-here
```

**Response (200):**
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
      "cookies_updated_at": "2025-12-18T14:30:22",
      "last_used_at": "2025-12-18T15:00:00"
    }
  ]
}
```

### Testing Phase 2

```bash
cd Backend
python test_phase2.py
```

Expected: All 7 tests pass ✅

---

## 🎨 Phase 3: Admin Panel

**Status:** ✅ Implemented
**Date:** December 18, 2025

### Overview

Phase 3 adds comprehensive admin panel with web-based user management, Instagram account monitoring, activity logs viewer, and system statistics dashboard.

### Features

#### 1. Admin Panel Web UI
- **Modern Dark Theme:** Black/purple/white design
- **Responsive Layout:** Works on desktop and mobile
- **Sidebar Navigation:** Easy access to features
- **Real-time Updates:** Notification system

#### 2. User Management Interface
- **User List:** View all users with credit usage
- **Search & Filter:** Find users, filter by status
- **Edit Users:** Modify credit limits, activate/deactivate
- **User Details:** View stats and recent jobs
- **Usage Tracking:** Visual progress bars

#### 3. Instagram Account Management
- **Account Pool Monitoring:** View all Instagram accounts
- **Cookie Health Status:** Visual indicators
- **Usage Statistics:** Daily and lifetime counts
- **Success Rates:** Track performance
- **Filter by Status:** Active, paused, healthy, expired

#### 4. Activity Logs Viewer
- **Comprehensive Logging:** All system events
- **Advanced Filtering:** Date range, event type, user, account
- **Export to CSV:** Download logs
- **Real-time Updates:** See events as they happen

#### 5. System Statistics Dashboard
- **Overview Cards:** Users, accounts, today's reels, success rate
- **Daily Trends Chart:** Reels scraped and active users
- **Credit Usage Chart:** Top consumers
- **Account Distribution:** Pie chart
- **Hourly Patterns:** Peak usage times
- **Success/Failure Rates:** Donut chart

#### 6. Performance Optimizations
- **Database Indexes:** Faster queries
- **Database Views:** Precomputed statistics
- **Efficient Queries:** Optimized SQL

### Setup Instructions

#### Step 1: Run Migration

```bash
psql -U scraper_user -d instagram_scraper -f Backend/migrations/002_phase3_indexes_views.sql
```

This creates:
- 10 indexes for faster queries
- 6 database views for statistics
- Performance optimizations

#### Step 2: Create Admin User

Default admin already created:
- Username: `admin`
- Password: `admin123`
- ⚠️ **CHANGE PASSWORD IMMEDIATELY!**

Or create new admin:

```python
from database import SessionLocal
from models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

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

#### Step 3: Access Admin Panel

1. Start server: `python app.py`
2. Navigate to: `http://localhost:8080/static/admin/index.html`
3. Login with admin credentials

### Admin Panel Pages

#### Dashboard

**Overview Cards:**
- Total Users (active/inactive)
- Instagram Accounts (active/paused)
- Today's Reels (jobs completed)
- Success Rate (percentage)

**Charts:**
- Daily Scraping Trends (line chart)
- Top Credit Consumers (bar chart)

**Recent Activity:**
- Last 10 events with icons

#### User Management

**Features:**
- Search by email/username
- Filter by status (all/active/inactive)
- Edit credit limits
- Activate/deactivate users
- View user details

**User Table Columns:**
- Email, Username
- Credits (used/limit with progress bar)
- Usage percentage
- Status badge
- Created date
- Actions (Edit, Details)

#### Instagram Accounts

**Features:**
- Filter by status
- Cookie health monitoring
- Usage statistics
- Success rate tracking

**Account Table Columns:**
- Username, Email
- Status badge
- Cookie Health (with age)
- Daily Usage
- Total Scrapes
- Success Rate (progress bar)
- Last Used

#### Activity Logs

**Features:**
- Date range filter
- Event type filter
- Export logs to CSV
- Detailed information

**Log Table Columns:**
- Timestamp
- Event Type (colored badge)
- User ID
- Instagram Account ID
- Job ID
- Details (JSON)

#### Statistics

**Advanced Charts:**
- Account Usage Distribution (pie chart)
- Hourly Usage Pattern (bar chart)
- Success vs Failure Rates (donut chart)

**Time Range Filter:**
- Last 7/14/30/90 days

---

## 📡 API Documentation

### Base URL

```
http://localhost:8080
```

### Authentication Endpoints

#### POST /api/auth/signup

Register new user.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "myusername",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "is_active": true,
  "created_at": "2025-12-18T14:30:22.123456"
}
```

#### POST /api/auth/login

User login.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "myusername"
  }
}
```

#### GET /api/auth/me

Get current user info.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "is_active": true,
  "created_at": "2025-12-18T14:30:22",
  "daily_credit_limit": 2000,
  "credits_used_today": 150,
  "last_credit_reset_date": "2025-12-18"
}
```

### Scraping Endpoints

#### POST /api/scrape

Start scraping job (enhanced with rotation & credits).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "usernames": ["cristiano", "leomessi"],
  "reel_count": 20,
  "group_id": null
}
```

**Response (200):**
```json
{
  "job_id": "job_20251218_143022_123456",
  "status": "started",
  "message": "Scraping job started using Instagram account insta_account_1"
}
```

**Error (403):**
```json
{
  "detail": "Insufficient credits. Remaining: 50, Required: 40"
}
```

**Error (503):**
```json
{
  "detail": "All Instagram accounts are exhausted. Try again later."
}
```

#### GET /api/job/{job_id}

Get job status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "job_id": "job_20251218_143022_123456",
  "status": "completed",
  "progress": 100,
  "duration": 45.2,
  "results": [
    {
      "username": "cristiano",
      "status": "success",
      "reels_scraped": 20
    }
  ]
}
```

### Group Management Endpoints

#### GET /api/groups

List user's groups.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "groups": [
    {
      "id": 1,
      "name": "Favorite Athletes",
      "usernames": ["cristiano", "leomessi", "neymarjr"],
      "created_at": "2025-12-18T14:30:22",
      "times_used": 5,
      "last_used": "2025-12-19T10:15:00"
    }
  ]
}
```

#### POST /api/groups

Create new group.

**Request:**
```json
{
  "name": "Tech Influencers",
  "usernames": ["mkbhd", "unboxtherapy", "linustech"]
}
```

**Response (200):**
```json
{
  "id": 2,
  "name": "Tech Influencers",
  "usernames": ["mkbhd", "unboxtherapy", "linustech"],
  "created_at": "2025-12-18T14:30:22",
  "times_used": 0
}
```

#### PUT /api/groups/{group_id}

Update existing group.

**Request:**
```json
{
  "name": "Tech Influencers Updated",
  "usernames": ["mkbhd", "unboxtherapy", "linustech", "mrwhosetheboss"]
}
```

#### DELETE /api/groups/{group_id}

Delete group.

**Response (200):**
```json
{
  "message": "Group deleted successfully"
}
```

### Analytics Endpoints

#### GET /api/analytics

Get analytics with filters.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `username` (string): Filter by Instagram username
- `min_plays` (int): Minimum play count
- `min_likes` (int): Minimum like count
- `min_comments` (int): Minimum comment count
- `sort_by` (string): date/plays/likes/comments
- `sort_order` (string): asc/desc
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50)

**Response (200):**
```json
{
  "reels": [
    {
      "id": 1,
      "instagram_username": "cristiano",
      "reel_code": "ABC123",
      "play_count": 1500000,
      "like_count": 50000,
      "comment_count": 2000,
      "reel_url": "https://instagram.com/reel/ABC123",
      "scraped_at": "2025-12-18T14:30:22"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 50,
  "total_pages": 3
}
```

#### GET /api/analytics/export

Export filtered data as CSV.

**Query Parameters:** Same as /api/analytics

**Response:** CSV file download

### Admin Endpoints

#### POST /api/admin/auth/login

Admin login.

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "admin": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

#### GET /api/admin/users

List all users with filters.

**Headers:**
```
Authorization: Bearer <admin-token>
```

**Query Parameters:**
- `search` (string): Search email/username
- `is_active` (boolean): Filter by status

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "myusername",
      "is_active": true,
      "daily_credit_limit": 2000,
      "credits_used_today": 150,
      "created_at": "2025-12-18T14:30:22"
    }
  ]
}
```

#### PUT /api/admin/users/{user_id}

Update user details.

**Request:**
```json
{
  "is_active": true,
  "daily_credit_limit": 5000
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "is_active": true,
  "daily_credit_limit": 5000
}
```

#### GET /api/admin/logs

Get activity logs.

**Query Parameters:**
- `start_date` (date): Filter start
- `end_date` (date): Filter end
- `event_type` (string): Filter by event
- `user_id` (int): Filter by user
- `limit` (int): Max results

**Response (200):**
```json
{
  "logs": [
    {
      "id": 1,
      "event_type": "scrape_success",
      "user_id": 1,
      "instagram_account_id": 2,
      "job_id": "job_123",
      "details": {...},
      "created_at": "2025-12-18T14:30:22"
    }
  ],
  "total": 100
}
```

#### GET /api/admin/stats/overview

Get system overview statistics.

**Response (200):**
```json
{
  "total_users": 50,
  "active_users": 45,
  "total_instagram_accounts": 3,
  "active_instagram_accounts": 2,
  "today_reels_scraped": 500,
  "today_jobs_completed": 25,
  "overall_success_rate": 95.5
}
```

---

## 👤 User Dashboard Guide

### Getting Started

#### 1. Create Account

1. Navigate to `http://localhost:8080`
2. Click "Sign Up" tab
3. Fill in:
   - Email: valid email address
   - Username: 3+ characters
   - Password: 8+ characters with letters and numbers
   - Confirm Password
4. Click "Create Account"
5. System creates account with 2000 daily credits

#### 2. Login

1. Enter email and password
2. Click "Login"
3. JWT token saved (7 days expiration)
4. Redirected to main dashboard

### Using the Dashboard

#### Scraper Page

**Method 1: Single Username**
1. Enter Instagram username
2. Click "Add" button
3. Repeat for multiple accounts
4. Username appears as purple tag

**Method 2: Bulk Entry**
1. Click "Add Multiple Usernames" textarea
2. Enter usernames, one per line
3. Click "Submit All"

**Method 3: Load from Group**
1. Click Groups tab
2. Find your saved group
3. Click "Load Group"
4. Usernames populate automatically

**Start Scraping:**
1. Set "Number of Reels" (default: 20)
2. Click "Start Scraping"
3. Job starts immediately
4. Switch to "Job Tracker" tab to monitor progress

#### Job Tracker Page

**Features:**
- View all your scraping jobs
- Real-time progress updates
- Filter by status (running/completed/failed)
- See duration and results
- Jobs auto-refresh every 2 seconds

**Job Card Information:**
- Job ID
- Timestamp
- Status badge (running/success/failed)
- Accounts scraped
- Reels per account
- Duration
- Success/failure counts
- Target accounts list

**Actions:**
- Click "Clear History" to remove all jobs
- Click "Refresh" to manually update

#### Groups Page

**Create Group:**
1. Add usernames to scraper
2. Enter group name
3. Click "Save as Group"
4. Group appears in sidebar

**Edit Group:**
1. Click "Edit" icon
2. Modify name or usernames
3. Click "Save Changes"

**Delete Group:**
1. Click "Delete" icon
2. Confirm deletion

**Load Group:**
1. Click "Load Group" button
2. Usernames populate scraper
3. Times used increments
4. Last used timestamp updates

#### Analytics Page

**Filters:**
- Instagram Username: Partial match search
- Minimum Plays: Filter by play count
- Minimum Likes: Filter by like count
- Minimum Comments: Filter by comment count

**Sorting:**
- Date Scraped (default)
- Play Count
- Like Count
- Comment Count
- Ascending/Descending

**Actions:**
- Click "Apply Filters"
- Navigate pages with Prev/Next
- Click "Export CSV" to download data

**Table Columns:**
- Instagram Username
- Reel Code
- Play Count (formatted with commas)
- Like Count
- Comment Count
- Scraped Date
- Reel URL (clickable)

### Credits System

**Understanding Credits:**
- Located in sidebar: "Daily Credits"
- Shows: Used / Limit
- Progress bar visualizes usage
- Remaining credits displayed

**How Credits Work:**
- 1 Credit = 1 Successfully Scraped Reel
- Failed scrapes don't consume credits
- Resets daily at midnight
- Admin can change your limit

**What Happens When Out of Credits:**
- Scraping requests rejected
- Error message: "Insufficient credits"
- Wait until midnight for reset
- Or contact admin for limit increase

---

## 🛡 Admin Panel Guide

### Access

1. Navigate to: `http://localhost:8080/static/admin/index.html`
2. Login with admin credentials
3. Dashboard loads automatically

### Dashboard Page

**Overview Cards:**
- **Total Users:** Click to view all users
- **Instagram Accounts:** Click to manage accounts
- **Today's Reels:** Total scraped today
- **Success Rate:** Overall system health

**Daily Trends Chart:**
- Last 7/14/30 days
- Blue line: Reels scraped
- Purple line: Active users
- Hover for exact values

**Top Credit Consumers:**
- Bar chart of top 10 users
- Click username to view details

**Recent Activity:**
- Last 10 system events
- Icons for event types
- Timestamps relative (e.g., "2 hours ago")

### User Management

**User List:**
- Search by email/username
- Filter: All / Active / Inactive
- Sort by email, credits, created date

**Edit User:**
1. Click "Edit" button
2. Modify:
   - Active status (checkbox)
   - Daily Credit Limit (number)
3. Click "Save Changes"
4. Confirmation message appears

**View User Details:**
1. Click "Details" button
2. See:
   - Total jobs
   - Total reels scraped
   - Success rate
   - Recent jobs list

**User Table:**
- Email (clickable to edit)
- Username
- Credits: Progress bar (used/limit)
- Usage: Percentage with color coding
  - Green: < 75%
  - Yellow: 75-90%
  - Red: > 90%
- Status: Active/Inactive badge
- Created: Date with time
- Actions: Edit, Details buttons

### Instagram Accounts

**Filter Options:**
- All Accounts
- Active Only
- Paused Only
- Healthy Cookies (0-5 days old)
- Expired Cookies (>7 days old)

**Account Table:**
- Username/Email
- Status: Active/Paused/Inactive badge
- Cookie Health:
  - 🟢 Healthy (0-5 days)
  - 🟡 Expiring (5-7 days)
  - 🔴 Expired (>7 days)
  - ⚫ No cookies
- Daily Usage: Count
- Total Scrapes: Lifetime count
- Success Rate: Progress bar with percentage
- Last Used: Timestamp

**Create New Account:**

*Professional UI matching Export CSV button design with improved modal form*

1. Click "➕ Add Instagram Account" button (purple button with plus icon)
2. Modal opens (650px width for optimal visibility)
3. Fill in form with clearly labeled fields:
   - Instagram Username (3+ characters, required)
   - Instagram Email (valid email, required)
   - Instagram Password (8+ characters, required)
4. Check confirmation checkbox (acknowledging password storage)
5. Click "Create Account" button (styled to match dashboard buttons)
6. Account appears in table with no cookies initially
7. Use cookie update feature to add valid cookies
8. Account becomes available in rotation pool

**Design Features:**
- Button styled identically to "Export CSV" from user dashboard
- Modal uses proper CSS classes for consistent styling
- All form fields fully visible (no overflow)
- Professional close button (×) in top-right
- Clean, organized layout with proper spacing
- Cancel and Create Account buttons properly aligned

**Actions:**
- Click username to view details
- Pause/Resume account
- Update cookies via cookie update modal

### Activity Logs

**Filters:**
- **Date Range:**
  - Start Date (date picker)
  - End Date (date picker)
  - Default: Last 7 days
- **Event Type:** Dropdown with all event types

**Export:**
1. Apply filters
2. Click "Export CSV"
3. File downloads with filtered logs

**Log Table:**
- Timestamp: Full date/time
- Event Type: Colored badge
  - Green: Success events
  - Blue: Info events
  - Red: Error events
  - Yellow: Warning events
- User ID: Link to user details
- Instagram Account ID: Link to account
- Job ID: Link to job (if applicable)
- Details: JSON object (hover to see full)

**Event Types:**
- account_created
- scrape_started
- scrape_success
- scrape_failed
- credits_deducted
- credits_reset
- cookies_updated
- account_selected
- admin_action
- user_created
- user_updated

### Statistics Page

**Time Range Selector:**
- Last 7 days
- Last 14 days
- Last 30 days
- Last 90 days

**Charts:**

1. **Account Usage Distribution (Pie Chart)**
   - Shows scrape distribution across Instagram accounts
   - Colors: Different color per account
   - Hover: See exact count and percentage

2. **Hourly Usage Pattern (Bar Chart)**
   - 24 bars (0-23 hours)
   - Shows peak usage times
   - Helps identify optimal scheduling

3. **Success vs Failure Rates (Donut Chart)**
   - Green: Successful scrapes
   - Red: Failed scrapes
   - Center: Total percentage
   - Hover: See exact counts

**Insights:**
- Identify most-used Instagram accounts
- Find peak usage hours
- Monitor success rate trends
- Detect accounts needing attention

---

## ⚙️ Configuration

### Environment Variables

**Backend/.env file:**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/instagram_scraper

# JWT Authentication
SECRET_KEY=your-secret-key-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Application Settings
MAX_GROUPS_PER_USER=100
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
DEBUG=True
ENVIRONMENT=development

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
```

### Changing Credit Limits

**Default Limit (for new users):**

Edit `Backend/migrations/001_multi_user_system.sql`:
```sql
ALTER TABLE users ADD COLUMN daily_credit_limit INTEGER DEFAULT 2000;
```

Change `2000` to desired default.

**Individual User:**

Admin Panel → Users → Edit → Modify "Daily Credit Limit"

Or via Python:
```python
from credit_system import update_user_credit_limit
update_user_credit_limit(db, user_id=1, new_limit=5000)
```

### Scheduler Timezone Configuration

**Default:** Midnight (00:00) IST (Indian Standard Time - Asia/Kolkata)

**Current Configuration:**
```python
# Backend/scheduler.py (line 21)
scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kolkata'))
```

**To Change Timezone:**

Edit `Backend/scheduler.py`:
```python
import pytz

# For a different timezone (e.g., US Eastern Time)
scheduler = AsyncIOScheduler(timezone=pytz.timezone('US/Eastern'))

# Or using Python 3.9+ built-in zoneinfo
from zoneinfo import ZoneInfo
scheduler = AsyncIOScheduler(timezone=ZoneInfo('America/New_York'))
```

**Available Timezones:**
- IST (India): `'Asia/Kolkata'`
- UTC: `'UTC'`
- US Eastern: `'US/Eastern'` or `'America/New_York'`
- UK: `'Europe/London'`
- Full list: [IANA Time Zone Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

**To Change Reset Time (within same timezone):**

Edit `Backend/scheduler.py`:
```python
scheduler.add_job(
    daily_reset_job,
    trigger=CronTrigger(hour=2, minute=30),  # 2:30 AM IST instead of midnight
    id='daily_reset',
    name='Daily Credit and Usage Counter Reset',
    replace_existing=True
)
```

**Manual Reset Command:**

To reset counters immediately without waiting for midnight:
```bash
cd Backend
python -c "from scheduler import run_manual_reset; run_manual_reset()"
```

### Changing Cookie Update Frequency

**Default:** Every 5 days

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Find "Instagram Cookie Update" task
3. Edit Trigger
4. Change "Repeat task every: X days"

**Recommended:**
- Minimum: 3 days
- Maximum: 7 days
- Optimal: 5 days

### Scraping Parameters

**Sleep Between Requests:**

Edit `Backend/Scripts/pipeline.py`:
```python
fetch_reels_paginated(..., sleep_seconds=3.0)  # Change to 5.0 for slower
```

**Max Reels Per Page:**

Edit `Backend/Scripts/pipeline.py`:
```python
fetch_reels_paginated(..., max_per_page=50)  # Max: 50
```

### CORS Configuration

**Development:**
```env
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

**Production:**
```env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

Edit `Backend/app.py` for more control:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "module 'crud' has no attribute 'log_activity'" Error

**Symptom:** When creating Instagram account via admin panel, error appears: "Failed to create Instagram account: module 'crud' has no attribute 'log_activity'"

**Cause:** Incorrect function name in backend code

**Solution:**
This has been fixed. The correct function is `crud.create_activity_log()` not `crud.log_activity()`. If you encounter this error:
1. Check [Backend/app.py:947](Backend/app.py) - should use `crud.create_activity_log()`
2. Restart backend server: `python app.py`
3. Try creating account again

**Fixed in:** Version 3.0.1 (December 2025)

---

#### 2. Admin Dashboard 500 Error - "ScrapingJob has no attribute 'created_at'"

**Symptom:** When opening admin panel, console shows errors:
- `GET /api/admin/stats/overview 500 (Internal Server Error)`
- `Error: Failed to fetch system overview: type object 'ScrapingJob' has no attribute 'created_at'`

**Cause:** Backend code using incorrect field names for ScrapingJob model

**Solution:**
This has been fixed in version 3.0.2. The correct field names are:
- `start_time` (not `created_at`)
- `end_time` (not `completed_at`)
- `usernames` (not `target_usernames`)
- `len(job.reels)` for count (not `reels_scraped`)

If you encounter this error:
1. Check [Backend/admin_routes.py](Backend/admin_routes.py) for correct field names
2. Restart backend server: `python app.py`
3. Refresh admin panel in browser

**Fixed in:** Version 3.0.2 (December 2025)

---

#### 3. User Details Modal Error - "'ScrapingJob' object has no attribute 'target_usernames'"

**Symptom:** When clicking "Details" button in admin Users tab, console shows:
- `GET /api/admin/users/{id} 500 (Internal Server Error)`
- `Error: Failed to fetch user details: 'ScrapingJob' object has no attribute 'target_usernames'`

**Cause:** Same as issue #2 - incorrect field name references

**Solution:**
Fixed in version 3.0.2. If encountered, verify backend uses correct field names and restart server.

**Fixed in:** Version 3.0.2 (December 2025)

---

#### 4. "No access token found" in Console

**Symptom:** Credit meter shows 0/2000 but doesn't update

**Cause:** Authentication token issue

**Solution:**
1. Clear browser localStorage
2. Logout and login again
3. Hard refresh (Ctrl+Shift+R)
4. Check if `authToken` exists in localStorage (F12 → Application → Local Storage)

#### 5. Daily Usage Showing Aggregate Totals / Credits Not Resetting at Midnight

**Symptom:**
- Admin panel shows high daily usage numbers (e.g., 60, 272) that don't reset
- User credits still showing used from previous day after midnight IST
- "Today's" usage shows cumulative data from multiple days

**Cause:** Timezone mismatch - Reset happening at server midnight instead of IST midnight

**Solution (FIXED in v3.0.4):**

The scheduler is now configured for IST timezone. If you upgraded from an older version:

**Step 1: Verify Scheduler Timezone**
```bash
# Restart backend server to load new timezone config
cd Backend
python app.py
```

Look for this log message:
```
[OK] Scheduler started successfully
Timezone: Asia/Kolkata (IST - Indian Standard Time)
Daily reset job scheduled for 00:00 IST (midnight) every day
```

**Step 2: Manual Reset (Clear Old Data)**
```bash
cd Backend
python -c "from scheduler import run_manual_reset; run_manual_reset()"
```

Expected output:
```
[OK] Reset credits for X user(s)
[OK] Reset daily counts for Y Instagram account(s)
```

**Step 3: Verify Results**
- Admin Panel → Instagram Accounts → Daily Usage should show **0**
- Admin Panel → Users → Credits should show **0 / [limit]**
- Total Scrapes remain unchanged (lifetime counter)

**Note:** After manual reset, automatic resets will happen at midnight IST every night.

**Fixed in:** Version 3.0.4 (December 25, 2025)

#### 6. Scraping Fails - No Reels Scraped

**Symptom:** Job completes but 0 reels scraped

**Cause:** Instagram account has invalid/test cookies

**Diagnosis:**
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

    if cookie_len < 100:
        print(f"  ⚠️ WARNING: Cookies appear invalid")
```

**Solution:**

Option 1 - Pause invalid accounts:
```python
from account_rotation import pause_account
pause_account(db, account_id=1)
```

Option 2 - Update cookies:
```bash
python Backend/Scripts/remote_cookie_updater.py
```

Option 3 - Manually update via API:
```python
import requests

cookies = {
    "sessionid": "valid_session_id_here",
    "csrftoken": "valid_csrf_token_here"
}

response = requests.post(
    "http://localhost:8080/api/admin/instagram-accounts/1/cookies",
    headers={"X-API-Key": "your-api-key"},
    json=cookies
)
```

#### 7. "All Instagram accounts are exhausted"

**Symptom:** Can't start scraping job

**Cause:** All Instagram accounts are paused or inactive

**Solution:**
```bash
# Check account status
cd Backend
python -c "
from database import SessionLocal
from crud import get_all_instagram_accounts

db = SessionLocal()
accounts = get_all_instagram_accounts(db)
active = [a for a in accounts if a.is_active and not a.is_paused]
print(f'Active accounts: {len(active)}')
for a in active:
    print(f'  - {a.username}')
"
```

Resume accounts:
```python
from account_rotation import resume_account
resume_account(db, account_id=1)
```

Or add new accounts.

#### 8. Database Connection Failed

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps

# If not running
docker start instagram_scraper_db

# Check logs
docker logs instagram_scraper_db

# Verify port
# Windows:
netstat -ano | findstr :5432
# macOS/Linux:
lsof -i :5432
```

#### 9. Admin Panel Won't Load

**Symptom:** Blank page or "Failed to load profile"

**Solution:**
1. Check backend is running
2. Verify admin user exists:
```bash
psql -U scraper_user -d instagram_scraper -c "SELECT * FROM admin_users;"
```
3. Clear browser cache
4. Check browser console (F12) for errors
5. Try different browser

#### 10. Playwright Login Fails (Cookie Updater)

**Error:** "Login failed" or "Error during login"

**Cause:** Instagram detected automation or 2FA enabled

**Solution:**
- Use browser cookie method instead (recommended)
- Disable headless mode to debug:
  ```python
  browser = await playwright.firefox.launch(headless=False)
  ```
- Check if 2FA is enabled (not supported)
- Use valid Instagram credentials

#### 11. Rate Limiting / Blocked Requests

**Symptom:** Instagram returns errors or empty responses

**Solution:**
- Increase sleep time:
  ```python
  fetch_reels_paginated(..., sleep_seconds=5.0)
  ```
- Use valid session cookies
- Wait 30-60 minutes before retrying
- Add more Instagram accounts to pool

#### 12. Charts Not Displaying (Admin Panel)

**Symptom:** Empty chart areas

**Solution:**
1. Check browser console for Chart.js errors
2. Verify Chart.js CDN is accessible
3. Check if data endpoints return valid JSON
4. Inspect network tab for failed API calls
5. Clear browser cache

#### 13. Database Migration Fails

**Error:** `column "created_at" does not exist`

**Solution:**

Run migrations manually:
```bash
# Connect to database
psql -U scraper_user -d instagram_scraper

# Create tables step by step
# Copy SQL from migrations/*.sql
```

Or drop and recreate:
```bash
docker-compose down -v
docker-compose up -d
psql -U scraper_user -d instagram_scraper -f migrations/001_multi_user_system.sql
psql -U scraper_user -d instagram_scraper -f migrations/002_phase3_indexes_views.sql
```

---

## 🔐 Security

### Best Practices

#### Passwords
- **SECRET_KEY:** Generate with `openssl rand -hex 32`
- **Database Password:** Use strong password (20+ characters)
- **User Passwords:** Minimum 8 characters, letters + numbers enforced
- **Admin Password:** CHANGE DEFAULT PASSWORD IMMEDIATELY

#### Environment Variables
- **Never commit .env** to version control
- Add to `.gitignore`:
  ```
  .env
  *.env
  ```
- Use `.env.example` as template

#### CORS
- **Development:** Allow localhost
- **Production:** Restrict to your domain only
  ```python
  allow_origins=["https://yourdomain.com"]
  ```

#### HTTPS
- **Production:** Use HTTPS only
- Install SSL certificate (Let's Encrypt)
- Configure Nginx reverse proxy

#### Rate Limiting
- **Enabled:** FastAPI slowapi middleware
- **Default:** 60 requests/minute per IP
- Adjust in `app.py`:
  ```python
  limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
  ```

#### Database
- **User Isolation:** Enforced at query level
- **SQL Injection:** Prevented by SQLAlchemy ORM
- **Foreign Keys:** CASCADE delete prevents orphaned records

#### JWT Tokens
- **Expiration:** 7 days (configurable)
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Storage:** localStorage (client-side)
- **Transmission:** Authorization header only

#### API Keys
- **Hashing:** Bcrypt hashed before storage
- **Permissions:** JSONB field for granular control
- **Revocation:** Set `is_active = false`
- **Rotation:** Generate new keys periodically

#### Instagram Cookies
- **Encryption:** Store in database as JSONB
- **Access Control:** Admin-only endpoints
- **Expiration:** Auto-refresh every 5 days
- **Security:** Keep cookies private (full account access)

### Production Checklist

Before deploying to production:

- [ ] Change SECRET_KEY in .env
- [ ] Change admin password
- [ ] Change database password
- [ ] Enable HTTPS
- [ ] Restrict CORS to production domain
- [ ] Set DEBUG=False
- [ ] Set ENVIRONMENT=production
- [ ] Configure firewall (ports 80, 443, 5432)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Enable monitoring (Sentry, etc.)
- [ ] Test all features
- [ ] Load test with expected traffic
- [ ] Create admin user with strong password
- [ ] Document all credentials securely

---

## 🤝 Contributing

### Development Setup

```bash
# 1. Fork repository
# 2. Clone your fork
git clone https://github.com/yourusername/Instagram_reel_scrapper.git

# 3. Create feature branch
git checkout -b feature/amazing-feature

# 4. Make changes
# 5. Test thoroughly

# 6. Commit changes
git commit -m "Add some amazing feature"

# 7. Push to branch
git push origin feature/amazing-feature

# 8. Open Pull Request
```

### Code Style

- **Python:** PEP 8 style guide
- **JavaScript:** ES6+ syntax
- **SQL:** Uppercase keywords
- **Comments:** Clear and concise

### Testing

Before submitting PR:
```bash
# Run Phase 1 tests
cd Backend
python test_phase1.py

# Run Phase 2 tests
python test_phase2.py

# Test all features manually
```

### Areas for Improvement

- [ ] Add unit tests for all modules
- [ ] Implement Celery for distributed tasks
- [ ] Add Redis for job queue
- [ ] Proxy support for scraping
- [ ] Real-time notifications (WebSockets)
- [ ] Export to multiple formats (Excel, JSON)
- [ ] Advanced analytics (charts, graphs)
- [ ] Email notifications
- [ ] Two-factor authentication
- [ ] API rate limiting per user
- [ ] Webhook support
- [ ] CLI tool
- [ ] Docker compose for full stack
- [ ] Kubernetes deployment config

---

## 📝 Changelog

### Version 3.0.4 (December 25, 2025)

**CRITICAL FIX: IST Timezone & Date Format Standardization**

**Timezone Configuration:**
- ✅ **Fixed daily reset timezone to IST (Indian Standard Time - Asia/Kolkata)**
  - Previous: Reset at server midnight (likely UTC ~5:30 AM IST)
  - Now: Reset at **00:00:00 IST** (midnight IST)
  - Added `timezone=pytz.timezone('Asia/Kolkata')` to AsyncIOScheduler

- ✅ Enhanced scheduler logging with timezone information
  - Logs now show "Timezone: Asia/Kolkata (IST - Indian Standard Time)"
  - Clear indication of scheduled reset time in IST

**Date Format Standardization:**
- ✅ **All dates now display in DD-MM-YYYY format (Indian standard)**
  - Created global date formatter utility (`Frontend/utils/dateFormatter.js`)
  - Replaced all US-format dates (MM/DD/YYYY) with DD-MM-YYYY
  - Timestamps use 24-hour format: DD-MM-YYYY HH:MM:SS

- ✅ Consistent date formatting across entire application:
  - User dashboard job tracker: DD-MM-YYYY HH:MM:SS
  - Analytics page: DD-MM-YYYY HH:MM:SS
  - Admin panel users tab: DD-MM-YYYY
  - Admin panel accounts tab: DD-MM-YYYY HH:MM:SS
  - Admin panel logs tab: DD-MM-YYYY HH:MM:SS
  - Admin panel stats charts: DD-MM-YYYY

**Manual Reset Command:**
- ✅ Added quick reset command for immediate testing:
  ```bash
  python -c "from scheduler import run_manual_reset; run_manual_reset()"
  ```

**Files Modified:**
- `Backend/scheduler.py` - Added IST timezone configuration
- `Frontend/utils/dateFormatter.js` - **NEW FILE** - Global date formatting functions
- `Frontend/script.js` - Removed ES6 imports, use global functions
- `Frontend/analytics.js` - Removed ES6 imports, use global functions
- `Frontend/admin/components/users.js` - Removed ES6 imports, use global functions
- `Frontend/admin/components/accounts.js` - Removed ES6 imports, use global functions
- `Frontend/admin/components/logs.js` - Removed ES6 imports, use global functions
- `Frontend/admin/components/stats.js` - Removed ES6 imports, use global functions
- `Frontend/index.html` - Load dateFormatter.js as global script
- `Frontend/admin/index.html` - Load dateFormatter.js as global script
- `CLAUDE.md` - Documentation updates

**Impact:**
- ✅ Daily reset now happens at correct IST midnight
- ✅ No more timezone confusion about "today's" usage
- ✅ Dates easy to read for Indian users (DD-MM-YYYY)
- ✅ Consistent 24-hour time format throughout
- ✅ Manual reset available for immediate testing
- ✅ Clear scheduler timezone logging

**Upgrade Notes:**
If upgrading from v3.0.3 or earlier:
1. Restart backend server to load new timezone config
2. Run manual reset to clear accumulated daily counters
3. Hard refresh browser (Ctrl+Shift+R) to load new date formatting

---

### Version 3.0.3 (December 25, 2025)

**Admin Panel Design Enhancements:**
- Replaced all emoji/text icons with professional SVG graphics throughout admin panel
  - Dashboard overview cards now use proper SVG icons (users, accounts, reels, success rate)
  - Sidebar navigation icons updated (dashboard, users, accounts, logs, statistics)
  - Notification bell icon now white (#ffffff) for better visibility
  - Activity/notification items use color-coded SVG icons
  - Toast notifications use SVG icons (success, error, warning, info)

**UI Improvements:**
- Removed empty purple logo circle above "Admin Panel" title
  - Set `.sidebar-logo { display: none; }` for cleaner look

- Enhanced notification panel visibility and styling
  - Added purple border (`border: 2px solid var(--accent-purple)`)
  - Increased max-height to 500px
  - Added border-radius for modern appearance
  - Created dedicated CSS classes for notification items
  - Replaced inline styles with semantic class names
  - Added `.notification-empty` for empty state

**Icon System:**
- Created comprehensive SVG icon library with color coding:
  - Purple (#8b5cf6): scrape_started, user_created, account_rotated, daily_reset
  - Green (#10b981): scrape_success, cookies_updated, account_created
  - Red (#ef4444): scrape_failed
  - Yellow (#f59e0b): user_updated, credits_deducted
  - Gray (#9ca3af): default fallback

**Files Modified:**
- `Frontend/admin/index.html` - Updated all icon SVGs, removed logo
- `Frontend/admin/admin.css` - Added icon CSS classes, notification styling
- `Frontend/admin/admin.js` - Updated notification rendering
- `Frontend/admin/components/stats.js` - Replaced emoji icons with SVG
- `CLAUDE.md` - Documentation updates

**Impact:**
- ✅ Professional, consistent design matching user dashboard
- ✅ All icons clearly visible with proper colors
- ✅ Notification panel fully functional and styled
- ✅ No more empty circles or missing emojis
- ✅ Improved accessibility and visual hierarchy

---

### Version 3.0.2 (December 24, 2025)

**Critical Bug Fixes:**
- Fixed admin dashboard `/api/admin/stats/overview` 500 error
  - Changed `ScrapingJob.created_at` → `ScrapingJob.start_time` (lines 278, 859)
  - Changed `job.created_at` → `job.start_time` (line 288)
  - Changed `job.completed_at` → `job.end_time` (line 289)
  - Error resolved: "type object 'ScrapingJob' has no attribute 'created_at'"

- Fixed user details modal 500 error
  - Changed `job.target_usernames` → `job.usernames` (line 285)
  - Changed `job.reels_scraped` → `len(job.reels)` (line 286)
  - Error resolved: "'ScrapingJob' object has no attribute 'target_usernames'"

- Fixed average reels calculation in statistics
  - Replaced invalid `func.avg(models.ScrapingJob.reels_scraped)` query
  - Implemented proper calculation using joined query to `ScrapedReel` table
  - Now correctly calculates: total_reels / completed_jobs

**Database Schema Alignment:**
- Corrected all field references to match actual database schema:
  - ✅ `usernames` (not `target_usernames`)
  - ✅ `start_time` (not `created_at`)
  - ✅ `end_time` (not `completed_at`)
  - ✅ `len(job.reels)` for scraped count (no direct `reels_scraped` field)

**Files Modified:**
- `Backend/admin_routes.py` - Fixed 7 incorrect field references
- `CLAUDE.md` - Documentation updates

**Impact:**
- ✅ Admin dashboard now loads without errors
- ✅ System overview statistics display correctly
- ✅ User details modal works properly
- ✅ All admin panel features fully operational

---

### Version 3.0.1 (December 24, 2025)

**UI/UX Improvements:**
- Redesigned "Add Instagram Account" button
  - Now matches "Export CSV" button design from user dashboard
  - Added professional SVG plus icon
  - Uses proper `btn btn-primary` CSS classes
  - Purple background (#8b5cf6) with smooth hover effects

- Improved "Add Instagram Account" Modal Form
  - Increased width from 500px to 650px (no more content overflow)
  - Added `.modal-body` wrapper for proper structure
  - Replaced inline styles with proper CSS classes
  - Fixed close button to use `.modal-close` class
  - Added clean form labels with `.form-label` class
  - Added helper text with `.form-hint` class
  - Improved checkbox layout with `.checkbox-label` class
  - Professional button alignment (Cancel left, Create Account right)

- Removed INFO Section
  - Deleted useless "API Endpoint: localhost:8080" section from user dashboard
  - Cleaned up unused CSS

**Bug Fixes:**
- Fixed activity logging error in Instagram account creation
  - Changed `crud.log_activity()` to `crud.create_activity_log()`
  - Error: "module 'crud' has no attribute 'log_activity'" is now resolved
  - Activity logs now properly record `account_created` events

**CSS Improvements:**
- Added 8 new CSS classes for consistent styling:
  - `.form-label` - Form field labels
  - `.form-hint` - Helper text below inputs
  - `.btn.btn-primary` - Primary action buttons
  - `.btn.btn-secondary` - Secondary action buttons
  - `.error-message` - Error message styling
  - `.modal-footer` - Modal footer with button layout
  - `.checkbox-label` - Checkbox with label styling
- Removed conflicting modal-specific CSS overrides
- All styles now use CSS custom properties (variables)

**Documentation:**
- Updated admin panel guide with new design features
- Added troubleshooting entry for log_activity error
- Updated version number to 3.0.1
- Added recent updates section at top of documentation

**Files Modified:**
- `Frontend/admin/components/accounts.js` - Button and modal redesign
- `Frontend/admin/admin.css` - New CSS classes and cleanup
- `Frontend/index.html` - Removed INFO section
- `Frontend/styles.css` - Removed INFO section CSS
- `Backend/app.py` - Fixed activity logging function name
- `CLAUDE.md` - Documentation updates

### Version 3.0 (December 18, 2025)

**Phase 3 Complete:**
- Admin panel with user management
- Instagram account pool monitoring
- Activity logs viewer
- System statistics dashboard
- Database indexes and views for performance

---

## 📄 License

This project is for educational purposes. Please respect Instagram's Terms of Service when using this tool.

**Disclaimer:** This tool is not affiliated with Instagram. Use responsibly and at your own risk.

---

## 📞 Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review API documentation at `http://localhost:8080/docs`
3. Check Docker logs: `docker logs instagram_scraper_db`
4. Check application logs in terminal
5. Open an issue on GitHub

---

## 🎉 Credits

**Built with:**
- FastAPI (backend framework)
- PostgreSQL (database)
- Vanilla JavaScript (frontend)
- Chart.js (admin panel charts)
- Docker (PostgreSQL container)

**Created with Claude Code** 🤖

---

**Version:** 3.0
**Last Updated:** December 2025
**Status:** Production Ready ✅

