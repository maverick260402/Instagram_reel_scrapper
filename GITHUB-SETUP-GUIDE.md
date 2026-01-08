# GitHub Repository Setup Guide

This guide shows you exactly what to configure on the GitHub website for CI/CD to work.

---

## 📋 Prerequisites

Before configuring GitHub, you must:

1. ✅ Have your VPS server set up (run `deployment/setup-server.sh`)
2. ✅ Have generated SSH keys for deployment
3. ✅ Have production `.env` values ready

---

## Part 1: Enable GitHub Actions

### Step 1: Navigate to Actions Tab

1. Go to your repository on GitHub
2. Click the **"Actions"** tab at the top

### Step 2: Enable Workflows

If you see "Workflows disabled":
1. Click **"I understand my workflows, go ahead and enable them"**

You should now see:
- ✅ "CI/CD Pipeline" workflow
- ✅ "Tests Only" workflow

---

## Part 2: Configure Repository Secrets

### Step 1: Go to Settings

1. Click **"Settings"** tab in your repository
2. In the left sidebar, click **"Secrets and variables"** → **"Actions"**

### Step 2: Add Each Secret

Click **"New repository secret"** button and add each of the following:

---

### Secret 1: VPS_HOST

**Name:** `VPS_HOST`

**Value:** Your VPS IP address or domain name

**How to get it:**
```bash
# On your VPS, run:
hostname -I | awk '{print $1}'

# Or use your domain:
# Example: myserver.com
```

**Example values:**
- `123.45.67.89`
- `myserver.com`
- `app.yourdomain.com`

---

### Secret 2: VPS_USER

**Name:** `VPS_USER`

**Value:** `instagram-scraper`

**Note:** This is always `instagram-scraper` (the user created by setup script)

---

### Secret 3: VPS_SSH_KEY

**Name:** `VPS_SSH_KEY`

**Value:** Your private SSH key (entire content)

**How to get it:**
```bash
# On your LOCAL machine, run:
cat ~/.ssh/instagram_scraper_deploy
```

**Important:**
- Copy the ENTIRE output
- Must include `-----BEGIN OPENSSH PRIVATE KEY-----`
- Must include `-----END OPENSSH PRIVATE KEY-----`
- Must include ALL lines in between

**Example format:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBK7VGZ5lN0IxUEfO8Ju9fKxVuS9K7VGZ5lN0IxUEfO8JAAAAJgxvN0YMbz
... (many lines) ...
dGVyIDxuYW1lQGV4YW1wbGUuY29tPgECAwQ=
-----END OPENSSH PRIVATE KEY-----
```

---

### Secret 4: VPS_PORT

**Name:** `VPS_PORT`

**Value:** `22`

**Note:** This is usually `22` (standard SSH port). Only change if your VPS uses a different SSH port.

---

### Secret 5: DATABASE_URL

**Name:** `DATABASE_URL`

**Value:** PostgreSQL connection string from your VPS

**How to get it:**
```bash
# SSH to your VPS, then run:
sudo grep DATABASE_URL /opt/instagram-scraper/.env
```

**Format:**
```
postgresql://scraper_user:YOUR_PASSWORD@localhost:5432/instagram_scraper
```

**Important:** Make sure to use the actual password you set during VPS setup

---

### Secret 6: SECRET_KEY

**Name:** `SECRET_KEY`

**Value:** JWT secret key from your VPS

**How to get it:**
```bash
# SSH to your VPS, then run:
sudo grep SECRET_KEY /opt/instagram-scraper/.env | cut -d'=' -f2
```

**Format:**
```
abc123def456789...  (64 hex characters)
```

**Note:** This should be a 64-character hexadecimal string

---

### Secret 7: ALLOWED_ORIGINS

**Name:** `ALLOWED_ORIGINS`

**Value:** Comma-separated list of allowed domains

**How to get it:**
```bash
# SSH to your VPS, then run:
sudo grep ALLOWED_ORIGINS /opt/instagram-scraper/.env | cut -d'=' -f2
```

**Format:**
```
https://yourdomain.com,http://yourdomain.com
```

**Examples:**
- `https://myapp.com,http://myapp.com`
- `https://app.example.com`
- `http://123.45.67.89:8080` (for testing with IP)

---

### Step 3: Verify All Secrets

After adding all 7 secrets, you should see:

| Name | Updated |
|------|---------|
| ALLOWED_ORIGINS | X seconds ago |
| DATABASE_URL | X seconds ago |
| SECRET_KEY | X seconds ago |
| VPS_HOST | X seconds ago |
| VPS_PORT | X seconds ago |
| VPS_SSH_KEY | X seconds ago |
| VPS_USER | X seconds ago |

**✅ All 7 secrets configured!**

---

## Part 3: Test the Setup

### Step 1: Make a Test Commit

On your **local machine**:

```bash
# Make sure you're in your repository
cd ~/path/to/Instagram_reel_scrapper

# Check you're on main branch
git branch

# Create an empty commit
git commit --allow-empty -m "Test CI/CD pipeline setup"

# Push to GitHub
git push origin main
```

### Step 2: Watch GitHub Actions

1. Go to your repository on GitHub
2. Click **"Actions"** tab
3. You should see a new workflow run: **"Test CI/CD pipeline setup"**
4. Click on it to see details

### Step 3: Monitor the Workflow

You'll see two jobs:

**Job 1: Run Tests**
- ✅ Checkout code
- ✅ Set up Python 3.11
- ✅ Install dependencies
- ✅ Run database migrations
- ✅ Run Phase 1 Tests
- ✅ Run Phase 2 Tests
- ✅ Run Phase 3 Tests

