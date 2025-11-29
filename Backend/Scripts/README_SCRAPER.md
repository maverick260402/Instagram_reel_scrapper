# Instagram Scraper with Dynamic Cookies

Complete integration of cookie management with Instagram reel scraping.

## 📁 Files

1. **getCookies.py** - Cookie acquisition utility
2. **scraper_with_cookies.py** - Main scraper with cookie integration
3. **example_usage.py** - Usage examples
4. **pipeline.py** (in Backend/) - Original pipeline (unchanged)

## 🚀 Quick Start

### Method 1: Interactive Menu (Easiest)

```bash
cd "d:\ThunderBolts\Project Tres\Script_Based_Solution\Instagram_reel_scrapper\Backend\Scripts"
python scraper_with_cookies.py
```

Follow the prompts to:
1. Provide cookies (manually recommended)
2. Scrape single or multiple users
3. Save/load cookies

### Method 2: Programmatic Usage

```python
from scraper_with_cookies import InstagramScraperWithCookies

# Provide cookies from browser
cookies = {
    "sessionid": "YOUR_SESSION_ID",
    "csrftoken": "YOUR_CSRF_TOKEN",
    "ds_user_id": "YOUR_USER_ID",
}

scraper = InstagramScraperWithCookies(cookies=cookies)

# Scrape a user
df = scraper.scrape_user("cristiano", reel_count=20)
print(df.head())
```

## 🍪 Getting Cookies from Browser (RECOMMENDED)

### Chrome/Edge:
1. Open Instagram and **login**
2. Press **F12** to open Developer Tools
3. Go to **Application** tab
4. In left sidebar: **Cookies** → `https://www.instagram.com`
5. Copy these cookies:

| Cookie Name | Required? | Description |
|------------|-----------|-------------|
| `sessionid` | ✅ YES | Authentication token (MOST IMPORTANT) |
| `csrftoken` | ✅ YES | CSRF protection token |
| `ds_user_id` | ✅ YES | Your user ID |
| `mid` | ⚪ Recommended | Machine ID |
| `ig_did` | ⚪ Recommended | Instagram device ID |
| `datr` | ⚪ Recommended | Device tracking |
| `rur` | ⚪ Recommended | Region/routing |

### Firefox:
1. Open Instagram and **login**
2. Press **F12** to open Developer Tools
3. Go to **Storage** tab
4. Click **Cookies** → `https://www.instagram.com`
5. Copy the same cookies as above

### Format as Python Dictionary:

```python
cookies = {
    "sessionid": "77967696629%3AUTq3mfQ36OdF5V%3A0",
    "csrftoken": "RveSWjfHjw8mJPPqXqWB44",
    "ds_user_id": "77967696629",
    "mid": "aMBkxQALAAE1j-UKTokmRi3MGTrO",
    "ig_did": "CC536145-A463-42A8-8C5E-E9CE461F64C6",
    "datr": "xWTAaC376j9eU8pZLQr3Zzxk",
    "rur": "RVA\\05477967696629\\0541795698791"
}
```

## 📖 Usage Examples

### Example 1: Single User

```python
from scraper_with_cookies import InstagramScraperWithCookies

cookies = {
    "sessionid": "YOUR_SESSION_ID",
    "csrftoken": "YOUR_CSRF_TOKEN",
    "ds_user_id": "YOUR_USER_ID",
}

scraper = InstagramScraperWithCookies(cookies=cookies)

# Scrape 50 reels from cristiano
df = scraper.scrape_user("cristiano", reel_count=50)

if df is not None:
    print(f"Scraped {len(df)} reels")
    print(df.head())
```

### Example 2: Multiple Users

```python
from scraper_with_cookies import InstagramScraperWithCookies

cookies = { ... }  # Your cookies

scraper = InstagramScraperWithCookies(cookies=cookies)

usernames = ["cristiano", "leomessi", "neymarjr", "virat.kohli"]

results = scraper.scrape_multiple_users(
    usernames=usernames,
    reel_count=30,
    sleep_between_users=5.0,      # Wait 5s between users
    sleep_between_requests=3.0     # Wait 3s between requests
)

# Check results
for username, df in results.items():
    if df is not None:
        print(f"{username}: {len(df)} reels ✅")
    else:
        print(f"{username}: FAILED ❌")
```

### Example 3: Save/Load Cookies

```python
from scraper_with_cookies import InstagramScraperWithCookies

# First time: save cookies
cookies = { ... }
scraper = InstagramScraperWithCookies(cookies=cookies)
scraper.cookie_manager.save_cookies_to_file(cookies, "my_cookies.json")

# Later: load cookies
scraper2 = InstagramScraperWithCookies()
loaded_cookies = scraper2.cookie_manager.load_cookies_from_file("my_cookies.json")
scraper2.cookies = loaded_cookies
scraper2._update_cookie_string()

# Use loaded cookies
df = scraper2.scrape_user("instagram", reel_count=10)
```

