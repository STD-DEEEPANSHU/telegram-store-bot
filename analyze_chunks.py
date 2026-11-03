import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_url = "https://client.xreg.site"
chunks = [
    "/_next/static/chunks/1uh_4jb-tc7zm.js",
    "/_next/static/chunks/1y_plgatmp3ld.js",
    "/_next/static/chunks/2r_6q3fjlp2qe.js",
    "/_next/static/chunks/20gq4cf8-8ujx.js",
    "/_next/static/chunks/1e8mgucsa9vec.js",
    "/_next/static/chunks/turbopack-02gt9s53ovwim.js",
    "/_next/static/chunks/0-untqzof86ch.js"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for chunk in chunks:
    url = base_url + chunk
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            content = res.read().decode('utf-8', errors='ignore')
            print(f"\n==========================================")
            print(f"CHUNK: {chunk} (Size: {len(content)} bytes)")
            print(f"==========================================")

            # Look for API endpoints
            apis = set(re.findall(r'["\'](/api/[^"\']+)["\']', content))
            if apis:
                print("API endpoints found:", apis)

            # Look for fetch/axios calls
            fetches = re.findall(r'(?:fetch|post|get)\s*\(\s*["\']([^"\']+)["\']', content)
            if fetches:
                print("Fetch calls:", set(fetches)[:10])

            # Look for brands or domains
            domains = set(re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content))
            if domains:
                print("External domains:", domains)

            # Look for feature names
            keywords = ["tunnel", "match", "license", "hwid", "device", "status", "features", "brand", "brandName", "aim", "esp", "recoil", "inject"]
            found_keywords = {}
            for kw in keywords:
                matches = re.findall(rf'["\'][^"\']*{kw}[^"\']*["\']', content, re.IGNORECASE)
                if matches:
                    found_keywords[kw] = len(matches)
            print("Keyword occurrences:", found_keywords)

            # Print some strings related to brand or config
            brand_strings = re.findall(r'["\'][^"\']*(?:xreg|brand|tenant)[^"\']*["\']', content, re.IGNORECASE)
            if brand_strings:
                print("Sample brand strings:", list(set(brand_strings))[:15])

    except Exception as e:
        print(f"Error fetching {chunk}: {e}")
