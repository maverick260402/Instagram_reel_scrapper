from playwright.sync_api import sync_playwright
import json
import time
from pathlib import Path
from datetime import datetime, timedelta


def extract_instagram_cookie(email: str, password: str, force_refresh: bool = False) -> str:
    """
    Extract Instagram cookies using Playwright login.
    Automatically reuses existing cookies if they are less than 5 days old.

    Args:
        email: Instagram email/username
        password: Instagram password
        force_refresh: If True, regenerate cookie even if valid cookie exists

    Returns:
        Cookie string formatted as: name=value; name=value; ...
    """

    # Setup cookie directory and file path
    cookies_dir = Path(__file__).parent / "cookies"
    cookies_dir.mkdir(exist_ok=True)

    # Find all existing cookie files
    cookie_files = sorted(cookies_dir.glob("insta_cookie_*.json"), reverse=True)

    # Check for valid cookies (less than 5 days old)
    if not force_refresh and cookie_files:
        for cookie_file_path in cookie_files:
            # Extract date from filename: insta_cookie_YYYY_MM_DD.json
            try:
                filename = cookie_file_path.stem  # insta_cookie_YYYY_MM_DD
                date_str = filename.replace("insta_cookie_", "")  # YYYY_MM_DD
                cookie_date = datetime.strptime(date_str, "%Y_%m_%d")

                # Calculate age in days
                age_days = (datetime.now() - cookie_date).days

                if age_days < 5:
                    # Cookie is still valid, reuse it
                    print(f">>> Found valid cookie from {date_str} ({age_days} days old)")
                    print(f">>> Loading cookie from: {cookie_file_path}")
                    with open(cookie_file_path, 'r') as f:
                        cookies_list = json.load(f)
                    return _format_cookie_string(cookies_list)
                else:
                    print(f">>> Cookie from {date_str} is {age_days} days old (expired)")
            except (ValueError, IndexError):
                # Skip malformed filenames
                print(f">>> Skipping invalid cookie file: {cookie_file_path.name}")
                continue

    # If we reach here, no valid cookie found - generate new one
    print(">>> No valid cookie found (older than 5 days or doesn't exist)")
    print(">>> Starting Playwright to extract fresh cookies...")

    today = datetime.now().strftime("%Y_%m_%d")
    cookie_file = cookies_dir / f"insta_cookie_{today}.json"

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(">>> Navigating to Instagram login page...")
        page.goto("https://www.instagram.com/accounts/login/")

        # Wait for login form to load
        page.wait_for_selector('input[name="username"]', timeout=10000)

        print(">>> Entering credentials...")
        page.fill('input[name="username"]', email)
        page.fill('input[name="password"]', password)

        print(">>> Clicking login button...")
        page.click('button[type="submit"]')

        print(">>> Waiting for login to complete...")
        time.sleep(5)

        print(">>> Login successful!")

        # Dismiss "Save Your Login Info?" prompt
        try:
            page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
            page.click('button:has-text("Not Now")')
            print(">>> Dismissed 'Save Login Info' prompt")
        except:
            pass

        # Dismiss "Turn on Notifications?" prompt
        try:
            page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
            page.click('button:has-text("Not Now")')
            print(">>> Dismissed 'Notifications' prompt")
        except:
            pass

        # Wait for everything to settle
        time.sleep(2)

        # Extract cookies
        cookies_list = context.cookies()
        print(f"\n>>> Extracted {len(cookies_list)} cookies")

        # Save to file
        with open(cookie_file, "w") as f:
            json.dump(cookies_list, f, indent=4)

        print(f"✔ Cookies saved to {cookie_file}")

        browser.close()

    return _format_cookie_string(cookies_list)


def _format_cookie_string(cookies_list: list) -> str:
    """
    Convert cookies list to browser-formatted string.
    Filters to include only essential Instagram cookies.

    Format: name=value; name=value; ...
    """
    # Essential Instagram cookies (based on working cookie string)
    ESSENTIAL_COOKIES = [
        'ig_did',
        'csrftoken',
        'datr',
        'ps_l',
        'ps_n',
        'ig_nrcb',
        'mid',
        'ds_user_id',
        'dpr',
        'sessionid',
        'wd',
        'rur'
    ]

    # Filter and maintain order from cookies_list
    cookie_parts = []
    for cookie in cookies_list:
        name = cookie.get('name', '')
        value = cookie.get('value', '')

        # Only include essential cookies
        if name in ESSENTIAL_COOKIES and value:
            cookie_parts.append(f"{name}={value}")

    cookie_string = "; ".join(cookie_parts)

    # Print filtered cookies for debugging
    filtered_names = [c.split('=')[0] for c in cookie_parts]
    print(f">>> Filtered cookies: {', '.join(filtered_names)}")

    return cookie_string


def get_latest_cookie() -> str:
    """
    Load the most recent cookie file from the cookies directory.

    Returns:
        Cookie string or None if no cookie file exists
    """
    cookies_dir = Path(__file__).parent / "cookies"
    if not cookies_dir.exists():
        return None

    # Find the most recent cookie file
    cookie_files = sorted(cookies_dir.glob("insta_cookie_*.json"), reverse=True)
    if not cookie_files:
        return None

    latest_file = cookie_files[0]
    print(f">>> Loading cookie from: {latest_file}")

    with open(latest_file, 'r') as f:
        cookies_list = json.load(f)

    return _format_cookie_string(cookies_list)


if __name__ == "__main__":
    # Test the cookie extraction
    email = input("Enter Instagram email/username: ")
    password = input("Enter Instagram password: ")

    cookie_string = extract_instagram_cookie(email, password)

    print("\n" + "="*80)
    print("COOKIE STRING (first 200 chars):")
    print(cookie_string[:200] + "...")
    print("="*80)
