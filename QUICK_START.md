# 🚀 Quick Start Guide - Instagram Reel Scraper

**Status**: ✅ Fully Operational
**Server**: Running on http://localhost:8888
**Last Updated**: December 19, 2025

---

## ✅ What's Already Done

- ✅ Database fully migrated (8 tables, 9 views, 51 indexes)
- ✅ Backend server running on port 8888
- ✅ All schemas verified and working
- ✅ Authentication system ready
- ✅ Admin panel configured
- ✅ Credit system active (2000 reels/day per user)
- ✅ Daily reset scheduler running (midnight auto-reset)

---

## 🎯 Quick Links

| Service | URL |
|---------|-----|
| **📱 Main App** | http://localhost:8888/static/index.html |
| **🔐 Login** | http://localhost:8888/static/login.html |
| **📝 Register** | http://localhost:8888/static/register.html |
| **👑 Admin Panel** | http://localhost:8888/static/admin/index.html |
| **📚 API Docs** | http://localhost:8888/docs |
| **🔧 API Redoc** | http://localhost:8888/redoc |

---

## 🏃‍♂️ Getting Started (5 Minutes)

### Step 1: Verify Server is Running

Check your terminal - you should see:
```
✅ Database initialized successfully
✅ Scheduler started successfully
INFO: Uvicorn running on http://127.0.0.1:8888
```

If not, start it:
```bash
cd Backend
python app.py
```

### Step 2: Register Your First User

1. Open: http://localhost:8888/static/register.html
2. Fill in:
   - **Email**: your@email.com
   - **Username**: yourname (min 3 chars)
   - **Password**: ******** (min 8 chars, letters + numbers)
3. Click **Sign Up**
4. You'll be redirected to login

### Step 3: Login

1. Enter your credentials
2. You'll see the main scraping interface

### Step 4: Add Instagram Accounts for Scraping

**These are the Instagram accounts the system will use to scrape reels (not your personal account!)**

Open a **new terminal** and run:

```bash
cd Backend
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On Linux/Mac

# Start Python shell
python
```

Then in Python:
```python
from database import SessionLocal
from crud import create_instagram_account

db = SessionLocal()

# Add Instagram account(s) to the pool
account = create_instagram_account(
    db=db,
    username="your_instagram_username",  # Instagram username
    email="your_insta@email.com",        # Instagram email
    password="your_instagram_password"    # Instagram password
)

print(f"✅ Account added: {account.username} (ID: {account.id})")
db.close()
```

**⚠️ Important**: You need at least ONE Instagram account in the pool before you can scrape!

### Step 5: Update Instagram Account Cookies

Instagram accounts need valid cookies to work. You have 2 options:

#### Option A: Generate API Key & Use Remote Updater (Recommended)

1. Generate API key:
   ```bash
   cd Backend
   python generate_api_key.py create "Cookie Updater"
   ```

   **Save the API key** - you'll need it!

2. Configure remote updater:
   - Edit `Backend/Scripts/remote_cookie_updater.py`
   - Update `SERVER_URL` to `http://localhost:8888`
   - Update `API_KEY` with the key from step 1
   - Add your Instagram account credentials

3. Run updater:
   ```bash
   python Backend/Scripts/remote_cookie_updater.py
   ```

#### Option B: Manual Cookie Update via API

Use your browser's developer tools to extract cookies from Instagram, then:

```bash
curl -X POST http://localhost:8888/api/admin/instagram-accounts/1/cookies ^
  -H "X-API-Key: your-api-key-here" ^
  -H "Content-Type: application/json" ^
  -d "{\"sessionid\":\"your_sessionid\", \"csrftoken\":\"your_csrftoken\"}"
```

### Step 6: Start Scraping!

1. Go to http://localhost:8888/static/index.html
2. Add Instagram usernames (accounts you want to scrape from)
3. Set number of reels (default: 20)
4. Click **Start Scraping**
5. View results in the **Analytics** tab

---

## 👑 Admin Panel Quick Guide

### Access Admin Panel

1. Navigate to: http://localhost:8888/static/admin/index.html
2. **Default credentials** (⚠️ CHANGE IMMEDIATELY!):
   - Username: `admin`
   - Password: `admin123`

### What You Can Do

- **📊 Dashboard**: System overview, statistics, charts
- **👥 Users**: View all users, edit credit limits, activate/deactivate
- **📱 Instagram Accounts**: Monitor account pool, check cookie health
- **📋 Activity Logs**: View all system events with filters
- **📈 Statistics**: Advanced analytics with time ranges

### Change Admin Password

```python
from database import SessionLocal
from models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
admin.password_hash = pwd_context.hash("your_new_secure_password")
db.commit()
db.close()

print("✅ Admin password changed!")
```

---

## 🔥 Common Tasks

### Add More Instagram Accounts

