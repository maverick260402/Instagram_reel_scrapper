from playwright.sync_api import sync_playwright
import json
import time

# Get login credentials from user
email = input("Enter Instagram email/username: ")
password = input("Enter Instagram password: ")

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)  # visible browser
    context = browser.new_context()
    page = context.new_page()

    print(">>> Navigating to Instagram login page...")
    page.goto("https://www.instagram.com/accounts/login/")

    # Wait for login form to load
    page.wait_for_selector('input[name="username"]', timeout=10000)

    print(">>> Entering credentials...")
    # Fill in username/email
    page.fill('input[name="username"]', email)

    # Fill in password
    page.fill('input[name="password"]', password)

    print(">>> Clicking login button...")
    # Click login button
    page.click('button[type="submit"]')

    print(">>> Waiting for login to complete...")
    # Wait for the login request to process
    time.sleep(5)

    print(">>> Login successful!")

    # Check if "Save Your Login Info?" prompt appears
    try:
        page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
        page.click('button:has-text("Not Now")')
        print(">>> Dismissed 'Save Login Info' prompt")
    except:
        pass

    # Check if "Turn on Notifications?" prompt appears
    try:
        page.wait_for_selector('button:has-text("Not Now")', timeout=5000)
        page.click('button:has-text("Not Now")')
        print(">>> Dismissed 'Notifications' prompt")
    except:
        pass

    # Wait a bit for everything to settle
    time.sleep(2)

    # Extract cookies
    cookies = context.cookies()
    print("\n>>> SESSION COOKIES:\n", cookies)

    # Save to file
    with open("insta_cookies.json", "w") as f:
        json.dump(cookies, f, indent=4)

    print("\n✔ Cookies saved to insta_cookies.json")

    # Keep browser open for a moment to verify success
    time.sleep(2)
    browser.close()
