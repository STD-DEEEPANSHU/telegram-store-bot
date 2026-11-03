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

    # Look for feature definitions
    features_pattern = re.findall(r'\{[^{}]*(?:name|label|desc|icon|key|type|id|min|max|default)[^{}]*aimhack[^{}]*\}', content, re.IGNORECASE)
    print("Features around aimhack:", len(features_pattern))
    for fp in features_pattern[:5]:
        print(" ->", fp.encode('ascii', 'ignore').decode())

    # Find labels of features
    labels = re.findall(r'label:\s*["\']([^"\']+)["\']', content)
    print("\nLabels found:")
    for l in list(set(labels)):
        print(" *", l.encode('ascii', 'ignore').decode())
