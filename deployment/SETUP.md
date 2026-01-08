# Complete Setup Guide - Instagram Reel Scraper CI/CD

This guide provides detailed step-by-step instructions for setting up CI/CD for the Instagram Reel Scraper project.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ VPS server running Ubuntu 20.04+ or Debian 11+
- ✅ Root or sudo access to the server
- ✅ GitHub repository with the code
- ✅ SSH access to your VPS
- ✅ Domain name (optional but recommended)
- ✅ Basic knowledge of Linux command line

---

## Part 1: VPS Server Setup (One-Time)

### Step 1: Access Your VPS

```bash
# SSH to your server
ssh your-username@your-vps-ip

# Example:
ssh root@123.45.67.89
# or
ssh ubuntu@myserver.com
```

### Step 2: Clone Repository

```bash
# Navigate to temporary directory
cd /tmp

# Clone your repository
git clone https://github.com/YOUR-USERNAME/Instagram_reel_scrapper.git
cd Instagram_reel_scrapper
```

### Step 3: Run Automated Setup

```bash
# Make script executable
chmod +x deployment/setup-server.sh

# Run setup script with sudo
sudo bash deployment/setup-server.sh
```

**What this script does:**
1. Updates system packages
2. Installs Python 3.11
3. Installs Docker and Docker Compose
4. Creates `instagram-scraper` user
5. Sets up `/opt/instagram-scraper` directory
6. Creates Python virtual environment
7. Starts PostgreSQL Docker container
8. Installs systemd service
9. Configures firewall (UFW)

**Expected output:**
```
==================================
Instagram Reel Scraper - VPS Server Setup
==================================

Continue? (y/n): y

==================================
Updating System Packages
==================================
✓ System packages updated

==================================
Installing Python 3.11
==================================
✓ Python 3.11 installed

... (more output) ...

==================================
Setup Complete!
==================================
```

### Step 4: Configure Production Environment

```bash
# Switch to application directory
cd /opt/instagram-scraper

# Copy environment template
sudo cp deployment/.env.production.example .env

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
echo "Generated SECRET_KEY: $SECRET_KEY"

# Generate strong database password
DB_PASSWORD=$(openssl rand -base64 24)
echo "Generated DB password: $DB_PASSWORD"

# Edit .env file
sudo nano .env
```

**Update these values in `.env`:**

```env
# Replace these values:
DATABASE_URL=postgresql://scraper_user:YOUR_DB_PASSWORD@localhost:5432/instagram_scraper
SECRET_KEY=YOUR_GENERATED_SECRET_KEY
ALLOWED_ORIGINS=https://yourdomain.com,http://yourdomain.com

# Also update:
POSTGRES_PASSWORD=YOUR_DB_PASSWORD
ENVIRONMENT=production
DEBUG=False
```

Save the file (Ctrl+X, then Y, then Enter).

**Set correct permissions:**
```bash
sudo chown instagram-scraper:instagram-scraper .env
sudo chmod 600 .env
```

### Step 5: Clone Code to Application Directory

```bash
# Switch to instagram-scraper user
sudo su - instagram-scraper

# Navigate to app directory
cd /opt/instagram-scraper

# Clone repository
git clone https://github.com/YOUR-USERNAME/Instagram_reel_scrapper.git .

# Verify files are there
ls -la
```

You should see:
- Backend/
- Frontend/
- deployment/
- .env
- venv/

### Step 6: Install Python Dependencies

```bash
# Still as instagram-scraper user
cd /opt/instagram-scraper

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r Backend/requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 sqlalchemy-2.0.36 ...
```

### Step 7: Start PostgreSQL Database

```bash
# Exit instagram-scraper user (back to your user)
exit

# Start PostgreSQL container
cd /opt/instagram-scraper/deployment
sudo docker-compose -f docker-compose.prod.yml up -d

# Verify it's running
docker ps
```

You should see:
```
CONTAINER ID   IMAGE                COMMAND                  STATUS
abc123def456   postgres:15-alpine   "docker-entrypoint.s…"   Up 10 seconds
```

### Step 8: Run Database Migrations

