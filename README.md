# Instagram Reel Scraper

A full-stack web application for scraping Instagram reel metadata with multi-user support, credit-based usage limits, intelligent account rotation, and admin controls.

## Quick Start

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Install dependencies
cd Backend && pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
psql -U scraper_user -d instagram_scraper -f migrations/001_multi_user_system.sql
psql -U scraper_user -d instagram_scraper -f migrations/002_phase3_indexes_views.sql

# 5. Start server
python app.py
```

**User Dashboard:** http://localhost:8080
**Admin Panel:** http://localhost:8080/static/admin/index.html
**API Docs:** http://localhost:8080/docs

## Features

| Feature | Description |
|---------|-------------|
| Multi-User System | Credit-based quotas (2000 reels/day default) |
| Account Rotation | Intelligent least-used Instagram account selection |
| Admin Panel | User management, account monitoring, statistics |
| Cookie Management | API for remote cookie updates |
| Daily Resets | Automatic credit reset at midnight IST |
| Analytics | Filter, sort, and export scraped data |

## Tech Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, JWT, APScheduler
- **Frontend:** Vanilla JavaScript, HTML5/CSS3, Chart.js
- **Database:** PostgreSQL 15+ (8 tables, 9 views)

## Database Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts with credit system |
| `instagram_accounts` | Instagram account pool with cookies |
| `scraping_jobs` | Job tracking with progress |
| `scraped_reels` | Individual reel metadata |
| `user_groups` | Username group management |
| `activity_logs` | Comprehensive event logging |
| `api_keys` | API authentication |
| `admin_users` | Admin panel authentication |

## Key API Endpoints

```
POST /api/auth/signup          # Register user
POST /api/auth/login           # User login
POST /api/scrape               # Start scraping job
GET  /api/job/{job_id}         # Check job status
GET  /api/analytics            # Get scraped data
POST /api/admin/instagram-accounts/{id}/cookies  # Update cookies
```

## Default Credentials

**Admin Panel:**
- Username: `admin`
- Password: `admin123`
- **Change immediately in production!**

## Documentation

For complete documentation including installation, API reference, troubleshooting, and security:

**See: [CLAUDE.md](CLAUDE.md)**

## Version

**Version:** 3.0.4
**Status:** Production Ready

---

*Created with Claude Code*
