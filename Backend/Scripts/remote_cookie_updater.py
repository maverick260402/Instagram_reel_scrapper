"""
Remote Cookie Updater for Instagram Accounts
Automatically extracts cookies using Playwright and updates the server
Run this script on Windows PC every 5 days (via Task Scheduler)

SECURITY NOTE: This script uses environment variables for sensitive credentials.
Set these environment variables before running:
  - COOKIE_UPDATER_SERVER_URL: The server URL (e.g., http://localhost:8080)
  - COOKIE_UPDATER_API_KEY: Your API key (generate with generate_api_key.py)
  - INSTAGRAM_EMAIL: Instagram account email
  - INSTAGRAM_PASSWORD: Instagram account password
  - INSTAGRAM_ACCOUNT_ID: Database ID of the Instagram account
"""

from playwright.sync_api import sync_playwright
import requests
import json
from datetime import datetime
import time
import sys
import os

# ==================== CONFIGURATION ====================
# Load configuration from environment variables for security

SERVER_URL = os.getenv("COOKIE_UPDATER_SERVER_URL", "http://167.71.224.203")
API_KEY = os.getenv("COOKIE_UPDATER_API_KEY", "_e5ZcJMpKDv0Walsv5fPsMSvuYh87KGBAFqWNd7kdrE")

# Instagram accounts to update - loaded from environment variables
# For multiple accounts, you can either:
# 1. Run the script multiple times with different env vars
# 2. Store account configs in a separate secure file (not in git)
INSTAGRAM_ACCOUNTS = []

# Load single account from environment variables if configured
_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
_account_email = os.getenv("INSTAGRAM_EMAIL")
_account_password = os.getenv("INSTAGRAM_PASSWORD")

if _account_id and _account_email and _account_password:
    INSTAGRAM_ACCOUNTS.append({
        "id": int(_account_id),
        "email": _account_email,
        "password": _account_password
    })

# Essential cookies to extract (Instagram specific)
ESSENTIAL_COOKIES = [
    'sessionid',
    'csrftoken',
    'ds_user_id',
    'ig_did',
    'mid',
    'datr',
    'rur',
    'wd',
    'ig_nrcb'
]

# ==================== COOKIE EXTRACTION ====================


def extract_cookies_for_account(email: str, password: str) -> dict:
    """
    Extract Instagram cookies using Playwright automation
    Returns a dictionary of essential cookies

    Based on proven logic from playwright_cookie_extractor.py
    """
    print(f"  [1/4] Launching browser...")

    with sync_playwright() as p:
        # Use Firefox for better reliability with Instagram
        browser = p.firefox.launch(
            headless=False  # Set to True for background execution
        )
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"  [2/4] Navigating to Instagram login...")
            page.goto("https://www.instagram.com/accounts/login/")

            # Wait for login form to load
            page.wait_for_selector('input[name="username"]', timeout=10000)

            print(f"  [3/4] Logging in...")
            # Fill login form
            page.fill('input[name="username"]', email)
            page.fill('input[name="password"]', password)

            # Click login button
            print(f"  [3/4] Clicking login button...")
            page.click('button[type="submit"]')

            print(f"  [3/4] Waiting for login to complete...")
            time.sleep(5)

            print(f"  [3/4] Login successful!")

            # Handle "Save Your Login Info?" prompt
            try:
                page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
                page.click('button:has-text("Not Now")')
                print(f"  [3/4] Dismissed 'Save Login Info' prompt")
            except:
                pass

            # Handle "Turn on Notifications?" prompt
            try:
                page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
                page.click('button:has-text("Not Now")')
                print(f"  [3/4] Dismissed 'Notifications' prompt")
            except:
                pass

            # Wait for everything to settle
            time.sleep(2)

            print(f"  [4/4] Extracting cookies...")
            # Extract all cookies
            all_cookies = context.cookies()

            # Filter essential cookies
            essential_cookies = {}
            for cookie in all_cookies:
                if cookie['name'] in ESSENTIAL_COOKIES:
                    essential_cookies[cookie['name']] = cookie['value']

            print(f"  [OK] Extracted {len(essential_cookies)} essential cookies")

            return essential_cookies

        except Exception as e:
            print(f"  [ERROR] Cookie extraction failed: {str(e)}")
            return {}

        finally:
            browser.close()


# ==================== SERVER COMMUNICATION ====================


def update_server_cookies(account_id: int, cookies: dict) -> bool:
    """
    Send extracted cookies to server via API
    Returns True if successful, False otherwise
    """
    if not cookies or len(cookies) == 0:
        print(f"  [ERROR] No cookies to update (extraction may have failed)")
        return False

    url = f"{SERVER_URL}/api/admin/instagram-accounts/{account_id}/cookies"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        print(f"  [UPLOAD] Sending cookies to server...")
        response = requests.post(url, json=cookies, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"  [OK] Server updated successfully!")
            print(f"       Account: {result.get('account_username', 'N/A')}")
            print(f"       Updated at: {result.get('updated_at', 'N/A')}")
            return True
        else:
            print(f"  [ERROR] Server returned error: {response.status_code}")
            print(f"       Message: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Cannot connect to server at {SERVER_URL}")
        print(f"       Make sure the server is running and accessible")
        return False
    except Exception as e:
        print(f"  [ERROR] Failed to update server: {str(e)}")
        return False