```bash
# Switch back to instagram-scraper user
sudo su - instagram-scraper
cd /opt/instagram-scraper/deployment

# Make migration script executable
chmod +x run-migrations.sh

# Run migrations
./run-migrations.sh
```

**Expected output:**
```
==================================
Running Database Migrations
==================================

ℹ Found 3 migration file(s)

ℹ Running migration: 000_initial_schema.sql
✓ 000_initial_schema.sql completed successfully
✓ Marked 000_initial_schema.sql as applied

ℹ Running migration: 001_multi_user_system.sql
✓ 001_multi_user_system.sql completed successfully
✓ Marked 001_multi_user_system.sql as applied

ℹ Running migration: 002_phase3_indexes_views.sql
✓ 002_phase3_indexes_views.sql completed successfully
✓ Marked 002_phase3_indexes_views.sql as applied

==================================
Migration Summary
==================================
Total migrations: 3
Applied: 3
Skipped: 0
Failed: 0

✓ All migrations completed successfully
```

### Step 9: Start the Application

```bash
# Exit instagram-scraper user
exit

# Start systemd service
sudo systemctl start instagram-scraper

# Check status
sudo systemctl status instagram-scraper
```

**Expected output:**
```
● instagram-scraper.service - Instagram Reel Scraper - FastAPI Application
     Loaded: loaded (/etc/systemd/system/instagram-scraper.service; enabled)
     Active: active (running) since Wed 2026-01-08 10:30:00 UTC; 5s ago
```

### Step 10: Verify Application is Running

```bash
# Health check
curl http://localhost:8080/docs

# You should see HTML output with "FastAPI" and "Swagger UI"
```

If you see HTML, the application is running! ✅

### Step 11: Enable Service on Boot

```bash
# Enable service to start automatically on reboot
sudo systemctl enable instagram-scraper

# Verify
sudo systemctl is-enabled instagram-scraper
# Should output: enabled
```

---

## Part 2: GitHub Actions Configuration

### Step 1: Generate SSH Key for Deployment

**On your LOCAL machine** (not VPS):

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/instagram_scraper_deploy

# When prompted for passphrase, press Enter (no passphrase)
```

You'll see:
```
Generating public/private ed25519 key pair.
Your identification has been saved in /home/you/.ssh/instagram_scraper_deploy
Your public key has been saved in /home/you/.ssh/instagram_scraper_deploy.pub
```

### Step 2: Add Public Key to VPS

**Still on your LOCAL machine:**

```bash
# Display public key
cat ~/.ssh/instagram_scraper_deploy.pub

# Copy the output (entire line starting with ssh-ed25519)
```

**On your VPS:**

```bash
# Switch to instagram-scraper user
sudo su - instagram-scraper

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add public key to authorized_keys
nano ~/.ssh/authorized_keys

# Paste the public key on a new line, save and exit

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys

# Exit back to your user
exit
```

### Step 3: Test SSH Connection

**On your LOCAL machine:**

```bash
# Test SSH connection with the new key
ssh -i ~/.ssh/instagram_scraper_deploy instagram-scraper@YOUR_VPS_IP

# If successful, you should be logged in as instagram-scraper user
# Type 'exit' to logout
```

### Step 4: Get Private SSH Key

**On your LOCAL machine:**

```bash
# Display private key (for GitHub Secrets)
cat ~/.ssh/instagram_scraper_deploy

# Copy the ENTIRE output including:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... (many lines) ...
# -----END OPENSSH PRIVATE KEY-----
```

**⚠️ IMPORTANT:** Keep this private key secure! Never share it publicly.

### Step 5: Get VPS Information

**On your VPS:**

```bash
# Get VPS IP address
hostname -I | awk '{print $1}'

# Get database URL from .env
sudo grep DATABASE_URL /opt/instagram-scraper/.env

# Get SECRET_KEY from .env
sudo grep SECRET_KEY /opt/instagram-scraper/.env

