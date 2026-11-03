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

    # Look for feature keys, sliders, toggles
    feature_keys = re.findall(r'["\']([a-zA-Z0-9_-]*(?:aim|head|fov|esp|location|damage|recoil|speed|bullet|magic|wall|antenna|bypass|silent)[a-zA-Z0-9_-]*)["\']', content, re.IGNORECASE)
    print("Feature keys found:", set(feature_keys))

    # Look for UI tabs / routes / sections
    tabs = re.findall(r'["\']([a-zA-Z0-9_-]*(?:tunnel|features|status|settings|license|device|profile|match)[a-zA-Z0-9_-]*)["\']', content, re.IGNORECASE)
    print("Tabs/Sections found:", set(tabs)[:30])
