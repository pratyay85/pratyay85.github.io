"""Check the built site for missing local links and preserved content."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

root = Path("_site")
routes = ["/", "/research/", "/teaching-2/", "/mentoring/", "/others/", "/others/the-coffee-house-experience/"]
errors = []
links = 0
for route in routes + ["/404.html"]:
    path = root / (route.lstrip("/") + ("index.html" if route.endswith("/") else ""))
    soup = BeautifulSoup(path.read_text(), "html.parser")
    assert soup.find("main"), route
    assert len(soup.find_all("h1")) == 1, route + ": expected one h1"
    assert soup.find("meta", attrs={"name": "viewport"}), route
    assert not soup.find("script", src=lambda value: value and "wordpress" in value), route
    for element in soup.select("[href], [src]"):
        for key in ("href", "src"):
            value = element.get(key, "")
            parsed = urlsplit(value)
            if not value or parsed.scheme or parsed.netloc or value.startswith("#"):
                continue
            local = root / unquote(parsed.path.lstrip("/"))
            if local.is_dir():
                local /= "index.html"
            links += 1
            if not local.exists():
                errors.append(route + " -> " + value)
    if route == "/":
        text = soup.main.get_text(" ", strip=True)
        for phrase in ["Principal Researcher", "Selected Invited Talks", "Program Committees", "প্রত্যয়"]:
            assert phrase in text, phrase
    if route == "/research/":
        ordered = soup.main.find_all("ol")
        count = sum(len(ol.find_all("li", recursive=False)) for ol in ordered)
        assert count == 43, f"Expected 43 peer-reviewed publications, got {count}"
        assert "InstaRand" in soup.main.get_text()
        assert "Two Round Multi-party Computation" in soup.main.get_text()
assert not errors, "\n".join(errors)
media = list((root / "wp-content/uploads").rglob("*"))
print(f"PASS: {len(routes)} content pages; {links} local links checked; {sum(p.is_file() for p in media)} local media files.")