# Get ALLOWED_ORIGINS from .env
sudo grep ALLOWED_ORIGINS /opt/instagram-scraper/.env
```

**Copy these values - you'll need them for GitHub Secrets.**

### Step 6: Configure GitHub Secrets

1. **Go to your GitHub repository**

2. **Navigate to Settings → Secrets and variables → Actions**

3. **Click "New repository secret"**

4. **Add each of these secrets:**

| Secret Name | Value | Example |
|-------------|-------|---------|
| `VPS_HOST` | Your VPS IP address | `123.45.67.89` |
| `VPS_USER` | `instagram-scraper` | `instagram-scraper` |
| `VPS_SSH_KEY` | Private SSH key (entire content) | `-----BEGIN OPENSSH...` |
| `VPS_PORT` | `22` | `22` |
| `DATABASE_URL` | From .env file | `postgresql://scraper_user:...` |
| `SECRET_KEY` | From .env file | `abc123def456...` |
| `ALLOWED_ORIGINS` | From .env file | `https://yourdomain.com` |

**For VPS_SSH_KEY:**
- Click "New repository secret"
- Name: `VPS_SSH_KEY`
- Value: Paste the ENTIRE private key including `-----BEGIN` and `-----END` lines
- Click "Add secret"

Repeat for all 7 secrets.

### Step 7: Verify GitHub Actions is Enabled

1. **Go to your repository → Actions tab**

2. **If you see "Workflows disabled":**
   - Click "I understand my workflows, go ahead and enable them"

3. **You should see:**
   - "CI/CD Pipeline" workflow
   - "Tests Only" workflow

---

## Part 3: Test the CI/CD Pipeline

### Step 1: Test Deployment with Empty Commit

**On your LOCAL machine:**

```bash
# Navigate to your repository
cd ~/path/to/Instagram_reel_scrapper

# Ensure you're on main branch
git checkout main

# Create empty commit to trigger deployment
git commit --allow-empty -m "Test CI/CD pipeline"

# Push to GitHub
git push origin main
```

### Step 2: Monitor GitHub Actions

1. **Go to GitHub → Actions tab**

2. **You should see a workflow running:**
   - "Test CI/CD pipeline" commit
   - Click on it to see details

3. **Watch the progress:**
   - "Run Tests" job should run first
   - If tests pass, "Deploy to VPS" job will run
   - Both should show green checkmarks ✅

### Step 3: Verify Deployment on VPS

**SSH to your VPS:**

```bash
# Check service status
sudo systemctl status instagram-scraper

# Check latest commit
cd /opt/instagram-scraper
git log -1 --oneline

# Health check
curl http://localhost:8080/docs
```

If everything works, you should see:
- Service is active (running)
- Latest commit matches what you pushed
- Health check returns HTML

**Congratulations! Your CI/CD pipeline is working! 🎉**

---

## Part 4: Day-to-Day Usage

### Making Code Changes

```bash
# On your local machine
cd ~/path/to/Instagram_reel_scrapper

# Create a new branch for your changes
git checkout -b feature/my-new-feature

# Make your changes to the code
nano Backend/app.py

# Commit changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/my-new-feature

# Create Pull Request on GitHub
# Tests will run automatically

# After PR is approved and merged to main
# Deployment happens automatically!
```

### Viewing Logs

```bash
# SSH to VPS
ssh instagram-scraper@YOUR_VPS_IP

# View service logs (real-time)
sudo journalctl -u instagram-scraper -f

# View last 100 log entries
sudo journalctl -u instagram-scraper -n 100

# View application log file
tail -f /opt/instagram-scraper/logs/app.log

# View error log file
tail -f /opt/instagram-scraper/logs/error.log
```

### Restarting the Application

```bash
# SSH to VPS
ssh instagram-scraper@YOUR_VPS_IP

# Restart service
sudo systemctl restart instagram-scraper

# Check status
sudo systemctl status instagram-scraper
```

### Manual Deployment

If you need to deploy manually (bypass GitHub Actions):

```bash
# SSH to VPS
ssh instagram-scraper@YOUR_VPS_IP

# Run deployment script
cd /opt/instagram-scraper/deployment
./deploy.sh
```

---

## Part 5: Optional Enhancements

### Setting Up Nginx Reverse Proxy

Install Nginx for HTTPS and better performance:

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/instagram-scraper
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/instagram-scraper /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Setting Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts to configure HTTPS