```python
from database import SessionLocal
from crud import create_instagram_account

db = SessionLocal()

# Add multiple accounts
accounts = [
    {"username": "account1", "email": "acc1@gmail.com", "password": "pass1"},
    {"username": "account2", "email": "acc2@gmail.com", "password": "pass2"},
]

for acc in accounts:
    account = create_instagram_account(db, **acc)
    print(f"✅ Added: {account.username}")

db.close()
```

### Check User Credit Usage

```python
from database import SessionLocal
from credit_system import get_user_credit_summary

db = SessionLocal()
summary = get_user_credit_summary(db, user_id=1)

print(f"Credits: {summary['remaining']}/{summary['daily_limit']}")
print(f"Used today: {summary['used_today']} ({summary['usage_percent']}%)")

db.close()
```

### Manually Reset Credits

```python
from database import SessionLocal
from credit_system import reset_all_daily_credits

db = SessionLocal()
reset_all_daily_credits(db)
print("✅ All credits reset!")
db.close()
```

### View Instagram Account Status

```python
from database import SessionLocal
from account_rotation import get_all_account_stats

db = SessionLocal()
stats = get_all_account_stats(db)

for account in stats:
    print(f"\n{account['username']} (ID: {account['id']})")
    print(f"  Active: {account['is_active']}")
    print(f"  Today: {account['daily_scrape_count']} reels")
    print(f"  Total: {account['total_scrapes']} reels")
    print(f"  Success rate: {account['success_rate']}%")
    print(f"  Cookie health: {account['cookie_health']}")

db.close()
```

---

## ⚠️ Troubleshooting

### "No Instagram accounts available" Error

**Cause**: No Instagram accounts in pool or all are paused

**Solution**:
```python
from database import SessionLocal
from crud import get_all_instagram_accounts

db = SessionLocal()
accounts = get_all_instagram_accounts(db)

print(f"Total accounts: {len(accounts)}")
for acc in accounts:
    print(f"  {acc.username}: active={acc.is_active}, paused={acc.is_paused}")

db.close()
```

If no accounts exist, follow **Step 4** above to add them.

### Scraping Returns 0 Reels

**Cause**: Instagram account cookies are invalid

**Solution**: Update cookies using **Step 5** above

### "Insufficient credits" Error

**Cause**: User has used all daily credits (default: 2000 reels/day)

**Solutions**:
1. Wait until midnight for automatic reset
2. Manually reset (admin):
   ```python
   from database import SessionLocal
   from credit_system import reset_all_daily_credits

   db = SessionLocal()
   reset_all_daily_credits(db)
   db.close()
   ```
3. Increase user's credit limit (admin):
   ```python
   from database import SessionLocal
   from credit_system import update_user_credit_limit

   db = SessionLocal()
   update_user_credit_limit(db, user_id=1, new_limit=5000)
   db.close()
   ```

### Server Won't Start (Port Already in Use)

**Solution**: Change port in `Backend/app.py` and `Backend/.env`

Current port: **8888**

To change to 9000:
1. Edit `Backend/app.py` line 955: `port=9000`
2. Edit `Backend/.env`: `ALLOWED_ORIGINS=http://localhost:9000,http://127.0.0.1:9000`
3. Restart server

### Database Connection Errors

**Check if PostgreSQL is running**:
```bash
docker ps | grep instagram_scraper_db
```

If not running:
```bash
docker start instagram_scraper_db
```

---

## 📊 System Limits & Features

| Feature | Limit | Notes |
|---------|-------|-------|
| **Daily Credits** | 2000 reels/user | Admin can change |
| **User Groups** | 100 per user | Set in .env |
| **Token Expiry** | 7 days | Auto-renew on use |
| **Job Timeout** | 10 minutes | For long scraping jobs |
| **Max Reels/Job** | Unlimited | Limited by credits |

---

## 🎓 Key Concepts

### Credits
- **1 Credit = 1 Reel Scraped**
- Resets daily at midnight automatically
- Admin can set custom limits per user
- Tracks total usage in admin panel

### Instagram Account Rotation
- System automatically selects **least-used** account
- Tracks success/failure rates
- Monitors cookie freshness
- Can pause/resume accounts individually

### Activity Logging
- All scraping events logged
- Admin actions tracked
- Cookie updates recorded
- Credit changes logged

---

## 📖 Full Documentation

- **📘 [CLAUDE.md](CLAUDE.md)** - Complete technical documentation
- **📗 [DATABASE_MIGRATION_COMPLETE.md](DATABASE_MIGRATION_COMPLETE.md)** - Migration details
- **📙 [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Project status (98% complete!)

---

## 🎉 You're Ready!

Your Instagram Reel Scraper is fully set up and ready to use!

**Next Steps**:
1. ✅ Register your account → http://localhost:8888/static/register.html
2. ✅ Add Instagram accounts for scraping (Step 4)
3. ✅ Update Instagram cookies (Step 5)
4. ✅ Start scraping! → http://localhost:8888/static/index.html

**Need Help?** Check the troubleshooting section above or review the full documentation.

---

**🚀 Happy Scraping!**
