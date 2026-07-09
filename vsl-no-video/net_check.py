import sys
from playwright.sync_api import sync_playwright

url = "http://localhost:8899/vsl-no-video/"
requests_log = []
console_errors = []
page_errors = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844})

    page.on("request", lambda req: requests_log.append(req.url))
    page.on("console", lambda msg: console_errors.append((msg.type, msg.text)) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(8000)

    browser.close()

suspicious = [u for u in requests_log if any(k in u.lower() for k in [
    "analytics", "googletagmanager", "google-analytics", "gtag",
    "panaderiacero", "g-c9evjfdrw8".lower(), "69d1f0601a421f920d2bd295"
])]

print("ALL REQUEST URLS:")
for u in requests_log:
    print("  ", u)

print("TOTAL REQUESTS:", len(requests_log))
print("SUSPICIOUS (GA/competitor) REQUESTS:", len(suspicious))
for u in suspicious:
    print("  ->", u)

print("\nCONSOLE ERRORS:", len(console_errors))
for t, m in console_errors[:20]:
    print("  [", t, "]", m[:300])

print("\nPAGE (uncaught) ERRORS:", len(page_errors))
for e in page_errors[:20]:
    print("  ", e[:300])

print("\nALL REQUEST HOSTS (unique):")
hosts = set()
from urllib.parse import urlparse
for u in requests_log:
    try:
        hosts.add(urlparse(u).netloc)
    except Exception:
        pass
for h in sorted(hosts):
    print("  ", h)
