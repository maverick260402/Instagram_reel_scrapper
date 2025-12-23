# Instagram Reel Scraper

A full-stack web application for scraping Instagram reel metadata with enterprise-grade features including multi-user support, credit-based usage limits, intelligent account rotation, and comprehensive admin controls.

## 🚀 Quick Start

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Install dependencies
cd Backend
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
psql -U scraper_user -d instagram_scraper -f migrations/001_multi_user_system.sql
psql -U scraper_user -d instagram_scraper -f migrations/002_phase3_indexes_views.sql

# 5. Start server
python app.py

# 6. Open browser
# Navigate to: http://localhost:8080
```

## ✨ Key Features

- **Multi-User System** - Credit-based quotas (2000 reels/day default)
- **Instagram Account Rotation** - Intelligent least-used account selection
- **Admin Panel** - User management, account monitoring, system statistics
- **Cookie Management** - Automated refresh every 5 days
- **Daily Resets** - Automatic credit and counter reset at midnight
- **Analytics Dashboard** - Filter, sort, and export scraped data
- **Real-time Tracking** - Job progress monitoring

## 🛠 Tech Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, JWT, APScheduler
- **Frontend:** Vanilla JavaScript, HTML5/CSS3, Chart.js
- **Database:** PostgreSQL 15+ (8 tables, 9 views)

## 📚 Complete Documentation

For complete documentation including:
- Detailed installation guide
- Database schema (all 8 tables with field details)
- Phase 1, 2, 3 implementation guides
- Full API documentation
- User dashboard guide
- Admin panel guide
- Configuration options
- Troubleshooting
- Security best practices

**See:** [claude.md](claude.md)

## 🗄 Database Schema (Summary)

**8 Tables:**
- `users` - User accounts with credit system
- `instagram_accounts` - Instagram account pool with cookies
- `scraping_jobs` - Job tracking with progress
- `scraped_reels` - Individual reel metadata
- `user_groups` - Username group management
- `activity_logs` - Comprehensive event logging
- `api_keys` - API authentication for cookie updates
- `admin_users` - Admin panel authentication

**9 Views:**
- Pre-computed statistics for analytics

## 🎯 User Access

**User Dashboard:** http://localhost:8080
- Sign up, login, manage groups
- Start scraping jobs
- View analytics and export data

**Admin Panel:** http://localhost:8080/static/admin/index.html
- Default login: admin / admin123 (CHANGE THIS!)
- Manage users and credit limits
- Monitor Instagram accounts
- View activity logs and statistics

## 📡 API Documentation

Interactive API docs: http://localhost:8080/docs

**Key Endpoints:**
- `POST /api/auth/signup` - Register user
- `POST /api/auth/login` - User login
- `POST /api/scrape` - Start scraping job (with credit check & rotation)
- `GET /api/job/{job_id}` - Check job status
- `GET /api/analytics` - Get scraped data with filters
- `POST /api/admin/instagram-accounts/{id}/cookies` - Update cookies

## 🔐 Security

- JWT authentication with 7-day expiration
- Bcrypt password hashing
- API key authentication for admin endpoints
- Rate limiting protection
- CORS configuration
- SQL injection prevention via ORM

## 🐛 Common Issues

**Credit meter not updating?**
- Fixed! Was using wrong token key (`access_token` instead of `authToken`)

**No reels scraped?**
- Check Instagram account cookies are valid
- Use remote_cookie_updater.py to refresh

**Database connection failed?**
- Verify PostgreSQL is running: `docker ps`
- Start if needed: `docker start instagram_scraper_db`

See [Troubleshooting](claude.md#troubleshooting) in claude.md for more.

## 📊 System Architecture

### Credit System Flow
1. User requests scrape (e.g., 20 reels)
2. System checks credits (does user have 20?)
3. System selects least-used Instagram account
4. Job starts with linked Instagram account
5. For each scraped reel: deduct 1 credit
6. Update Instagram account usage counter
7. Log activity

### Daily Reset (Midnight)
- All user credits reset to 0
- All Instagram account daily counters reset to 0
- Logged in activity_logs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

## 📄 License

For educational purposes. Respect Instagram's Terms of Service.

---

**Version:** 3.0 (Phase 3 Complete)
**Status:** Production Ready ✅

**For complete documentation, see [claude.md](claude.md)**
