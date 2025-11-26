import requests
import gzip
import brotli
import zlib
import json
from pathlib import Path
import zstandard as zstd  # pip install zstandard

url = "https://www.instagram.com/api/v1/media/3653386088336272837/info/"

headers = {
    "authority": "www.instagram.com",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",  # zstd included
    "accept-language": "en-US,en;q=0.9,hi;q=0.8",
    "cookie": "ds_user_id=5601622418; ; rur=\"RVA\\0545601622418\\0541794059836:01fe94ceb9c6168da517b5ea372c1593e2c32fe2ccfb6b494dae90537dd7c6b39ec98156\"",
    "referer": "https://www.instagram.com/reel/DKzb0p2oy3F/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "x-asbd-id": "359341",
    "x-csrftoken": "rtEaRSsAYdcaCYRdhNEQP_",
    "x-ig-app-id": "936619743392459",
    "x-ig-www-claim": "hmac.AR31HKj8b9KOUFrzc8p5I-I-sPA_NpZ-M5chsuYxDekGo-AL",
    "x-requested-with": "XMLHttpRequest",
    "x-web-session-id": "cet4aj:9k671o:4d0qiq",
}

response = requests.get(url, headers=headers)
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

# Decode as UTF-8 or fallback
try:
    text = content.decode("utf-8")
except UnicodeDecodeError:
    text = content.decode("latin-1", errors="replace")

# Pretty print if JSON
# Pretty print if JSON and write output to response.json
output_path = Path(__file__).parent / "response.json"
try:
    data = json.loads(text)
    pretty = json.dumps(data, indent=4)
    print(pretty)
    # Write JSON to file (pretty, utf-8)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Wrote JSON to {output_path}")
except Exception:
    # Not valid JSON, write raw text under the key "raw"
    print("Raw Text:\n", text)
    out = {"raw": text}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=4)
    print(f"Wrote raw text to {output_path}")