# Test auto-renewal
sudo certbot renew --dry-run
```

### Setting Up Database Backups

Create a backup script:

```bash
# Create backup script
sudo nano /opt/instagram-scraper/backup-db.sh
```

Paste this:

```bash
#!/bin/bash
BACKUP_DIR="/opt/instagram-scraper/backups/database"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
docker exec instagram_scraper_db_prod pg_dump -U scraper_user instagram_scraper | gzip > $BACKUP_DIR/backup_${DATE}.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

Make executable and schedule:

```bash
# Make executable
sudo chmod +x /opt/instagram-scraper/backup-db.sh

# Add to crontab (run daily at 2 AM)
sudo crontab -e

# Add this line:
0 2 * * * /opt/instagram-scraper/backup-db.sh
```

---

## Part 6: Troubleshooting

### Issue: Tests Fail in GitHub Actions

**Check:**
```bash
# Run tests locally
cd Backend
python test_phase1.py
python test_phase2.py
python test_phase3.py
```

Fix any errors and push again.

### Issue: Deployment Fails - SSH Error

**Check GitHub Secrets:**
- VPS_HOST is correct
- VPS_USER is `instagram-scraper`
- VPS_SSH_KEY contains the full private key

**Test SSH locally:**
```bash
ssh -i ~/.ssh/instagram_scraper_deploy instagram-scraper@YOUR_VPS_IP
```

### Issue: Application Won't Start

**Check logs:**
```bash
sudo journalctl -u instagram-scraper -n 100
```

**Common issues:**
- Missing .env file
- Database not running
- Port 8080 already in use
- Permission errors

**Fix permissions:**
```bash
sudo chown -R instagram-scraper:instagram-scraper /opt/instagram-scraper
```

### Issue: Database Connection Error

**Check PostgreSQL:**
```bash
docker ps | grep postgres

# If not running:
cd /opt/instagram-scraper/deployment
docker-compose -f docker-compose.prod.yml up -d
```

---

## Part 7: Maintenance Tasks

### Update Python Dependencies

```bash
ssh instagram-scraper@YOUR_VPS_IP
cd /opt/instagram-scraper
source venv/bin/activate
pip install --upgrade -r Backend/requirements.txt
sudo systemctl restart instagram-scraper
```

### View Database Tables

```bash
docker exec -it instagram_scraper_db_prod psql -U scraper_user -d instagram_scraper

# Inside psql:
\dt  # List tables
\d users  # Describe users table
SELECT COUNT(*) FROM users;  # Count users
\q  # Quit
```

### Monitor System Resources

```bash
# CPU and memory usage
htop

# Disk usage
df -h

# Docker stats
docker stats
```

---

## 📞 Getting Help

If you run into issues:

1. **Check logs first:**
   ```bash
   sudo journalctl -u instagram-scraper -n 100
   ```

2. **Review deployment documentation:**
   - [README.md](./README.md)
   - [../CLAUDE.md](../CLAUDE.md)

3. **Common commands:**
   ```bash
   # Restart application
   sudo systemctl restart instagram-scraper

   # Check status
   sudo systemctl status instagram-scraper

   # View logs
   sudo journalctl -u instagram-scraper -f

   # Health check
   curl http://localhost:8080/docs
   ```

---

## ✅ Success Checklist

Mark each item as you complete it:

**Server Setup:**
- [ ] VPS server accessible via SSH
- [ ] `setup-server.sh` executed successfully
- [ ] `.env` file created with production values
- [ ] PostgreSQL container running
- [ ] Database migrations completed
- [ ] Application service running
- [ ] Health check passes (`curl http://localhost:8080/docs`)

**GitHub Configuration:**
- [ ] SSH key generated
- [ ] Public key added to VPS
- [ ] All 7 GitHub Secrets configured
- [ ] GitHub Actions enabled

**Testing:**
- [ ] Empty commit pushed to main branch
- [ ] GitHub Actions workflow runs successfully
- [ ] Deployment completes without errors
- [ ] Application accessible after deployment

**Optional:**
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Database backups scheduled
- [ ] Monitoring set up

---

**Congratulations!** You've successfully set up CI/CD for the Instagram Reel Scraper! 🎉

Every time you push to the main branch, your application will automatically test and deploy to production.

---

**Last Updated:** January 2026
**Version:** 1.0.0