**Job 2: Deploy to VPS** (only runs if tests pass)
- ✅ Checkout code
- ✅ Setup SSH
- ✅ Deploy to VPS
- ✅ Cleanup SSH

### Step 4: Verify Deployment

If the workflow shows all green checkmarks ✅:

1. **SSH to your VPS:**
   ```bash
   ssh instagram-scraper@your-vps-ip
   ```

2. **Check service status:**
   ```bash
   sudo systemctl status instagram-scraper
   ```

3. **Check latest commit:**
   ```bash
   cd /opt/instagram-scraper
   git log -1 --oneline
   ```

4. **Health check:**
   ```bash
   curl http://localhost:8080/docs
   ```

All should be working! 🎉

---

## Part 4: Add Status Badges (Optional)

### Step 1: Update Badge URLs

Edit `README.md` and replace `YOUR-USERNAME` with your actual GitHub username:

**Before:**
```markdown
![CI/CD Status](https://github.com/YOUR-USERNAME/Instagram_reel_scrapper/actions/workflows/ci-cd.yml/badge.svg)
```

**After:**
```markdown
![CI/CD Status](https://github.com/maverick260402/Instagram_reel_scrapper/actions/workflows/ci-cd.yml/badge.svg)
```

### Step 2: Commit and Push

```bash
git add README.md
git commit -m "Update CI/CD status badge"
git push origin main
```

Now your README will show live build status! ✅

---

## Part 5: Optional Settings

### Branch Protection Rules

Protect your main branch from accidental pushes:

1. **Go to:** Settings → Branches
2. **Click:** Add rule
3. **Branch name pattern:** `main`
4. **Enable:**
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
5. **Select status checks:**
   - ✅ Run Tests
6. **Click:** Create

Now you can't push directly to main without passing tests!

### Notifications

Get notified when deployments succeed/fail:

1. **Go to:** Settings → Notifications
2. **Choose notification method:**
   - Email
   - Slack (requires Slack integration)
   - Discord (requires webhook)
3. **Configure triggers:**
   - Workflow runs
   - Failed deployments

---

## Troubleshooting GitHub Setup

### ❌ "SSH connection failed" Error

**Problem:** VPS_SSH_KEY is incorrect

**Fix:**
1. Generate new SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/instagram_deploy_new
   ```

2. Add public key to VPS:
   ```bash
   cat ~/.ssh/instagram_deploy_new.pub | ssh your-user@your-vps "sudo -u instagram-scraper tee -a /home/instagram-scraper/.ssh/authorized_keys"
   ```

3. Update GitHub Secret `VPS_SSH_KEY` with new private key:
   ```bash
   cat ~/.ssh/instagram_deploy_new
   ```

### ❌ "Tests Failed" Error

**Problem:** Tests are failing in CI

**Fix:**
1. Run tests locally:
   ```bash
   cd Backend
   python test_phase1.py
   python test_phase2.py
   python test_phase3.py
   ```

2. Fix any errors

3. Push again:
   ```bash
   git add .
   git commit -m "Fix failing tests"
   git push origin main
   ```

### ❌ "Deployment Failed - Health Check" Error

**Problem:** Application didn't start correctly on VPS

**Fix:**
1. SSH to VPS
2. Check logs:
   ```bash
   sudo journalctl -u instagram-scraper -n 100
   ```
3. Common issues:
   - Missing .env file
   - Database not running
   - Port 8080 already in use

### ❌ Workflow Not Triggering

**Problem:** Workflow doesn't run when you push

**Fix:**
1. Check GitHub Actions is enabled:
   - Go to Actions tab
   - Look for "Workflows disabled" message

2. Check workflow file syntax:
   - View `.github/workflows/ci-cd.yml`
   - Look for YAML syntax errors

3. Check branch name:
   - Workflow only runs on `main` branch
   - Verify you pushed to `main`

---

## Quick Reference: All GitHub Secrets

| Secret | Example | Where to Get |
|--------|---------|--------------|
| VPS_HOST | `123.45.67.89` | `hostname -I` on VPS |
| VPS_USER | `instagram-scraper` | Fixed value |
| VPS_SSH_KEY | `-----BEGIN...` | `cat ~/.ssh/instagram_scraper_deploy` |
| VPS_PORT | `22` | Usually 22 |
| DATABASE_URL | `postgresql://...` | From VPS `.env` file |
| SECRET_KEY | `abc123...` | From VPS `.env` file |
| ALLOWED_ORIGINS | `https://...` | From VPS `.env` file |

---

## ✅ Checklist

- [ ] GitHub Actions enabled in repository
- [ ] All 7 secrets configured correctly
- [ ] Test commit pushed to main branch
- [ ] Workflow ran successfully (green checkmarks)
- [ ] Application deployed and accessible on VPS
- [ ] Status badges updated in README
- [ ] (Optional) Branch protection rules enabled
- [ ] (Optional) Notifications configured

---

## 🎉 Success!

If all items are checked, your CI/CD pipeline is fully configured and working!

**From now on:**
- Every push to `main` automatically deploys to production ✅
- Every pull request automatically runs tests ✅
- Failed tests block deployment ✅
- Deployment failures automatically rollback ✅

**Next Steps:**
- Make code changes
- Create pull request
- Merge to main
- Watch automatic deployment!

---

**Need Help?**
- Deployment guide: [deployment/SETUP.md](deployment/SETUP.md)
- Troubleshooting: [deployment/README.md](deployment/README.md)
- Full documentation: [CLAUDE.md](CLAUDE.md)

---

**Happy deploying!** 🚀
