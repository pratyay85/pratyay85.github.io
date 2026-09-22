"""Check the built site for missing local links and preserved content."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

root = Path("_site")
routes = ["/", "/research/", "/teaching-2/", "/mentoring/", "/others/", "/others/the-coffee-house-experience/"]
errors = []
links = 0
for route in routes + ["/404.html", "/sitemap/"]:
    path = root / (route.lstrip("/") + ("index.html" if route.endswith("/") else ""))
    soup = BeautifulSoup(path.read_text(), "html.parser")
    main = soup.select_one(".page__content")
    assert main, route
    portrait = soup.select_one(".author__avatar img")
    assert portrait and portrait["src"].endswith("/images/pm-standard-photo.png"), route
    assert len(soup.find_all("h1")) == 1, route + ": expected one h1"
    assert soup.find("meta", attrs={"name": "viewport"}), route
    assert not soup.find("script", src=lambda value: value and "wordpress" in value), route
    for element in soup.select("[href], [src]"):
        for key in ("href", "src"):
            value = element.get(key, "")
            parsed = urlsplit(value)
            if not value or value.startswith("#") or (parsed.netloc and parsed.hostname not in {"pratyay85.github.io", "pratyay.net"}) or (parsed.scheme and parsed.scheme not in ("http", "https")):
                continue
            local = root / unquote(parsed.path.lstrip("/"))
            if local.is_dir():
                local /= "index.html"
            links += 1
            if not local.exists():
                errors.append(route + " -> " + value)
    if route == "/":
        text = main.get_text(" ", strip=True)
        for phrase in ["Principal Researcher", "Selected Invited Talks", "Program Committees", "প্রত্যয়"]:
            assert phrase in text, phrase
    if route == "/research/":
        ordered = main.find_all("ol")
        count = sum(len(ol.find_all("li", recursive=False)) for ol in ordered)
        source = BeautifulSoup(Path("research/index.html").read_text(), "html.parser")
        expected_list = source.find(id="peer-reviewed").find_next_sibling("ol")
        expected_titles = [
            li.find(["strong", "b"]).get_text(" ", strip=True)
            for li in expected_list.find_all("li", recursive=False)
        ]
        actual_titles = [
            li.find(["strong", "b"]).get_text(" ", strip=True)
            for ol in ordered for li in ol.find_all("li", recursive=False)
        ]
        assert len(expected_titles) >= 43, "Original publication list appears truncated"
        assert count == len(expected_titles), f"Expected {len(expected_titles)} peer-reviewed publications, got {count}"
        assert actual_titles == expected_titles, "Built publication titles/order differ from source"
        assert "InstaRand" in main.get_text()
        assert "Two Round Multi-party Computation" in main.get_text()
assert not errors, "\n".join(errors)
media = list((root / "wp-content/uploads").rglob("*"))
print(f"PASS: {len(routes)} content pages; {links} local links checked; {sum(p.is_file() for p in media)} local media files.")
