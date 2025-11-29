# -*- coding: utf-8 -*-
"""
Instagram Cookie Utility
Provides methods to obtain and manage Instagram cookies for scraping
"""

import requests
import json
import time
from typing import Dict, Optional


class InstagramCookieManager:
    """Manage Instagram cookies for authenticated requests"""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.instagram.com"

    def get_basic_cookies(self) -> Dict[str, str]:
        """
        Get basic unauthenticated cookies from Instagram homepage
        These include: datr, ig_did, ig_nrcb, mid, csrftoken

        NOTE: These cookies alone are NOT sufficient for scraping user data.
        You need sessionid which requires authentication.

        Returns:
            Dict of cookie name: value pairs
        """
        try:
            print("= Requesting basic cookies from Instagram...")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            response = self.session.get(self.base_url, headers=headers, timeout=10)
            response.raise_for_status()

            cookies = self.session.cookies.get_dict()

            print(" Basic cookies obtained:")
            for name, value in cookies.items():
                print(f"   {name}: {value[:20]}..." if len(value) > 20 else f"   {name}: {value}")

            return cookies

        except Exception as e:
            print(f"L Error getting basic cookies: {e}")
            return {}

    def login_and_get_cookies(self, username: str, password: str) -> Optional[Dict[str, str]]:
        """
        Login to Instagram and obtain authenticated cookies

        WARNING: Instagram has strong bot detection. This method may not work reliably.
        Consider using browser extension method instead (see print_browser_instructions)

        Args:
            username: Instagram username
            password: Instagram password

        Returns:
            Dict of cookies if successful, None otherwise
        """
        try:
            print(f"= Attempting to login as {username}...")

            # First get basic cookies and csrf token
            self.get_basic_cookies()
            csrf_token = self.session.cookies.get('csrftoken')

            if not csrf_token:
                print("L Failed to get CSRF token")
                return None

            # Prepare login data
            login_url = f"{self.base_url}/accounts/login/ajax/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "X-CSRFToken": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/accounts/login/",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {
                "username": username,
                "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
                "queryParams": "{}",
                "optIntoOneTap": "false"
            }

            response = self.session.post(login_url, headers=headers, data=data, timeout=10)
            result = response.json()

            if result.get("authenticated"):
                cookies = self.session.cookies.get_dict()

                if 'sessionid' in cookies:
                    print(" Login successful! Authenticated cookies obtained:")
                    print(f"   sessionid: {cookies['sessionid'][:20]}...")
                    return cookies
                else:
                    print("� Login responded as authenticated but no sessionid found")
                    return None
            else:
                print(f"L Login failed: {result.get('message', 'Unknown error')}")
                if result.get('two_factor_required'):
                    print("   2FA is enabled. Cannot automate login with 2FA.")
                return None

        except Exception as e:
            print(f"L Error during login: {e}")
            return None

    def format_cookie_string(self, cookies: Dict[str, str]) -> str:
        """
        Format cookies dict into a string for use in headers

        Args:
            cookies: Dict of cookie name: value pairs

        Returns:
            Cookie string in format "name1=value1; name2=value2; ..."
        """
        return "; ".join([f"{name}={value}" for name, value in cookies.items()])

    def save_cookies_to_file(self, cookies: Dict[str, str], filename: str = "instagram_cookies.json"):
        """Save cookies to a JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f" Cookies saved to {filename}")
        except Exception as e:
            print(f"L Error saving cookies: {e}")

    def load_cookies_from_file(self, filename: str = "instagram_cookies.json") -> Optional[Dict[str, str]]:
        """Load cookies from a JSON file"""
        try:
            with open(filename, 'r') as f:
                cookies = json.load(f)
            print(f" Cookies loaded from {filename}")
            return cookies
        except FileNotFoundError:
            print(f"L File {filename} not found")
            return None
        except Exception as e:
            print(f"L Error loading cookies: {e}")
            return None

    @staticmethod
    def print_browser_instructions():
        """
        Print instructions for manually extracting cookies from browser
        This is the MOST RELIABLE method for getting authenticated cookies
        """
        print("""
TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW
Q          HOW TO GET INSTAGRAM COOKIES FROM BROWSER            Q
ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]

METHOD 1: Using Browser Developer Tools (Recommended)


1. Open Instagram in your browser and LOGIN to your account

2. Open Developer Tools:
   - Chrome/Edge: Press F12 or Ctrl+Shift+I
   - Firefox: Press F12 or Ctrl+Shift+I

3. Go to the "Application" tab (Chrome/Edge) or "Storage" tab (Firefox)

4. In the left sidebar:
   - Expand "Cookies"
   - Click on "https://www.instagram.com"

5. You'll see a list of cookies. Find and copy these important ones:

   ESSENTIAL COOKIES (Must have):
   
   " sessionid     � Most important! This authenticates you
   " csrftoken     � Required for POST requests
   " ds_user_id    � Your user ID

   ADDITIONAL COOKIES (Recommended):
   
   " mid           � Machine ID
   " ig_did        � Instagram device ID
   " datr          � Device tracking
   " rur           � Region/routing
   " ig_nrcb       � Not a robot check bypass

6. Format them as a cookie string:

   sessionid=YOUR_SESSION_ID; csrftoken=YOUR_CSRF_TOKEN; ds_user_id=YOUR_USER_ID; mid=YOUR_MID; ig_did=YOUR_IG_DID; datr=YOUR_DATR; rur=YOUR_RUR


METHOD 2: Using EditThisCookie Extension (Easier)


1. Install "EditThisCookie" extension:
   - Chrome: https://chrome.google.com/webstore (search "EditThisCookie")
   - Firefox: https://addons.mozilla.org (search "EditThisCookie")

2. Login to Instagram in your browser

3. Click the EditThisCookie extension icon

4. Click "Export" button (exports cookies as JSON)

5. Use the exported JSON in your code


METHOD 3: Using This Script


1. Run this script with your credentials:

   from getCookies import InstagramCookieManager

   manager = InstagramCookieManager()
   cookies = manager.login_and_get_cookies("your_username", "your_password")

   if cookies:
       cookie_string = manager.format_cookie_string(cookies)
       print(cookie_string)

�  WARNING: Automated login may trigger Instagram's bot detection!
   Browser method is more reliable for production use.


IMPORTANT NOTES:


" Cookies expire after ~90 days of inactivity
" Using the same cookies from multiple IPs may trigger security alerts
" Keep your cookies private (they give full access to your account)
" For production, consider using Instagram's official API instead

ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]
        """)


def main():
    """Example usage"""

    print("Instagram Cookie Manager")
    print("=" * 60)
    print()
    print("Choose an option:")
    print("1. Get basic cookies (unauthenticated)")
    print("2. Login and get cookies (may not work due to bot detection)")
    print("3. Show browser extraction instructions (RECOMMENDED)")
    print()

    choice = input("Enter choice (1-3): ").strip()

    manager = InstagramCookieManager()

    if choice == "1":
        print()
        cookies = manager.get_basic_cookies()
        if cookies:
            print("\n=� Cookie string format:")
            print(manager.format_cookie_string(cookies))

            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == 'y':
                manager.save_cookies_to_file(cookies)

    elif choice == "2":
        print()
        print("�  WARNING: This may not work due to Instagram's bot detection")
        print("   Consider using the browser method instead (option 3)")
        print()
        username = input("Instagram username: ").strip()
        password = input("Instagram password: ").strip()

        print()
        cookies = manager.login_and_get_cookies(username, password)

        if cookies:
            print("\n=� Cookie string format:")
            print(manager.format_cookie_string(cookies))

            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == 'y':
                manager.save_cookies_to_file(cookies)
        else:
            print("\n=� TIP: Use option 3 to learn how to get cookies from your browser")

    elif choice == "3":
        InstagramCookieManager.print_browser_instructions()

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
