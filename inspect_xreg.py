import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

req = urllib.request.Request('https://client.xreg.site', headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        html = res.read().decode('utf-8', errors='ignore')
        print(f"Status: {res.status}")
        print(f"HTML Length: {len(html)}")

        # Extract text content
        text_matches = re.findall(r'>([^<]{4,})<', html)
        meaningful_texts = [t.strip() for t in text_matches if t.strip() and not t.strip().startswith('{')]
        print("\n--- SAMPLE PAGE TEXTS ---")
        for t in meaningful_texts[:30]:
            print(t)

        # Extract scripts
        scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
        print(f"\nFound {len(scripts)} scripts:")
        for s in scripts:
            print(s)

        # Look for build manifest or routes
        manifest_match = re.findall(r'/_next/static/[^/]+/(_buildManifest\.js|_ssgManifest\.js)', html)
        print("Manifests:", manifest_match)

except Exception as e:
    print(f"Error: {e}")