### Example 4: Manual Step-by-Step

```python
from scraper_with_cookies import InstagramScraperWithCookies

cookies = { ... }
scraper = InstagramScraperWithCookies(cookies=cookies)

username = "cristiano"

# Step 1: Get target ID
target_id = scraper.get_target_id(username)
print(f"Target ID: {target_id}")

# Step 2: Fetch reels
meta_path = scraper.fetch_reels_paginated(
    target_id=target_id,
    username=username,
    desired_count=100,
    sleep_seconds=3.0,
    max_per_page=50
)
print(f"Saved to: {meta_path}")

# Step 3: Extract data
df = scraper.extract_reel_data(meta_path)
print(df.head())
```

## 🔧 Features

### InstagramScraperWithCookies Class

**Methods:**
- `get_target_id(username)` - Get user's target ID
- `fetch_reels_paginated(target_id, username, desired_count, ...)` - Fetch reels with pagination
- `extract_reel_data(meta_path)` - Extract data from JSON to DataFrame/CSV
- `scrape_user(username, reel_count, ...)` - Complete workflow for one user
- `scrape_multiple_users(usernames, reel_count, ...)` - Scrape multiple users

**Parameters:**
- `desired_count` / `reel_count` - Number of reels to scrape (default: 20)
- `sleep_seconds` / `sleep_between_requests` - Delay between requests (default: 3.0s)
- `sleep_between_users` - Delay between users (default: 5.0s)
- `max_per_page` - Maximum reels per page (default: 50, max: 50)

## 📂 Output Structure

```
Backend/
└── output_json/
    └── {username}/
        ├── meta_data.json       # Raw Instagram API response
        └── scrapped_data.csv    # Extracted reel data
```

**CSV Columns:**
- `pk` - Post ID
- `code` - Short code
- `play_count` - Number of plays
- `comment_count` - Number of comments
- `like_count` - Number of likes
- `is_reel_pinned` - Whether reel is pinned (Yes/No)
- `url` - Direct URL to the reel

## ⚠️ Important Notes

### Cookie Expiration
- Cookies expire after ~90 days of inactivity
- You'll need to refresh them periodically
- If scraping fails, try getting fresh cookies

### Rate Limiting
- Instagram may rate limit if you make too many requests
- Use appropriate sleep timings (3-5 seconds recommended)
- Don't scrape too many users at once

### Authentication
- **sessionid** is the most critical cookie
- Without it, scraping will fail
- Keep your cookies private (they give full account access)

### Bot Detection
- Instagram has strong bot detection
- Using cookies from real browser session is most reliable
- Automated login (option 2 in getCookies.py) often fails

## 🐛 Troubleshooting

### "Could not find target_id"
- Username doesn't exist or is private
- Cookies are expired or invalid
- Instagram changed their HTML structure

### "Login failed" / "Error during login"
- Instagram detected automation
- 2FA is enabled (can't automate)
- Use browser cookie method instead

### Empty results / No reels found
- Account has no reels
- Account is private
- Cookies don't have permission to view

### Rate limiting errors
- Increase `sleep_seconds` parameter
- Reduce number of reels per request
- Wait before trying again

## 🔐 Security

**NEVER commit cookies to Git:**
- Add `*.json` to `.gitignore`
- Don't share cookie files
- Cookies give full access to your account

**Best Practices:**
- Use a secondary Instagram account for scraping
- Don't use your main account
- Rotate cookies periodically

## 📝 Comparison with Original Pipeline

| Feature | pipeline.py | scraper_with_cookies.py |
|---------|------------|------------------------|
| Cookies | Hardcoded ❌ | Dynamic ✅ |
| Cookie expiry handling | Manual ❌ | Automatic ✅ |
| Interactive mode | No ❌ | Yes ✅ |
| Cookie management | No ❌ | Yes (save/load) ✅ |
| Multiple users | Manual loop ⚪ | Built-in method ✅ |
| Error handling | Basic ⚪ | Enhanced ✅ |
| Progress tracking | Basic ⚪ | Detailed ✅ |

## 📚 Additional Resources

- [Instagram Graph API (Official)](https://developers.facebook.com/docs/instagram-api)
- [Requests Documentation](https://requests.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🤝 Contributing

Feel free to improve this scraper:
- Better error handling
- Cookie rotation support
- Proxy support
- Async/concurrent scraping

---

**Created with Claude Code** 🤖
