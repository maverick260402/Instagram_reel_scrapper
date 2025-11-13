import requests
import json
import re
from bs4 import BeautifulSoup  # pip install beautifulsoup4

url = "https://www.instagram.com/sabrinacarpenter/reels"

headers = {
    "authority": "www.instagram.com",  # Recommended
    # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "accept-encoding": "gzip, deflate, br, zstd",
    # "accept-language": "en-US,en;q=0.9",
    "cookie": 'datr=pHBEaHK8sOX4LJjDob8KiA_y; ig_did=F8B0AADE-9E90-4C02-AB79-048A7192D338; ig_nrcb=1; mid=aExmxwALAAGU12v9xytF4YVZLFyL; dpr=1.25; csrftoken=lMEEbCVayqAAwpUbv7ZwluP94YjdFrGE; ds_user_id=77967696629; sessionid=77967696629%3AnUSwlOVPJTAG4f%3A19%3AAYhBASiMO5ZqbOKLyYQWl70OC2-7hsNYpBAustdpiA; ps_l=1; ps_n=1; rur="RVA\\05477967696629\\0541794074786:01fe487a7e3cdfeca9a2c71d2dd4131bf7cb6dfb4eccd7fa1602feb81106008b4158cb54"; wd=690x730',  # ESSENTIAL
    # "dpr": "1.25",
    # "sec-ch-prefers-color-scheme": "light",
    # "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    # "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.125", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.125"',
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",  # Recommended for avoiding detection
    "sec-fetch-mode": "navigate",  # Recommended for avoiding detection
    "sec-fetch-site": "none",  # Recommended for avoiding detection
    "sec-fetch-user": "?1",  # Recommended for avoiding detection
    # "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",  # ESSENTIAL
    # "viewport-width": "690",
}

# Step 1: GET the page
response = requests.get(url, headers=headers)
html = response.text

# Step 2: Find the target_id in the HTML
target_id_match = re.search(r'"target_id"\s*:\s*"?(\d+)"?', html)

if target_id_match:
    target_id = target_id_match.group(1)
    print(f"✅ Found target_id: {target_id}")
else:
    print("⚠️ Could not find target_id in the page.")
    target_id = None


'''
# Step 3: Find the embedded JSON using regex or BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
scripts = soup.find_all("script", string=re.compile("window._sharedData"))

json_data = None
for script in scripts:
    match = re.search(r"window\._sharedData\s*=\s*(\{.*\});", script.string or "")
    if match:
        json_data = json.loads(match.group(1))
        break

# If window._sharedData not found, try looking for other JSON patterns
if not json_data:
    # Look for script tags containing JSON data
    all_scripts = soup.find_all("script", type="application/json")
    for script in all_scripts:
        try:
            json_data = json.loads(script.string)
            print(f"✅ Found JSON data in <script type='application/json'>")
            break
        except:
            continue
json_file_path = "Instagram_reel_scrapper/output_json/target_id/sabrinacarpenter/sabrinacarpenter_reels.json"
# Step 4: Save the JSON
if json_data:
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    print(f"✅ JSON data extracted and saved as '{json_file_path}'")
else:
    print("⚠️ Could not find embedded JSON data in the page.")
'''