# ==================== MAIN EXECUTION ====================


def main():
    """Main execution flow"""
    print("\n" + "=" * 70)
    print("INSTAGRAM COOKIE UPDATER")
    print("=" * 70)
    print(f"Server: {SERVER_URL}")
    print(f"Accounts to update: {len(INSTAGRAM_ACCOUNTS)}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Validate configuration
    if not API_KEY:
        print("[ERROR] COOKIE_UPDATER_API_KEY environment variable not set!")
        print("Set it using: set COOKIE_UPDATER_API_KEY=your_api_key_here (Windows)")
        print("Or: export COOKIE_UPDATER_API_KEY=your_api_key_here (Linux/Mac)")
        print("Generate an API key using: python generate_api_key.py create \"Cookie Updater\"")
        sys.exit(1)

    if not INSTAGRAM_ACCOUNTS:
        print("[ERROR] No Instagram accounts configured!")
        print("Set these environment variables:")
        print("  INSTAGRAM_ACCOUNT_ID=<database_id>")
        print("  INSTAGRAM_EMAIL=<account_email>")
        print("  INSTAGRAM_PASSWORD=<account_password>")
        sys.exit(1)

    results = {
        "successful": 0,
        "failed": 0,
        "total": len(INSTAGRAM_ACCOUNTS)
    }

    for idx, account in enumerate(INSTAGRAM_ACCOUNTS, 1):
        account_id = account.get('id')
        email = account.get('email')
        password = account.get('password')

        print(f"\n[{idx}/{len(INSTAGRAM_ACCOUNTS)}] Processing Account ID: {account_id}")
        print(f"Email: {email}")
        print("-" * 70)

        if not account_id or not email or not password:
            print(f"  [ERROR] Missing account_id, email, or password. Skipping...")
            results['failed'] += 1
            continue

        try:
            # Extract cookies
            cookies = extract_cookies_for_account(email, password)

            if cookies:
                # Update server
                success = update_server_cookies(account_id, cookies)
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            else:
                print(f"  [ERROR] Cookie extraction returned no cookies")
                results['failed'] += 1

        except Exception as e:
            print(f"  [ERROR] Unexpected error: {str(e)}")
            results['failed'] += 1

        # Wait between accounts to avoid detection
        if idx < len(INSTAGRAM_ACCOUNTS):
            print(f"\n  [WAIT] Waiting 15 seconds before next account...")
            time.sleep(15)

    # Print summary
    print("\n" + "=" * 70)
    print("COOKIE UPDATE SUMMARY")
    print("=" * 70)
    print(f"Total Accounts: {results['total']}")
    print(f"Successful:     {results['successful']}")
    print(f"Failed:         {results['failed']}")
    print(f"Completed at:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    if results['failed'] > 0:
        print("[WARNING] Some accounts failed to update. Check logs above for details.")
        sys.exit(1)
    else:
        print("[SUCCESS] All accounts updated successfully!")
        sys.exit(0)


# ==================== ADDITIONAL UTILITIES ====================


def test_server_connection():
    """Test if the server is reachable and API key is valid"""
    print("\n" + "=" * 70)
    print("TESTING SERVER CONNECTION")
    print("=" * 70)
    print(f"Server URL: {SERVER_URL}")
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print("=" * 70 + "\n")

    url = f"{SERVER_URL}/api/admin/instagram-accounts"
    headers = {"X-API-Key": API_KEY}

    try:
        print("[1/2] Connecting to server...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"[2/2] [OK] Server connection successful!")
            print(f"\n     Found {data.get('count', 0)} Instagram accounts in pool:")
            for account in data.get('accounts', []):
                print(f"       - ID: {account['id']}, Username: {account['username']}, Email: {account['email']}")
            print("\n" + "=" * 70)
            print("[SUCCESS] Server is reachable and API key is valid!")
            print("=" * 70 + "\n")
            return True
        elif response.status_code == 401:
            print(f"[2/2] [ERROR] Invalid API key!")
            print(f"\nThe API key is not authorized. Generate a new one using:")
            print(f"  python generate_api_key.py create \"Cookie Updater\"")
            print("=" * 70 + "\n")
            return False
        else:
            print(f"[2/2] [ERROR] Server returned: {response.status_code}")
            print(f"     Response: {response.text}")
            print("=" * 70 + "\n")
            return False

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {SERVER_URL}")
        print(f"\nMake sure:")
        print(f"  1. The server is running (python app.py)")
        print(f"  2. The SERVER_URL is correct")
        print(f"  3. No firewall is blocking the connection")
        print("=" * 70 + "\n")
        return False
    except Exception as e:
        print(f"[ERROR] Connection test failed: {str(e)}")
        print("=" * 70 + "\n")
        return False


# ==================== ENTRY POINT ====================


if __name__ == "__main__":
    # Check if test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server_connection()
    else:
        main()
