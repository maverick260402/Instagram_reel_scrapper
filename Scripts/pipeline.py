import requests
import json
import re
import zstandard as zstd  # pip install zstandard
import gzip, brotli, zlib
from pathlib import Path
import pandas as pd
import os


def get_target_id(username: str):

    url = f"https://www.instagram.com/{username}/reels/"

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

    return target_id

def get_meta_date(target_id, username: str):
    url = "https://www.instagram.com/graphql/query"

    # Build the variables payload safely using json.dumps to avoid f-string format issues
    variables_obj = {
        "data": {
            "include_feed_video": True,
            "page_size": 12,
            "target_user_id": str(target_id)
        },
        "first": 3,
        "last": None
    }
    variables_json = json.dumps(variables_obj)

    payload = {
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
    "variables": variables_json,
    "doc_id": "9905035666198614"
    }

    headers = {
        "authority": "www.instagram.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "1874",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "datr=pHBEaHK8sOX4LJjDob8KiA_y; ig_did=F8B0AADE-9E90-4C02-AB79-048A7192D338; ig_nrcb=1; mid=aExmxwALAAGU12v9xytF4YVZLFyL; dpr=1.25; csrftoken=lMEEbCVayqAAwpUbv7ZwluP94YjdFrGE; ds_user_id=77967696629; sessionid=77967696629%3AnUSwlOVPJTAG4f%3A19%3AAYhBASiMO5ZqbOKLyYQWl70OC2-7hsNYpBAustdpiA; wd=690x730; rur=\"RVA\\05477967696629\\0541794072327:01fe0008fe9b3b028caa876476fa95aeaada35dcaa223b4d33675d9f0ba24ac80bec8b55\"",
        "origin": "https://www.instagram.com",
        "priority": "u=1, i",
        "referer": f"https://www.instagram.com/{username}/reels/",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-full-version-list": '"Google Chrome";v="141.0.7390.125", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.125"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-platform-version": '"19.0.0"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-bloks-version-id": "e931ff03adc522742d788ba659da2ded4fb760f51c8576b5cd93cdaf3987e4b0",
        "x-csrftoken": "lMEEbCVayqAAwpUbv7ZwluP94YjdFrGE",
        "x-fb-friendly-name": "PolarisProfileReelsTabContentQuery_connection",
        "x-fb-lsd": "E69Uy1mzZDPfOwhuzCVwEl",
        "x-ig-app-id": "936619743392459",
        "x-root-field-name": "xdt_api__v1__clips__user__connection_v2",
    }

    response = requests.post(url, headers=headers, data=payload)

    # Handle possible compression (zstd, br, gzip)
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

    # Save JSON into repository's output_json/<username>/meta_data.json
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "output_json" / username
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "meta_data.json"

    try:
        text = content.decode("utf-8")
        data = json.loads(text)
        pretty = json.dumps(data, indent=4)
        #print(pretty)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Wrote JSON to {output_path}")
    except Exception:
        # Not valid JSON or decode failed — show a preview and save raw text
        print("Raw Text (first 500 bytes):")
        #print(content[:500])
        try:
            text = content.decode("utf-8", errors="replace")
        except Exception:
            text = content.decode("latin-1", errors="replace")
        out = {"raw": text}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=4)
        print(f"Wrote raw text to {output_path}")

    return output_path
    
def get_meta_data(meta_output_path: str) -> pd.DataFrame:

    with open(meta_output_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Navigate to edges list
    edges = data.get("data", {}).get("xdt_api__v1__clips__user__connection_v2", {}).get("edges", [])

    # Extract required fields
    extracted_data = []
    for edge in edges:
        media = edge.get("node", {}).get("media", {})
        extracted_data.append({
            "pk": media.get("pk"),
            "code": media.get("code"),
            "play_count": media.get("play_count"),
            "comment_count": media.get("comment_count"),
            "like_count": media.get("like_count"),
            #"view_count": media.get("view_count"),
            "url": f'https://www.instagram.com/reel/{media.get("code")}/'
        })

    # Create DataFrame
    df = pd.DataFrame(extracted_data)

    # Define CSV path in same folder
    csv_path = os.path.join(os.path.dirname(meta_output_path), "scrapped_data.csv")
    df.to_csv(csv_path, index=False)

    return df

def main():
    username = "brut.india"
    target_id = get_target_id(username)
    if target_id:
        print(f"Target ID for {username}: {target_id}")
    else:
        print(f"Failed to retrieve Target ID for {username}.")

    meta_output_path = get_meta_date(target_id, username)
    if meta_output_path:
        print(f"Meta data saved to: {meta_output_path}")
        # Continue with the next steps in your pipeline
        df_result = get_meta_data(meta_output_path)
        print(df_result)
    else:
        print("Failed to retrieve meta data.")

if __name__ == "__main__":
    main()


