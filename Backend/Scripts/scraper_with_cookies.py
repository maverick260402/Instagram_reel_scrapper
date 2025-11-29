# -*- coding: utf-8 -*-
"""
Instagram Reel Scraper with Dynamic Cookie Management
Integrates getCookies.py with pipeline scraping functionality
"""

import requests
import json
import re
import zstandard as zstd
import gzip
import brotli
import zlib
from pathlib import Path
import pandas as pd
import os
import time
from typing import Dict, Optional, List
from getCookies import InstagramCookieManager


class InstagramScraperWithCookies:
    """Instagram scraper that uses dynamically obtained cookies"""

    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        Initialize the scraper with cookies

        Args:
            cookies: Dictionary of Instagram cookies. If None, will prompt user to obtain cookies.
        """
        self.cookie_manager = InstagramCookieManager()
        self.cookies = cookies or {}
        self.cookie_string = ""
        self.csrftoken = ""

        if not self.cookies:
            print("\nNo cookies provided. You need to obtain cookies first.")
            self._obtain_cookies_interactive()
        else:
            self._update_cookie_string()

    def _obtain_cookies_interactive(self):
        """Interactive method to obtain cookies"""
        print("\n" + "="*60)
        print("COOKIE ACQUISITION")
        print("="*60)
        print("\nChoose how to obtain cookies:")
        print("1. Get basic cookies (unauthenticated - NOT RECOMMENDED)")
        print("2. Login with credentials (may fail due to bot detection)")
        print("3. I'll provide cookies manually (RECOMMENDED)")
        print()

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            print("\nWARNING: Basic cookies alone won't work for scraping.")
            print("You need authenticated cookies with sessionid.")
            proceed = input("Proceed anyway? (y/n): ").strip().lower()
            if proceed == 'y':
                self.cookies = self.cookie_manager.get_basic_cookies()
                self._update_cookie_string()

        elif choice == "2":
            print("\nWARNING: This may not work due to Instagram's bot detection")
            username = input("Instagram username: ").strip()
            password = input("Instagram password: ").strip()

            self.cookies = self.cookie_manager.login_and_get_cookies(username, password)
            if self.cookies:
                self._update_cookie_string()
                print("\nCookies obtained successfully!")
            else:
                print("\nLogin failed. Please use manual method (option 3)")
                self._manual_cookie_input()

        elif choice == "3":
            self._manual_cookie_input()
        else:
            print("Invalid choice. Exiting.")
            exit(1)

    def _manual_cookie_input(self):
        """Manually input cookie string"""
        print("\n" + "="*60)
        print("MANUAL COOKIE INPUT")
        print("="*60)
        InstagramCookieManager.print_browser_instructions()
        print("\n" + "="*60)
        print("\nPaste your cookie string here:")
        print("Format: sessionid=XXX; csrftoken=YYY; ds_user_id=ZZZ; ...")
        print()

        cookie_string = input("Cookie string: ").strip()

        if not cookie_string:
            print("ERROR: No cookie string provided. Exiting.")
            exit(1)

        # Parse cookie string into dict
        self.cookies = {}
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                self.cookies[name.strip()] = value.strip()

        # Verify essential cookies
        if 'sessionid' not in self.cookies:
            print("\nWARNING: sessionid not found in cookies!")
            print("Scraping will likely fail without it.")
            proceed = input("Continue anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                exit(1)

        self._update_cookie_string()
        print("\nCookies loaded successfully!")

    def _update_cookie_string(self):
        """Update the cookie string and extract csrftoken"""
        self.cookie_string = self.cookie_manager.format_cookie_string(self.cookies)
        self.csrftoken = self.cookies.get('csrftoken', '')

        # Print cookie summary
        print("\nCookie Summary:")
        print(f"  sessionid: {'✓ Present' if 'sessionid' in self.cookies else '✗ Missing (REQUIRED!)'}")
        print(f"  csrftoken: {'✓ Present' if 'csrftoken' in self.cookies else '✗ Missing'}")
        print(f"  ds_user_id: {'✓ Present' if 'ds_user_id' in self.cookies else '✗ Missing'}")
        print(f"  Total cookies: {len(self.cookies)}")

    def get_target_id(self, username: str) -> Optional[str]:
        """
        Get Instagram user's target_id from their profile page

        Args:
            username: Instagram username

        Returns:
            target_id string if found, None otherwise
        """
        url = f"https://www.instagram.com/{username}/reels/"

        headers = {
            "authority": "www.instagram.com",
            "cookie": self.cookie_string,
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            html = response.text

            target_id_match = re.search(r'"target_id"\s*:\s*"?(\d+)"?', html)

            if target_id_match:
                target_id = target_id_match.group(1)
                print(f"✅ Found target_id for {username}: {target_id}")
                return target_id
            else:
                print(f"⚠️ Could not find target_id for {username}")
                return None

        except Exception as e:
            print(f"❌ Error getting target_id for {username}: {e}")
            return None

    def fetch_reels_paginated(
        self,
        target_id: str,
        username: str,
        desired_count: int = 20,
        sleep_seconds: float = 3.0,
        max_per_page: int = 50
    ) -> Optional[Path]:
        """
        Fetch reels with pagination using dynamic cookies

        Args:
            target_id: Instagram user's target ID
            username: Instagram username
            desired_count: Number of reels to fetch
            sleep_seconds: Delay between requests
            max_per_page: Maximum reels per page

        Returns:
            Path to the saved JSON file, or None if failed
        """
        url = "https://www.instagram.com/graphql/query"

        accumulated_edges = []
        cursor = None
        last_page_info = {}

        # Base payload
        base_payload = {
            "av": "17841477778895962",
            "__d": "www",
            "__user": "0",
            "__a": "1",
            "__req": "1k",
            "__hs": "20399.HYP:instagram_web_pkg.2.1...0",
            "dpr": "1",
            "__ccg": "GOOD",
            "__rev": "1029561462",
            "__s": "1urb85:988u7l:9zj82a",
            "__hsi": "7570035321675026816",
            "__dyn": "7xeUjG1mxu1syUbFp41twWwIxu13wvoKewSAwHwNw9G2S7o2vwa24o0B-q1ew6ywaq0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9O1lwxwQzXwae4UaEW2G0AEco5G1Wxfxm16wUwtE1wEbUGdG1QwTU9UaQ0Lo6-3u2WE5B08-269wr86C1mgcEed6goK2O4Xxui2qi7E5y4UrwHwGwa6bBK4o16UsxWawOwgV84q2i",
            "__csr": "ghTiMjgmFNdgPsQn3tZOl5EyYIyanObnTGdWLjBbiDAyFUHGp2aChaCO4AjtqhKV8guvWtkmnBl5GC9zXCmnx6pbLAxvKmmAii4VFEOZyK9yUy8AFy8jt16KFVF_qAVaCyKqUGl4ybgGcCHyFZCoKbCALDyqxabyayoCdAwzAypqK-2G4oyi48-awXxa6E1eEjw05vvwioWaK7Q1k808lB9wyKfCg1o9oaAjiH80azy82xyVoSbwai0YUsw3dU2eU0ni80QQ8xii4sEeE4Rz62Sf80K8iwFg1SO4m0L8981jpRo2cwbi8gKOwfm0GP0Szm0eJ22mNU7h05FG3u01rbw1ilw50w1EPw0CFw4mw",
            "__hsdp": "g59_6Mi2FcI4u2sJ4FJH8lcxwhP912QD4RFNh2NhSg8EKiHsmtBoUklVN3N8cywyo-aA41BxaU5dd6g4LiwhO39osK3mjzpm26loeQ28UgDg6i11wLxu7875waOK485mq2abwWBwxwDwl9GG7E8EogkwjUaUco4Kbw3j40nO2-U3GwrUap80xy1zwSwoE5609AwLwh80HG2N061pU5y0HU611G",
            "__hblp": "0u4U4q1ZwFyU8pUdQ2e4V8SEiCxZ120GUngS9xt2ohBz6mEjBxC48-3K8BAyk4HzA5ooJ5GE8Q8CyWwkoWiAcwlUa8GqrFafz8C5UG4o-32A4oqod86WVaQuXwlpEy6oyE9oy8Gm269xSi7ocoO7EtAxx2Uy2y2q2KEO261byU1UEK1lw47ghw4MwVwLK3q0IU6-2CQ0RofU2OwjU4m7orxG2a3-3S4UW17w23obU4i1ow4Uw920zbCxe643C2O0zU5q2KtDVoaoO6oc8colwKDxi19S6o4e7E",
            "__sjsp": "g59_sj93UGjb17wDbharqO5j8o4sOggJ9NdqskgIktB22bACsmtBoUklaeK8gd61WK1jwmt0o888do",
            "__comet_req": "7",
            "fb_dtsg": "NAft_AfACbdIh8iliExT2KJdllUp2Jjo5HjZ6mpVsjbtmG0CLNb2PCg:17843683195144578:1762438082",
            "jazoest": "26331",
            "lsd": "E69Uy1mzZDPfOwhuzCVwEl",
            "__spin_r": "1029561462",
            "__spin_b": "trunk",
            "__spin_t": "1762536196",
            "__crn": "comet.igweb.PolarisProfileReelsTabRoute",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "PolarisProfileReelsTabContentQuery_connection",
            "server_timestamps": "true",
            "doc_id": "9905035666198614"
        }

        headers = {
            "authority": "www.instagram.com",
            "method": "POST",
            "path": "/graphql/query",
            "scheme": "https",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": self.cookie_string,
            "origin": "https://www.instagram.com",
            "priority": "u=1, i",
            "referer": f"https://www.instagram.com/{username}/reels/",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-full-version-list": '"Chromium";v="142.0.7444.176", "Google Chrome";v="142.0.7444.176", "Not_A Brand";v="99.0.0.0"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"19.0.0"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "x-asbd-id": "359341",
            "x-bloks-version-id": "e931ff03adc522742d788ba659da2ded4fb760f51c8576b5cd93cdaf3987e4b0",
            "x-csrftoken": self.csrftoken,
            "x-fb-friendly-name": "PolarisProfileReelsTabContentQuery",
            "x-fb-lsd": "xa_3XLBDc95COAGnE9hhQy",
            "x-ig-app-id": "936619743392459",
            "x-root-field-name": "xdt_api__v1__clips__user__connection_v2",
        }

        print(f"\n{'='*60}")
        print(f"STARTING PAGINATION for {username}")
        print(f"  Target count: {desired_count}")
        print(f"  Max per page: {max_per_page}")
        print(f"{'='*60}\n")

        while len(accumulated_edges) < desired_count:
            remaining = desired_count - len(accumulated_edges)
            page_size = min(max_per_page, remaining)

            variables_obj = {
                "data": {
                    "include_feed_video": True,
                    "page_size": page_size,
                    "target_user_id": str(target_id)
                },
                "first": page_size,
                "last": None
            }
            if cursor:
                variables_obj["after"] = cursor

            payload = dict(base_payload)
            payload["variables"] = json.dumps(variables_obj)

            print(f"📥 Requesting page: want={page_size}, after={cursor}, collected={len(accumulated_edges)}")

            try:
                response = requests.post(url, headers=headers, data=payload, timeout=30)
                print(f"   ✓ Status: {response.status_code}")

                if response.status_code != 200:
                    print(f"   ✗ Error: Received status code {response.status_code}")
                    print(f"   Response: {response.text[:500]}")
                    break

                content = response.content
                encoding = response.headers.get("content-encoding", "").lower()

                # Decompress
                try:
                    if "zstd" in encoding or "zstandard" in encoding:
                        dctx = zstd.ZstdDecompressor()
                        content = dctx.decompress(content)
                    elif "br" in encoding:
                        content = brotli.decompress(content)
                    elif "gzip" in encoding:
                        content = gzip.decompress(content)
                    elif "deflate" in encoding:
                        content = zlib.decompress(content)
                except Exception as e:
                    print(f"   ⚠️ Decompression failed: {e}")

                # Parse JSON
                try:
                    text = content.decode("utf-8", errors="replace")
                    data = json.loads(text)
                except Exception as e:
                    print(f"   ✗ Failed to parse JSON: {e}")
                    print(f"   Response snippet: {content[:1000]}")
                    break

                connection = data.get("data", {}).get("xdt_api__v1__clips__user__connection_v2", {})
                edges = connection.get("edges", [])
                page_info = connection.get("page_info", {})

                if not edges:
                    print("   → No more edges found")
                    break

                print(f"   → Got {len(edges)} edges")
                accumulated_edges.extend(edges)
                last_page_info = page_info or last_page_info

                if not page_info.get("has_next_page"):
                    print("   → No next page")
                    break

                cursor = page_info.get("end_cursor")

                # Sleep before next request
                if len(accumulated_edges) < desired_count:
                    print(f"   💤 Sleeping for {sleep_seconds}s...")
                    time.sleep(sleep_seconds)

            except Exception as e:
                print(f"   ✗ Request failed: {e}")
                break

        # Save to file
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent
        output_dir = repo_root / "output_json" / username
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "meta_data.json"

        combined = {
            "data": {
                "xdt_api__v1__clips__user__connection_v2": {
                    "edges": accumulated_edges,
                    "page_info": last_page_info
                }
            }
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=4)

        print(f"\n✅ Wrote combined JSON with {len(accumulated_edges)} edges to {output_path}")
        return output_path

    def extract_reel_data(self, meta_output_path: Path) -> pd.DataFrame:
        """
        Extract reel data from JSON and save to CSV

        Args:
            meta_output_path: Path to the meta_data.json file

        Returns:
            DataFrame with extracted reel data
        """
        with open(meta_output_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        edges = data.get("data", {}).get("xdt_api__v1__clips__user__connection_v2", {}).get("edges", [])

        extracted_data = []
        for edge in edges:
            media = edge.get("node", {}).get("media", {})

            clips_tab_pinned_user_ids = media.get("clips_tab_pinned_user_ids", [])
            is_pinned = "Yes" if clips_tab_pinned_user_ids else "No"

            extracted_data.append({
                "pk": media.get("pk"),
                "code": media.get("code"),
                "play_count": media.get("play_count"),
                "comment_count": media.get("comment_count"),
                "like_count": media.get("like_count"),
                "is_reel_pinned": is_pinned,
                "url": f'https://www.instagram.com/reel/{media.get("code")}/'
            })

        df = pd.DataFrame(extracted_data)

        csv_path = os.path.join(os.path.dirname(meta_output_path), "scrapped_data.csv")
        df.to_csv(csv_path, index=False)

        print(f"✅ Saved CSV to {csv_path}")
        print(f"\nDataFrame Preview:")
        print(df.head())

        return df

    def scrape_user(
        self,
        username: str,
        reel_count: int = 20,
        sleep_seconds: float = 3.0
    ) -> Optional[pd.DataFrame]:
        """
        Complete scraping workflow for a single user

        Args:
            username: Instagram username
            reel_count: Number of reels to scrape
            sleep_seconds: Delay between requests

        Returns:
            DataFrame with scraped data, or None if failed
        """
        print(f"\n{'='*60}")
        print(f"SCRAPING USER: {username}")
        print(f"{'='*60}")

        # Step 1: Get target ID
        target_id = self.get_target_id(username)
        if not target_id:
            print(f"✗ Failed to get target_id for {username}")
            return None

        # Step 2: Fetch reels
        meta_path = self.fetch_reels_paginated(
            target_id,
            username,
            desired_count=reel_count,
            sleep_seconds=sleep_seconds,
            max_per_page=50
        )

        if not meta_path:
            print(f"✗ Failed to fetch reels for {username}")
            return None

        # Step 3: Extract data
        df = self.extract_reel_data(meta_path)

        print(f"\n✅ Successfully scraped {len(df)} reels for {username}")
        return df

    def scrape_multiple_users(
        self,
        usernames: List[str],
        reel_count: int = 20,
        sleep_between_users: float = 5.0,
        sleep_between_requests: float = 3.0
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Scrape multiple users sequentially

        Args:
            usernames: List of Instagram usernames
            reel_count: Number of reels per user
            sleep_between_users: Delay between users
            sleep_between_requests: Delay between requests

        Returns:
            Dictionary mapping username to DataFrame
        """
        results = {}

        print(f"\n{'#'*60}")
        print(f"BATCH SCRAPING: {len(usernames)} users")
        print(f"{'#'*60}")

        for idx, username in enumerate(usernames, 1):
            print(f"\n[{idx}/{len(usernames)}] Processing: {username}")

            df = self.scrape_user(username, reel_count, sleep_between_requests)
            results[username] = df

            # Sleep between users (except after last one)
            if idx < len(usernames) and sleep_between_users > 0:
                print(f"\n💤 Sleeping for {sleep_between_users}s before next user...")
                time.sleep(sleep_between_users)

        # Print summary
        print(f"\n{'#'*60}")
        print("SCRAPING SUMMARY")
        print(f"{'#'*60}")
        successful = sum(1 for df in results.values() if df is not None)
        failed = len(usernames) - successful
        print(f"✓ Successful: {successful}/{len(usernames)}")
        print(f"✗ Failed: {failed}/{len(usernames)}")

        return results


