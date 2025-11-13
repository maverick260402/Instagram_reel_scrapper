import requests
import json
import zstandard as zstd  # pip install zstandard
import gzip, brotli, zlib
from pathlib import Path

url = "https://www.instagram.com/graphql/query"

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
    "variables": '{"data":{"include_feed_video":true,"page_size":12,"target_user_id":"8713286"},"first":3,"last":null}',
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
    "referer": "https://www.instagram.com/sabrinacarpenter/reels/",
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

# Decode, print nicely and write output to response.json
output_path = Path(__file__).parent / "response_2.json"
try:
    text = content.decode("utf-8")
    data = json.loads(text)
    pretty = json.dumps(data, indent=4)
    print(pretty)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Wrote JSON to {output_path}")
except Exception:
    # Not valid JSON or decode failed — show a preview and save raw text
    print("Raw Text (first 500 bytes):")
    print(content[:500])
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception:
        text = content.decode("latin-1", errors="replace")
    out = {"raw": text}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=4)
    print(f"Wrote raw text to {output_path}")
