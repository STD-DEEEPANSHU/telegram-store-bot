import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://client.xreg.site/_next/static/chunks/1uh_4jb-tc7zm.js"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
    content = res.read().decode('utf-8', errors='ignore')

    # Find brand config
    brand_matches = re.findall(r'BRAND\s*=\s*\{[^}]+\}', content)
    print("BRAND matches count:", len(brand_matches))
    for bm in brand_matches[:10]:
        print("BRAND config snippet:", bm[:300])

    # Find features list
    features_matches = re.findall(r'features\s*:\s*\[[^\]]+\]', content)
    print("Features matches count:", len(features_matches))
    for fm in features_matches[:5]:
        print("Features snippet:", fm[:300])

    # Search for all mentions of happ proxy or tunnel
    happ_matches = re.findall(r'[^;{}]{0,50}(?:happ|tunnel|v2ray|shadowsocks|proxy)[^;{}]{0,50}', content, re.IGNORECASE)
    print(f"\nHapp / Tunnel mentions count: {len(happ_matches)}")
    for hm in list(set(happ_matches))[:20]:
        print(" ->", hm.strip())
