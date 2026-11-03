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
    print("Chunk length:", len(content))

    # Find API endpoints
    apis = set(re.findall(r'["\'](/api/[^"\']+)["\']', content))
    print("APIs:", apis)

    # Find URLs
    urls = set(re.findall(r'https?://[a-zA-Z0-9.-]+[^\s"\'<>]*', content))
    print("URLs:", urls)

    # Find all strings in content
    strings = re.findall(r'"([^"\\]{3,100})"', content)
    interesting = [s for s in strings if any(k in s.lower() for k in ['key', 'auth', 'brand', 'tunnel', 'device', 'hwid', 'login', 'token', 'user', 'session', 'panel', 'match'])]
    print("Interesting strings count:", len(interesting))
    for s in list(set(interesting))[:40]:
        print(" -", s)
