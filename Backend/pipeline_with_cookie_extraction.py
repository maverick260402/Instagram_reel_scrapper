"""
Pipeline with automatic cookie extraction and retry logic.
This script wraps the original pipeline.py functions and injects fresh cookies.
"""

import sys
from pathlib import Path
import time

# Add Backend directory to path to import modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from playwright_cookie_extractor import extract_instagram_cookie, get_latest_cookie
import requests
import json
import re
import zstandard as zstd
import gzip
import brotli
import zlib
import pandas as pd


# ==================== CONFIGURATION ====================
# Set your Instagram credentials here
INSTAGRAM_EMAIL = "jigglyphilcam@gmail.com"  # TODO: Set your Instagram email/username
INSTAGRAM_PASSWORD = "Maverick15#"  # TODO: Set your Instagram password

# If credentials are empty, prompt user
if not INSTAGRAM_EMAIL or not INSTAGRAM_PASSWORD:
    print("⚠️ Instagram credentials not set in script.")
    INSTAGRAM_EMAIL = input("Enter Instagram email/username: ")
    INSTAGRAM_PASSWORD = input("Enter Instagram password: ")
# =======================================================


def extract_cookie_value(cookie_string: str, key: str) -> str:
    """
    Extract a specific cookie value from cookie string.

    Args:
        cookie_string: Full cookie string (name=value; name=value; ...)
        key: Cookie name to extract

    Returns:
        Cookie value or empty string if not found
    """
    parts = cookie_string.split('; ')
    for part in parts:
        if '=' in part:
            name, value = part.split('=', 1)
            if name == key:
                return value
    return ""


class CookieManager:
    """Manages cookie extraction and caching"""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._current_cookie = None

    def get_cookie(self, force_refresh: bool = False) -> str:
        """
        Get cookie string. Loads from today's file if exists,
        otherwise extracts fresh cookie using Playwright.
        """
        if force_refresh or not self._current_cookie:
            print("\n" + "="*80)
            print("🔑 EXTRACTING INSTAGRAM COOKIES")
            print("="*80)
            self._current_cookie = extract_instagram_cookie(
                self.email,
                self.password,
                force_refresh=force_refresh
            )
            print("✔ Cookie ready for use")
            print("="*80 + "\n")

        return self._current_cookie


# Initialize cookie manager
cookie_manager = CookieManager(INSTAGRAM_EMAIL, INSTAGRAM_PASSWORD)


def get_target_id_with_cookie(username: str, cookie_string: str):
    """
    Modified version of get_target_id that uses provided cookie.
    """
    url = f"https://www.instagram.com/{username}/reels/"

    headers = {
        "authority": "www.instagram.com",
        "cookie": cookie_string,  # Injected cookie
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    html = response.text

    target_id_match = re.search(r'"target_id"\s*:\s*"?(\d+)"?', html)

    if target_id_match:
        target_id = target_id_match.group(1)
        print(f"✅ Found target_id: {target_id}")
    else:
        print("⚠️ Could not find target_id in the page.")
        target_id = None

    return target_id


def fetch_reels_paginated_with_cookie(
    target_id,
    username: str,
    cookie_string: str,
    desired_count: int = 20,
    sleep_seconds: float = 1.0,
    max_per_page: int = 50
):
    """
    Modified version of fetch_reels_paginated that uses provided cookie.
    """
    url = "https://www.instagram.com/graphql/query"

    accumulated_edges = []
    cursor = None
    last_page_info = {}

    # Extract dynamic values from cookie
    csrftoken = extract_cookie_value(cookie_string, 'csrftoken')
    ds_user_id = extract_cookie_value(cookie_string, 'ds_user_id')

    print(f">>> Using csrftoken: {csrftoken}")
    print(f">>> Using ds_user_id: {ds_user_id}")
    print(f">>> Cookie string length: {len(cookie_string)}")

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
        "content-length": "1490",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": cookie_string,  # Injected cookie
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
        "x-csrftoken": csrftoken,  # Dynamically extracted from cookie
        "x-fb-friendly-name": "PolarisProfileReelsTabContentQuery",
        "x-fb-lsd": "xa_3XLBDc95COAGnE9hhQy",
        "x-ig-app-id": "936619743392459",
        "x-root-field-name": "xdt_api__v1__clips__user__connection_v2",
    }

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

        print(f"Requesting page: want={page_size} after={cursor} (collected={len(accumulated_edges)})")
        response = requests.post(url, headers=headers, data=payload)
        print(f"  -> status: {response.status_code}")
        print(response)
        content = response.content
        encoding = response.headers.get("content-encoding", "").lower()
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
            print("⚠️ Decompression failed:", e)

        try:
            text = content.decode("utf-8", errors="replace")
            data = json.loads(text)
        except Exception:
            print("⚠️ Failed to parse JSON for a page, stopping pagination.")
            snippet = content[:1000]
            try:
                print("Response snippet:", snippet.decode("utf-8", errors="replace"))
            except Exception:
                print("(binary response)")
            break

        connection = data.get("data", {}).get("xdt_api__v1__clips__user__connection_v2", {})
        edges = connection.get("edges", [])
        page_info = connection.get("page_info", {})

        if not edges:
            break

        print(f"  -> edges on this page: {len(edges)}")
        accumulated_edges.extend(edges)
        last_page_info = page_info or last_page_info

        if not page_info.get("has_next_page"):
            print("  -> no next page")
            break

        cursor = page_info.get("end_cursor")
        time.sleep(sleep_seconds)

    # Write combined result
    repo_root = Path(__file__).resolve().parent
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

    print(f"Wrote combined JSON with {len(accumulated_edges)} edges to {output_path}")
    return output_path


