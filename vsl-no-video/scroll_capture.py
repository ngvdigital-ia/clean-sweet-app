from playwright.sync_api import sync_playwright
import time

url = "https://recetas.panaderiacero.com/rqpjsh4mqz"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1500)

    # Scroll through the entire page in small steps to trigger any
    # IntersectionObserver-based lazy content (Elementor lazy containers, etc.)
    height = page.evaluate("document.body.scrollHeight")
    step = 300
    y = 0
    while y < height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(250)
        y += step
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height > height:
            height = new_height

    # scroll back to top, then bottom, then back to top again for safety
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    has_chef = page.evaluate("document.body.innerText.includes('Chef Natasha')")
    print("Chef Natasha present after scroll:", has_chef)

    html = page.content()
    with open("original_scrolled.html", "w", encoding="utf-8") as f:
        f.write(html)

    browser.close()
