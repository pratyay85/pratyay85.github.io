"""Browser checks for functional navigation, images, and responsive overflow."""
import functools
import http.server
import json
import threading
from playwright.sync_api import sync_playwright

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory="_site")
server = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
routes = ["/", "/research/", "/teaching-2/", "/mentoring/", "/others/", "/others/the-coffee-house-experience/"]
results = []
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for width, height in [(1440, 1000), (390, 844), (320, 740)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            # Third-party embeds/fonts are outside the local layout check.
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("http://127.0.0.1") else route.abort())
            for path in routes:
                response = page.goto("http://127.0.0.1:8765" + path)
                assert response.status == 200, path
                assert page.locator("main").is_visible(), path
                overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                assert not overflow, f"Horizontal overflow at {width}px: {path}"
                broken = page.locator("img").evaluate_all("(imgs) => imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)")
                assert not broken, broken
                active = page.locator('nav[aria-label="Main navigation"] a[aria-current="page"]')
                assert active.count() == 1, path
                assert active.is_visible(), path
            page.goto("http://127.0.0.1:8765/")
            page.locator('nav[aria-label="Main navigation"]').get_by_role("link", name="Publications", exact=True).click()
            assert page.url.endswith("/research/")
            results.append({"viewport": [width, height], "pages": len(routes), "result": "pass"})
            page.close()
        browser.close()
finally:
    server.shutdown()
print(json.dumps(results))