def extract_metadata_to_csv(meta_output_path: str) -> pd.DataFrame:
    """
    Extract metadata from JSON and save to CSV.
    Same as get_meta_data() from original pipeline.
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

    csv_path = Path(meta_output_path).parent / "scrapped_data.csv"
    df.to_csv(csv_path, index=False)

    return df


def scrape_user_with_retry(username: str, desired_count: int = 20, sleep_seconds: float = 3.0, max_per_page: int = 50):
    """
    Scrape a user's reels with automatic cookie refresh and retry on failure.

    Returns:
        dict with status and results
    """
    retry_count = 0
    max_retries = 1

    while retry_count <= max_retries:
        try:
            # Get cookie (uses cached cookie or extracts fresh)
            cookie_string = cookie_manager.get_cookie(force_refresh=(retry_count > 0))

            print(f"\n{'='*80}")
            print(f"📊 SCRAPING USER: {username}")
            print(f"{'='*80}\n")

            # Get target ID
            print(f"Step 1/3: Getting target_id for {username}...")
            target_id = get_target_id_with_cookie(username, cookie_string)

            if not target_id:
                return {
                    "username": username,
                    "status": "failed",
                    "error": "Could not find target_id"
                }

            print(f"✔ Target ID: {target_id}\n")

            # Fetch reels
            print(f"Step 2/3: Fetching {desired_count} reels...")
            meta_output_path = fetch_reels_paginated_with_cookie(
                target_id,
                username,
                cookie_string,
                desired_count=desired_count,
                sleep_seconds=sleep_seconds,
                max_per_page=max_per_page
            )

            if not meta_output_path:
                raise Exception("Failed to fetch reels metadata")

            print(f"✔ Meta data saved to: {meta_output_path}\n")

            # Extract to CSV
            print(f"Step 3/3: Extracting data to CSV...")
            df_result = extract_metadata_to_csv(meta_output_path)
            csv_path = Path(meta_output_path).parent / "scrapped_data.csv"

            print(f"✔ CSV saved to: {csv_path}")
            print(f"✔ Total reels scraped: {len(df_result)}")

            return {
                "username": username,
                "status": "success",
                "reels_scraped": len(df_result),
                "csv_path": str(csv_path),
                "json_path": str(meta_output_path)
            }

        except Exception as e:
            print(f"\n❌ Error scraping {username}: {e}")

            if retry_count < max_retries:
                print(f"\n🔄 RETRYING with fresh cookies (Attempt {retry_count + 2}/{max_retries + 1})...")
                retry_count += 1
            else:
                print(f"\n❌ Failed after {max_retries + 1} attempts")
                return {
                    "username": username,
                    "status": "failed",
                    "error": str(e)
                }


def main():
    """
    Main function to scrape multiple users.
    """
    print("\n" + "="*80)
    print("🚀 INSTAGRAM REEL SCRAPER WITH AUTO COOKIE MANAGEMENT")
    print("="*80 + "\n")

    # Define usernames to scrape
    usernames = ["ajaydevgn"]  # Modify this list as needed

    # Configuration
    desired_count = 50  # Number of reels per user
    sleep_seconds = 3.0  # Sleep between requests
    max_per_page = 12    # Max reels per page

    results = []

    for username in usernames:
        result = scrape_user_with_retry(
            username,
            desired_count=desired_count,
            sleep_seconds=sleep_seconds,
            max_per_page=max_per_page
        )
        results.append(result)

        # Print result summary
        print(f"\n{'='*80}")
        if result["status"] == "success":
            print(f"✅ SUCCESS: {username} - {result['reels_scraped']} reels")
            print(f"   CSV: {result['csv_path']}")
        else:
            print(f"❌ FAILED: {username} - {result['error']}")
        print(f"{'='*80}\n")

        # Sleep between users
        if username != usernames[-1]:
            print(f"⏳ Sleeping for 5 seconds before next user...\n")
            time.sleep(5)

    # Final summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(results)}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
