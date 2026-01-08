# Instagram Reel Scraper

![CI/CD Status](https://github.com/YOUR-USERNAME/Instagram_reel_scrapper/actions/workflows/ci-cd.yml/badge.svg)
![Tests](https://github.com/YOUR-USERNAME/Instagram_reel_scrapper/actions/workflows/test-only.yml/badge.svg)

A full-stack web application for scraping Instagram reel metadata with enterprise-grade features including multi-user support, credit-based usage limits, intelligent account rotation, and comprehensive admin controls.

**✨ Now with automated CI/CD deployment via GitHub Actions!**

## 🚀 Quick Start

### Local Development

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

### Production Deployment (VPS with CI/CD)

```bash
# 1. Run automated setup on your VPS
sudo bash deployment/setup-server.sh

# 2. Configure GitHub Secrets (see deployment/SETUP.md)

# 3. Push to main branch - automatic deployment!
git push origin main
```

**📖 Complete deployment guide:** [deployment/SETUP.md](deployment/SETUP.md)

## ✨ Key Features

### Application Features
- **Multi-User System** - Credit-based quotas (2000 reels/day default)
- **Instagram Account Rotation** - Intelligent least-used account selection
- **Admin Panel** - User management, account monitoring, system statistics
- **Cookie Management** - Automated refresh every 5 days
- **Daily Resets** - Automatic credit and counter reset at midnight
- **Analytics Dashboard** - Filter, sort, and export scraped data
- **Real-time Tracking** - Job progress monitoring

### DevOps Features (NEW!)
- **🚀 CI/CD Pipeline** - Automated testing and deployment via GitHub Actions
- **✅ Automated Testing** - Runs Phase 1, 2, 3 tests on every push
- **📦 Docker Database** - PostgreSQL in production-ready Docker container
- **🔄 Zero-Downtime Deploys** - Systemd service with health checks
- **🔐 Secure Deployment** - SSH key authentication, environment secrets
- **📊 Deployment Monitoring** - GitHub Actions logs and status badges
- **🔙 Automatic Rollback** - Restores previous version on failure

## 🛠 Tech Stack

### Application
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, JWT, APScheduler
- **Frontend:** Vanilla JavaScript, HTML5/CSS3, Chart.js
- **Database:** PostgreSQL 15+ (8 tables, 9 views)

### DevOps & Infrastructure
- **CI/CD:** GitHub Actions
- **Deployment:** Systemd service on Linux VPS
- **Database Container:** Docker Compose with PostgreSQL 15
- **Web Server:** Uvicorn (with optional Nginx reverse proxy)
- **Migrations:** Automated SQL migration runner
- **Monitoring:** Systemd logs, health checks

## 📚 Complete Documentation

### Application Documentation
For application features, database schema, and API documentation:
- Detailed installation guide
- Database schema (all 8 tables with field details)
- Phase 1, 2, 3 implementation guides
- Full API documentation
- User dashboard guide
- Admin panel guide
- Configuration options
- Troubleshooting
- Security best practices

**See:** [CLAUDE.md](CLAUDE.md)

### Deployment Documentation
For CI/CD setup and production deployment:
- **Quick Start:** [deployment/README.md](deployment/README.md)
- **Step-by-Step Setup:** [deployment/SETUP.md](deployment/SETUP.md)
- Server setup scripts, systemd configuration, migration runner
- GitHub Actions workflows, secrets configuration
- Troubleshooting deployment issues

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

## 🚀 CI/CD Pipeline

This project uses GitHub Actions for automated testing and deployment.

### How It Works

```
Push to main → Run tests → Deploy to VPS → Health check → ✅ Live!
```

### Deployment Flow

1. **Developer pushes code** to `main` branch
2. **GitHub Actions triggers** automatically
3. **CI Stage:** Runs all unit tests (Phase 1, 2, 3)
   - If tests fail → Deployment STOPS ❌
4. **CD Stage:** Deploys to production VPS
   - SSH to server
   - Pull latest code
   - Install dependencies
   - Run database migrations
   - Restart systemd service
   - Perform health check
   - Rollback if health check fails
5. **Deployment complete** ✅

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI/CD Pipeline** | Push to `main` | Full testing + deployment |
| **Tests Only** | Pull requests | Testing without deployment |

### Setting Up CI/CD

**Prerequisites:**
- VPS server (Ubuntu/Debian)
- GitHub repository
- SSH access

**Quick Setup:**
```bash
# 1. On your VPS
sudo bash deployment/setup-server.sh

# 2. Configure GitHub Secrets (7 required)
# See deployment/SETUP.md for details

# 3. Push to main - auto-deploy!
git push origin main
```

**📖 Complete setup guide:** [deployment/SETUP.md](deployment/SETUP.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and test locally
4. Push and create pull request (tests run automatically!)
5. After approval, merge to main (auto-deploys to production!)

## 📄 License

For educational purposes. Respect Instagram's Terms of Service.

---

**Version:** 3.1 (Phase 3 + CI/CD Complete)
**Status:** Production Ready ✅ | CI/CD Enabled 🚀

### 📖 Documentation Links
- **Application Guide:** [CLAUDE.md](CLAUDE.md)
- **Deployment Guide:** [deployment/SETUP.md](deployment/SETUP.md)
- **API Docs:** http://localhost:8080/docs (when running)

### 🔗 Quick Links
- [Setup Server](deployment/setup-server.sh) - One-time VPS setup
- [Deploy Script](deployment/deploy.sh) - Manual deployment
- [CI/CD Workflow](.github/workflows/ci-cd.yml) - GitHub Actions config
- [Environment Template](deployment/.env.production.example) - Production config

**Built with Claude Code** 🤖
