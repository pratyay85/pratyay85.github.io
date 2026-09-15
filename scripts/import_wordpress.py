"""Import public WordPress content once; subsequent builds use the committed snapshot."""
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://pratyay.net"
ROUTES = ["/", "/research/", "/teaching-2/", "/mentoring/", "/others/", "/others/the-coffee-house-experience/"]
OWN_HOSTS = {"pratyay.net", "www.pratyay.net", "pratmukh.wordpress.com", "pratmukh.files.wordpress.com"}
ASSET_SUFFIXES = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
report = {"source": SOURCE, "pages": [], "downloads": [], "warnings": []}
assets = {}

def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0 (personal website migration)"}), timeout=45) as response:
                return response.read(), response.headers.get("Content-Type", "")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))

def local_asset(url):
    parsed = urlsplit(url)
    raw_path = unquote(parsed.path)
    if "/wp-content/uploads/" in raw_path:
        path = raw_path
    else:
        path = "/wp-content/uploads" + raw_path
    parts = Path(path).parts
    if ".." in parts:
        raise ValueError("Unsafe media path")
    target = ROOT / path.lstrip("/")
    if url in assets:
        return assets[url]
    if target.exists():
        assets[url] = path
        return path
    try:
        data, kind = fetch(url)
        if "text/html" in kind:
            raise ValueError("Media URL returned HTML")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        report["downloads"].append({"source": url, "path": path, "bytes": len(data)})
        assets[url] = path
        return path
    except Exception as error:
        # Keep the public WordPress media URL working even after pratyay.net moves.
        fallback = "https://pratmukh.files.wordpress.com/" + raw_path.split("/wp-content/uploads/")[-1].lstrip("/")
        report["warnings"].append({"url": url, "error": str(error), "fallback": fallback})
        assets[url] = fallback
        return fallback

def rewrite(value, base):
    if not value or value.startswith(("#", "mailto:", "tel:", "data:")):
        return value
    absolute = urljoin(base, value)
    parsed = urlsplit(absolute)
    if parsed.hostname not in OWN_HOSTS:
        return absolute
    route = parsed.path.rstrip("/") + "/"
    if route in ROUTES:
        return route + (("#" + parsed.fragment) if parsed.fragment else "")
    if Path(parsed.path).suffix.lower() in ASSET_SUFFIXES:
        return local_asset(absolute)
    return absolute.replace("https://pratyay.net", "https://pratmukh.wordpress.com")

def main():
    pages = []
    for route in ROUTES:
        data, _ = fetch(SOURCE + route)
        soup = BeautifulSoup(data, "html.parser")
        article = soup.select_one(".entry-content") or soup.select_one(".wp-block-post-content") or soup.select_one("article")
        if article is None:
            raise RuntimeError("No article found: " + route + " " + str(soup)[:4000])
        for junk in article.select("script, style, .sharedaddy, .sd-sharing-enabled, .wpcnt, .jp-relatedposts, #jp-post-flair, .jetpack-likes-widget-wrapper"):
            junk.decompose()
        for element in article.find_all(True):
            for key in list(element.attrs):
                if key.lower().startswith("on"):
                    del element[key]
            for key in ("href", "src", "poster"):
                if element.has_attr(key):
                    value = element[key]
                    if value.strip().lower().startswith(("javascript:", "vbscript:")):
                        del element[key]
                    else:
                        element[key] = rewrite(value, SOURCE + route)
            if element.has_attr("srcset"):
                del element["srcset"]
            if element.has_attr("sizes"):
                del element["sizes"]
            if element.name == "iframe":
                element["loading"] = "lazy"
                element["title"] = element.get("title", "Embedded media")
            if element.name == "img":
                element["loading"] = "lazy"
        title = soup.select_one(".entry-title") or soup.select_one(".wp-block-post-title")
        title = title.get_text(" ", strip=True) if title else ("Home" if route == "/" else route.strip("/").title())
        styles = [link.get("href") for link in soup.select('link[rel="stylesheet"]')]
        body_class = soup.body.get("class", []) if soup.body else []
        pages.append({"route": route, "title": title, "html": article.decode_contents()})
        report["pages"].append({"route": route, "title": title, "stylesheets": styles, "body_classes": body_class, "text_length": len(article.get_text())})
    (ROOT / "content").mkdir(exist_ok=True)
    (ROOT / "content/pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "content/migration-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"pages": len(pages), "downloads": len(report["downloads"]), "warnings": report["warnings"]}, indent=2))

if __name__ == "__main__":
    main()