def main():
    """Main function with interactive menu"""

    print("\n" + "="*60)
    print("INSTAGRAM REEL SCRAPER WITH DYNAMIC COOKIES")
    print("="*60)

    # Initialize scraper (will prompt for cookies if needed)
    scraper = InstagramScraperWithCookies()

    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Scrape single user")
        print("2. Scrape multiple users")
        print("3. Update cookies")
        print("4. Save current cookies to file")
        print("5. Load cookies from file")
        print("6. Exit")
        print()

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            username = input("\nEnter Instagram username: ").strip()
            reel_count = input("Number of reels to scrape (default 20): ").strip()
            reel_count = int(reel_count) if reel_count else 20

            scraper.scrape_user(username, reel_count)

        elif choice == "2":
            print("\nEnter usernames (comma-separated):")
            usernames_input = input("Usernames: ").strip()
            usernames = [u.strip() for u in usernames_input.split(',') if u.strip()]

            if not usernames:
                print("No usernames provided.")
                continue

            reel_count = input("Number of reels per user (default 20): ").strip()
            reel_count = int(reel_count) if reel_count else 20

            scraper.scrape_multiple_users(usernames, reel_count)

        elif choice == "3":
            print("\nUpdating cookies...")
            scraper._obtain_cookies_interactive()

        elif choice == "4":
            filename = input("\nFilename (default: instagram_cookies.json): ").strip()
            filename = filename if filename else "instagram_cookies.json"
            scraper.cookie_manager.save_cookies_to_file(scraper.cookies, filename)

        elif choice == "5":
            filename = input("\nFilename (default: instagram_cookies.json): ").strip()
            filename = filename if filename else "instagram_cookies.json"
            cookies = scraper.cookie_manager.load_cookies_from_file(filename)
            if cookies:
                scraper.cookies = cookies
                scraper._update_cookie_string()

        elif choice == "6":
            print("\nExiting...")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
