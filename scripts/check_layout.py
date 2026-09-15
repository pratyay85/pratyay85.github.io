"""Validate the Academic Pages layout, real portrait, navigation and theme switch."""
import base64
import functools
import http.server
import json
import os
import threading
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory="_site")
server = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
def serve_preview(route):
    """Serve the production URL from this build so absolute theme links stay local."""
    parsed = urlsplit(route.request.url)
    if parsed.hostname in {"pratyay85.github.io", "pratyay.net"}:
        response = route.fetch(url="http://127.0.0.1:8765" + parsed.path + ("?" + parsed.query if parsed.query else ""))
        route.fulfill(response=response)
    else:
        route.abort()

routes = ["/", "/research/", "/teaching-2/", "/mentoring/", "/others/", "/others/the-coffee-house-experience/"]
results = []
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for width, height in [(1440, 1000), (390, 844), (320, 740)]:
            page = browser.new_page(viewport={"width": width, "height": height}, color_scheme="light")
            page.route("**/*", serve_preview)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            for path in routes:
                response = page.goto("https://pratyay85.github.io" + path)
                assert response.status == 200, path
                page.locator(".page__content").wait_for(state="visible")
                page.wait_for_function("getComputedStyle(document.querySelector('#main')).opacity === '1'")
                assert 0 <= page.locator(".page__title").bounding_box()["y"] < height, "Heading must appear in the first screen"
                page.wait_for_function("Array.from(document.querySelectorAll('.author__avatar img')).every(i => i.complete && i.naturalWidth > 0)")
                assert not page.evaluate("document.documentElement.scrollWidth > window.innerWidth"), f"Horizontal overflow at {width}px: {path}"
                broken = page.locator("img").evaluate_all("(imgs) => imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)")
                assert not broken, broken
                assert page.locator(".masthead").is_visible()
                portrait = page.locator(".author__avatar img")
                assert portrait.get_attribute("src").endswith("/images/pm-standard-photo.png")
                if width >= 1024:
                    assert page.locator(".sidebar").bounding_box()["x"] < page.locator(".page").bounding_box()["x"], "Profile must be left of content"
                    assert portrait.bounding_box()["width"] <= 180, "Use the compact Academic Pages portrait"
            page.goto("https://pratyay85.github.io/")
            nav_link = page.locator("#site-nav").get_by_role("link", name="Publications", exact=True)
            if not nav_link.is_visible():
                page.locator("#site-nav > button").click()
            nav_link.click()
            assert page.url.endswith("/research/")
            page.goto("https://pratyay85.github.io/")
            page.locator("#theme-toggle").click()
            page.wait_for_function("document.documentElement.dataset.theme === 'dark'")
            page.locator("#theme-toggle").click()
            page.wait_for_function("document.documentElement.dataset.theme !== 'dark'")
            if width < 925:
                page.locator(".author__urls-wrapper button").click()
                assert page.locator(".author__urls a[href='mailto:pratyay85@gmail.com']").is_visible()
                page.locator(".author__urls-wrapper button").click()
            assert not errors, errors
            if os.getenv("GITHUB_REF_NAME") == "academicpages-redesign" and width in (1440, 390):
                page.wait_for_function("getComputedStyle(document.querySelector('#main')).opacity === '1'")
                page.screenshot(path=f"validation-{width}.png", animations="disabled")
                print(f"PREVIEW_{width}:" + base64.b64encode(page.screenshot(animations="disabled")).decode())
            results.append({"viewport": [width, height], "pages": len(routes), "portrait": "verified", "navigation": "pass", "theme_toggle": "pass"})
            page.close()
        browser.close()
finally:
    server.shutdown()
print(json.dumps(results))
