import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://client.xreg.site/_next/static/chunks/1uh_4jb-tc7zm.js"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
    content = res.read().decode('utf-8', errors='ignore')

    # Look around /api/happ
    for m in re.finditer(r'/api/happ', content):
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + 200)
        print("=== /api/happ context ===")
        print(content[start:end].encode('ascii', 'ignore').decode())

    # Look around /api/redeem
    for m in re.finditer(r'/api/redeem', content):
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + 200)
        print("=== /api/redeem context ===")
        print(content[start:end].encode('ascii', 'ignore').decode())

    # Look around /api/features
    for m in re.finditer(r'/api/features', content):
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + 200)
        print("=== /api/features context ===")
        print(content[start:end].encode('ascii', 'ignore').decode())
