# -*- coding: utf-8 -*-
"""
Example Usage of Instagram Scraper with Cookies
Shows different ways to use the scraper programmatically
"""

from scraper_with_cookies import InstagramScraperWithCookies


# ============================================================
# EXAMPLE 1: Manual Cookie String (RECOMMENDED)
# ============================================================
def example_manual_cookies():
    """Use manually obtained cookies from browser"""

    # Get cookies from your browser (F12 -> Application -> Cookies)
    cookies = {
        "sessionid": "YOUR_SESSION_ID_HERE",
        "csrftoken": "YOUR_CSRF_TOKEN_HERE",
        "ds_user_id": "YOUR_USER_ID_HERE",
        "mid": "YOUR_MID_HERE",
        "ig_did": "YOUR_IG_DID_HERE",
        "datr": "YOUR_DATR_HERE",
        "rur": "YOUR_RUR_HERE",
    }

    # Initialize scraper with cookies
    scraper = InstagramScraperWithCookies(cookies=cookies)

    # Scrape single user
    df = scraper.scrape_user("cristiano", reel_count=10)

    if df is not None:
        print(f"\n✅ Successfully scraped {len(df)} reels")
        print(df.head())


# ============================================================
# EXAMPLE 2: Load Cookies from File
# ============================================================
def example_load_from_file():
    """Load cookies from a saved JSON file"""

    scraper = InstagramScraperWithCookies()

    # Load cookies from file
    cookies = scraper.cookie_manager.load_cookies_from_file("instagram_cookies.json")

    if cookies:
        scraper.cookies = cookies
        scraper._update_cookie_string()

        # Scrape user
        df = scraper.scrape_user("virat.kohli", reel_count=15)

        if df is not None:
            print(f"\n✅ Scraped {len(df)} reels")


# ============================================================
# EXAMPLE 3: Scrape Multiple Users
# ============================================================
def example_multiple_users():
    """Scrape multiple users in one go"""

    # Provide cookies
    cookies = {
        "sessionid": "YOUR_SESSION_ID",
        "csrftoken": "YOUR_CSRF_TOKEN",
        "ds_user_id": "YOUR_USER_ID",
    }

    scraper = InstagramScraperWithCookies(cookies=cookies)

    # Scrape multiple users
    usernames = ["cristiano", "leomessi", "neymarjr"]

    results = scraper.scrape_multiple_users(
        usernames=usernames,
        reel_count=20,
        sleep_between_users=5.0,
        sleep_between_requests=3.0
    )

    # Print results
    for username, df in results.items():
        if df is not None:
            print(f"\n{username}: {len(df)} reels scraped")
        else:
            print(f"\n{username}: FAILED")


# ============================================================
# EXAMPLE 4: Interactive Mode (No cookies provided)
# ============================================================
def example_interactive():
    """
    Interactive mode - will prompt user to provide cookies
    This is useful when running as a standalone script
    """

    # Don't provide cookies - script will prompt user
    scraper = InstagramScraperWithCookies()

    # Then use normally
    df = scraper.scrape_user("instagram", reel_count=10)


# ============================================================
# EXAMPLE 5: Step-by-Step Manual Process
# ============================================================
def example_step_by_step():
    """Manually control each step of the scraping process"""

    cookies = {
        "sessionid": "YOUR_SESSION_ID",
        "csrftoken": "YOUR_CSRF_TOKEN",
        "ds_user_id": "YOUR_USER_ID",
    }

    scraper = InstagramScraperWithCookies(cookies=cookies)

    username = "cristiano"

    # Step 1: Get target ID
    target_id = scraper.get_target_id(username)

    if target_id:
        print(f"Target ID: {target_id}")

        # Step 2: Fetch reels
        meta_path = scraper.fetch_reels_paginated(
            target_id=target_id,
            username=username,
            desired_count=50,
            sleep_seconds=3.0,
            max_per_page=50
        )

        if meta_path:
            print(f"Meta data saved to: {meta_path}")

            # Step 3: Extract and save CSV
            df = scraper.extract_reel_data(meta_path)
            print(f"\nExtracted {len(df)} reels")
            print(df.head())


# ============================================================
# EXAMPLE 6: Cookie Management
# ============================================================
def example_cookie_management():
    """Demonstrate cookie save/load functionality"""

    # Get cookies from browser (manually)
    cookies = {
        "sessionid": "YOUR_SESSION_ID",
        "csrftoken": "YOUR_CSRF_TOKEN",
        "ds_user_id": "YOUR_USER_ID",
    }

    scraper = InstagramScraperWithCookies(cookies=cookies)

    # Save cookies to file for later use
    scraper.cookie_manager.save_cookies_to_file(
        scraper.cookies,
        filename="my_instagram_cookies.json"
    )

    # Later, load cookies from file
    loaded_cookies = scraper.cookie_manager.load_cookies_from_file(
        filename="my_instagram_cookies.json"
    )

    # Use loaded cookies
    new_scraper = InstagramScraperWithCookies(cookies=loaded_cookies)
    new_scraper.scrape_user("instagram", reel_count=5)


# ============================================================
# MAIN - Run examples
# ============================================================
if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     Instagram Scraper with Cookies - Usage Examples       ║
    ╚════════════════════════════════════════════════════════════╝

    This file shows different ways to use the scraper.

    ⚠️  IMPORTANT: Before running any example:
    1. Get your Instagram cookies from browser (F12 -> Application)
    2. Replace "YOUR_SESSION_ID_HERE" etc. with real values
    3. Make sure you have sessionid, csrftoken, and ds_user_id

    Choose an example to run:
    1. Manual cookies (recommended)
    2. Load from file
    3. Multiple users
    4. Interactive mode
    5. Step-by-step
    6. Cookie management

    Or run the main script directly: python scraper_with_cookies.py
    """)

    choice = input("Enter example number (1-6) or 'q' to quit: ").strip()

    if choice == "1":
        print("\n⚠️  Update cookies in the code first!")
        # example_manual_cookies()
    elif choice == "2":
        example_load_from_file()
    elif choice == "3":
        print("\n⚠️  Update cookies in the code first!")
        # example_multiple_users()
    elif choice == "4":
        example_interactive()
    elif choice == "5":
        print("\n⚠️  Update cookies in the code first!")
        # example_step_by_step()
    elif choice == "6":
        example_cookie_management()
    else:
        print("Exiting...")
