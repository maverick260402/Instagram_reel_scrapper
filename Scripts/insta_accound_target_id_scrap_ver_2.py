import requests
import re
import brotli  # pip install brotli

url = "https://www.instagram.com/sabrinacarpenter/reels"

headers = {
    "authority": "www.instagram.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'datr=pHBEaHK8sOX4LJjDob8KiA_y; ig_did=F8B0AADE-9E90-4C02-AB79-048A7192D338; ig_nrcb=1; mid=aExmxwALAAGU12v9xytF4YVZLFyL; dpr=1.25; csrftoken=lMEEbCVayqAAwpUbv7ZwluP94YjdFrGE; ds_user_id=77967696629; sessionid=77967696629%3AnUSwlOVPJTAG4f%3A19%3AAYhBASiMO5ZqbOKLyYQWl70OC2-7hsNYpBAustdpiA; ps_l=1; ps_n=1; rur="RVA\\05477967696629\\0541794074786:01fe487a7e3cdfeca9a2c71d2dd4131bf7cb6dfb4eccd7fa1602feb81106008b4158cb54"; wd=690x730',
    "dpr": "1.25",
    "sec-ch-prefers-color-scheme": "light",
    "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.125", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.125"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "viewport-width": "690",
}

# Step 1: Fetch HTML (binary response)
response = requests.get(url, headers=headers)

# Step 2: Decode Brotli if needed
encoding = response.headers.get("Content-Encoding", "")
if "br" in encoding:
    html = brotli.decompress(response.content).decode("utf-8", errors="ignore")
elif "gzip" in encoding:
    import gzip
    html = gzip.decompress(response.content).decode("utf-8", errors="ignore")
else:
    html = response.text

# Step 3: Search for target_id
match = re.search(r'"target_id"\s*:\s*"(\d+)"', html)
if match:
    target_id = match.group(1)
    print(f"✅ Found target_id: {target_id}")
else:
    print("⚠️ target_id not found in decoded HTML.")
