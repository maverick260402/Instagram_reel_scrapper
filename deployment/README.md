# Deployment Guide - Instagram Reel Scraper

This directory contains all deployment scripts and configuration files for deploying the Instagram Reel Scraper to a production VPS server.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Files Overview](#files-overview)
- [Initial Server Setup](#initial-server-setup)
- [GitHub Configuration](#github-configuration)
- [Manual Deployment](#manual-deployment)
- [Automated Deployment](#automated-deployment)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🚀 Quick Start

### Prerequisites

- Ubuntu 20.04+ or Debian 11+ VPS server
- Root or sudo access
- GitHub repository
- Domain name (optional but recommended)

### 3-Step Deployment

```bash
# 1. Initial server setup (run once on VPS)
sudo bash deployment/setup-server.sh

# 2. Configure GitHub Secrets (in GitHub repository settings)
# See "GitHub Configuration" section below

# 3. Push to main branch - automatic deployment!
git push origin main
```

---

## 📁 Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| **setup-server.sh** | One-time VPS initialization | First deployment only |
| **deploy.sh** | Manual deployment script | Manual deployments or testing |
| **run-migrations.sh** | Database migration runner | Automatic during deployment |
| **docker-compose.prod.yml** | PostgreSQL production config | Managed by setup script |
| **instagram-scraper.service** | Systemd service definition | Installed by setup script |
| **.env.production.example** | Production environment template | Copy and configure |
| **README.md** | This file | Documentation |
| **SETUP.md** | Detailed setup guide | Step-by-step instructions |

---

## 🔧 Initial Server Setup

### Step 1: Prepare Your VPS

1. **SSH to your server:**
   ```bash
   ssh your-user@your-vps-ip
   ```

2. **Clone your repository:**
   ```bash
   cd /tmp
   git clone https://github.com/your-username/Instagram_reel_scrapper.git
   cd Instagram_reel_scrapper
   ```

3. **Run setup script:**
   ```bash
   sudo bash deployment/setup-server.sh
   ```

   This script will:
   - Update system packages
   - Install Python 3.11
   - Install Docker and Docker Compose
   - Create application user (`instagram-scraper`)
   - Set up directory structure at `/opt/instagram-scraper`
   - Configure PostgreSQL container
   - Install systemd service
   - Configure firewall

### Step 2: Configure Environment

1. **Create production .env file:**
   ```bash
   cd /opt/instagram-scraper
   sudo cp deployment/.env.production.example .env
   sudo nano .env
   ```

2. **Fill in required values:**
   ```env
   # Generate SECRET_KEY
   openssl rand -hex 32

   # Update .env with:
   SECRET_KEY=<generated-key>
   DATABASE_URL=postgresql://scraper_user:YOUR_STRONG_PASSWORD@localhost:5432/instagram_scraper
   ALLOWED_ORIGINS=https://yourdomain.com
   POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD
   ```

3. **Set correct permissions:**
   ```bash
   sudo chown instagram-scraper:instagram-scraper .env
   sudo chmod 600 .env
   ```

### Step 3: Initial Manual Deployment

1. **Clone repository to application directory:**
   ```bash
   sudo su - instagram-scraper
   cd /opt/instagram-scraper
   git clone https://github.com/your-username/Instagram_reel_scrapper.git .
   ```

2. **Install Python dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r Backend/requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   cd deployment
   chmod +x run-migrations.sh
   ./run-migrations.sh
   ```

4. **Start the application:**
   ```bash
   sudo systemctl start instagram-scraper
   sudo systemctl status instagram-scraper
   ```

5. **Verify it's working:**
   ```bash
   curl http://localhost:8080/docs
   ```

   You should see the FastAPI documentation page.

---

## 🔐 GitHub Configuration

### Step 1: Generate SSH Key for Deployment

On your **local machine**, generate a dedicated SSH key:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/instagram_scraper_deploy
```

### Step 2: Add Public Key to VPS

```bash
# Copy public key to VPS
cat ~/.ssh/instagram_scraper_deploy.pub | ssh your-user@your-vps-ip 'sudo -u instagram-scraper tee -a /home/instagram-scraper/.ssh/authorized_keys'
```

### Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value | How to Get |
|-------------|-------|-----------|
| **VPS_HOST** | Your VPS IP or domain | `hostname -I` on VPS |
| **VPS_USER** | `instagram-scraper` | Fixed value |
| **VPS_SSH_KEY** | Private SSH key | `cat ~/.ssh/instagram_scraper_deploy` |
| **VPS_PORT** | `22` | SSH port (usually 22) |
| **DATABASE_URL** | PostgreSQL connection | From `.env` file on VPS |
| **SECRET_KEY** | JWT secret key | From `.env` file on VPS |
| **ALLOWED_ORIGINS** | Your domain(s) | From `.env` file on VPS |

### Step 4: Test GitHub Actions

1. **Push a small change to main branch:**
   ```bash
   git commit --allow-empty -m "Test CI/CD pipeline"
   git push origin main
   ```

2. **Monitor deployment:**
   - Go to GitHub → Actions tab
   - Watch the workflow run
   - Check for green checkmarks ✓

3. **Verify on VPS:**
   ```bash
   ssh your-vps-ip
   sudo systemctl status instagram-scraper
   curl http://localhost:8080/docs
   ```

---

## 🔨 Manual Deployment

For manual deployments or troubleshooting:

```bash
# SSH to VPS
ssh instagram-scraper@your-vps-ip

# Navigate to app directory
cd /opt/instagram-scraper

# Run deployment script
./deployment/deploy.sh
```

The script will:
1. Create backup of current code
2. Pull latest changes from GitHub
3. Install/update dependencies
4. Run database migrations
5. Restart the application
6. Perform health check
7. Rollback on failure

---

## ⚙️ Automated Deployment

### How It Works

GitHub Actions automatically deploys when you push to the `main` branch:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Developer pushes code to main branch                        │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. GitHub Actions triggers CI/CD workflow                      │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. CI Stage (on GitHub's servers):                             │
│    - Run tests (test_phase1.py, test_phase2.py, test_phase3.py)│
│    - If tests fail → STOP (no deployment)                      │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. CD Stage (on your VPS):                                     │
│    - SSH to VPS server                                          │
│    - Pull latest code                                           │
│    - Install dependencies                                       │
│    - Run migrations                                             │
│    - Restart service                                            │
│    - Health check                                               │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Deployment complete! 🎉                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Files

- **`.github/workflows/ci-cd.yml`** - Main CI/CD pipeline (tests + deployment)
- **`.github/workflows/test-only.yml`** - PR testing only (no deployment)

### Deployment Triggers

| Branch | Event | Tests Run? | Deploy? |
|--------|-------|------------|---------|
| main | Push | Yes | Yes (if tests pass) |
| main | PR | Yes | No |
| develop | Push | Yes | No |
| develop | PR | Yes | No |
| feature/* | Push | Yes | No |
| feature/* | PR | Yes | No |

---

## 🐛 Troubleshooting

### Deployment Failed - Tests Failed

**Symptom:** GitHub Actions shows red X, deployment didn't happen

**Solution:**
1. Check GitHub Actions logs
2. Fix failing tests locally
3. Push fix to main branch
4. Deployment will retry automatically

### Deployment Failed - SSH Connection Error

**Symptom:** "Permission denied" or "Connection refused" during deployment

**Solution:**
```bash
# Verify SSH key is added to VPS
ssh -i ~/.ssh/instagram_scraper_deploy instagram-scraper@your-vps-ip

# If fails, re-add public key:
cat ~/.ssh/instagram_scraper_deploy.pub | ssh your-user@your-vps-ip 'sudo -u instagram-scraper tee -a /home/instagram-scraper/.ssh/authorized_keys'
```

### Application Not Starting

**Symptom:** Systemd service fails to start

**Solution:**
```bash
# Check service status
sudo systemctl status instagram-scraper

# View error logs
sudo journalctl -u instagram-scraper -n 100

# Common issues:
# 1. Missing .env file
sudo ls -la /opt/instagram-scraper/.env

# 2. Database not running
docker ps | grep postgres

# 3. Port already in use
sudo lsof -i :8080

# 4. Permission issues
sudo chown -R instagram-scraper:instagram-scraper /opt/instagram-scraper
```

### Database Connection Error

**Symptom:** "could not connect to server: Connection refused"

**Solution:**
```bash
# Check PostgreSQL container
docker ps

# If not running, start it
cd /opt/instagram-scraper/deployment
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker logs instagram_scraper_db_prod
```

### Health Check Failed

**Symptom:** Deployment script reports health check failure

**Solution:**
```bash
# Manual health check
curl -v http://localhost:8080/docs

# If fails, check app logs
sudo journalctl -u instagram-scraper -f

# Restart service
sudo systemctl restart instagram-scraper
```

### Rollback to Previous Version

**Symptom:** New deployment broke something

**Solution:**
```bash
# SSH to VPS
ssh instagram-scraper@your-vps-ip
cd /opt/instagram-scraper

# Find previous commit
git log --oneline -5

# Checkout previous version
git checkout <previous-commit-hash>

# Restart service
sudo systemctl restart instagram-scraper

# Or use backup
cd backups
ls -lt  # Find latest backup
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/instagram-scraper
sudo systemctl restart instagram-scraper
```

---

## 🔧 Maintenance

### View Application Logs

```bash
# Real-time logs
sudo journalctl -u instagram-scraper -f

# Last 100 lines
sudo journalctl -u instagram-scraper -n 100

# Application log file
tail -f /opt/instagram-scraper/logs/app.log

# Error log file
tail -f /opt/instagram-scraper/logs/error.log
```

### Database Backup

```bash
# Manual backup
docker exec instagram_scraper_db_prod pg_dump -U scraper_user instagram_scraper > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i instagram_scraper_db_prod psql -U scraper_user instagram_scraper < backup_20250108.sql
```

### Update Dependencies

```bash
# SSH to VPS
ssh instagram-scraper@your-vps-ip
cd /opt/instagram-scraper

# Activate venv
source venv/bin/activate

# Update specific package
pip install --upgrade fastapi

# Update all packages
pip install --upgrade -r Backend/requirements.txt

# Restart service
sudo systemctl restart instagram-scraper
```

### Check Migration Status

```bash
cd /opt/instagram-scraper/deployment
./run-migrations.sh status
```

### Reset Migrations (Dangerous!)

```bash
cd /opt/instagram-scraper/deployment
./run-migrations.sh reset
./run-migrations.sh run
```

### Restart Services

```bash
# Restart application
sudo systemctl restart instagram-scraper

# Restart database
docker restart instagram_scraper_db_prod

# Restart both
sudo systemctl restart instagram-scraper && docker restart instagram_scraper_db_prod
```

### Monitor System Resources

```bash
# System resources
htop

# Disk usage
df -h

# Docker resources
docker stats

# Application port
sudo netstat -tulpn | grep 8080
```

---

## 📊 Useful Commands

### Service Management

```bash
# Start service
sudo systemctl start instagram-scraper

# Stop service
sudo systemctl stop instagram-scraper

# Restart service
sudo systemctl restart instagram-scraper

# Check status
sudo systemctl status instagram-scraper

# Enable on boot
sudo systemctl enable instagram-scraper

# Disable on boot
sudo systemctl disable instagram-scraper
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it instagram_scraper_db_prod psql -U scraper_user -d instagram_scraper

# List databases
docker exec -it instagram_scraper_db_prod psql -U scraper_user -c "\l"

# List tables
docker exec -it instagram_scraper_db_prod psql -U scraper_user -d instagram_scraper -c "\dt"

# Run SQL query
docker exec -it instagram_scraper_db_prod psql -U scraper_user -d instagram_scraper -c "SELECT COUNT(*) FROM users;"
```

### Git Operations

```bash
# Pull latest code
cd /opt/instagram-scraper
git pull origin main

# Check current commit
git rev-parse HEAD

# View recent commits
git log --oneline -10

# Reset to specific commit
git reset --hard <commit-hash>
```

---

## 🔗 Related Documentation

- [SETUP.md](./SETUP.md) - Detailed step-by-step setup guide
- [../CLAUDE.md](../CLAUDE.md) - Complete application documentation
- [../README.md](../README.md) - Project overview

---

## 📞 Support

If you encounter issues:

1. Check logs: `sudo journalctl -u instagram-scraper -n 100`
2. Check database: `docker logs instagram_scraper_db_prod`
3. Check GitHub Actions logs in the Actions tab
4. Review this troubleshooting guide

---

**Version:** 1.0.0
**Last Updated:** January 2026
**Maintained by:** Your Team
