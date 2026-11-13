#!/usr/bin/env python3
"""Read-only SEO quality audit for Kayhan's static pages.

This script reports issues without changing site files or failing deployment.
It checks discoverability metadata, canonical URLs, language tags, headings,
JSON-LD syntax, duplicate titles/canonicals, and sitemap coverage.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import json
import re

ROOT = Path(".")
BASE = "https://chitaseee.github.io/Cosmology/"
SITEMAP = ROOT / "sitemap.xml"


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.lang = ""
        self.h1_count = 0
        self.jsonld_count = 0
        self.jsonld_errors = 0
        self.in_jsonld = False
        self.jsonld_parts = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            if a.get("name", "").lower() == "description":
                self.description = a.get("content", "").strip()
            elif a.get("name", "").lower() == "robots":
                self.robots = a.get("content", "").lower()
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = a.get("href", "").strip()
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.jsonld_parts = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_jsonld:
            self.in_jsonld = False
            raw = "".join(self.jsonld_parts).strip()
            if raw:
                self.jsonld_count += 1
                try:
                    json.loads(raw)
                except (ValueError, TypeError):
                    self.jsonld_errors += 1

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.in_jsonld:
            self.jsonld_parts.append(data)

    @property
    def title(self):
        return re.sub(r"\s+", " ", "".join(self.title_parts)).strip()


pages = sorted(p for p in ROOT.rglob("*.html")
               if ".git" not in p.parts and "node_modules" not in p.parts)
issues = Counter()
titles = Counter()
canonicals = Counter()
sitemap_urls = []
structured_data_blocks = 0

for path in pages:
    parser = SEOParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issues["unreadable_html"] += 1
        print(f"WARN {path}: could not parse HTML ({exc})")
        continue

    structured_data_blocks += parser.jsonld_count

    if not parser.title:
        issues["missing_title"] += 1
        print(f"WARN {path}: missing <title>")
    else:
        titles[parser.title] += 1
        if len(parser.title) > 70:
            issues["long_title"] += 1
            print(f"WARN {path}: title is {len(parser.title)} characters")
    is_noindex = "noindex" in parser.robots
    if not parser.description and not is_noindex:
        issues["missing_description"] += 1
        print(f"WARN {path}: missing meta description")
    elif parser.description and (len(parser.description) < 50 or len(parser.description) > 180):
        issues["description_length"] += 1
        print(f"WARN {path}: description length is {len(parser.description)}")
    if not parser.canonical and not is_noindex:
        issues["missing_canonical"] += 1
        print(f"WARN {path}: missing canonical URL")
    elif parser.canonical:
        canonicals[parser.canonical] += 1
        if not parser.canonical.startswith(BASE):
            issues["canonical_outside_site"] += 1
            print(f"WARN {path}: canonical is outside the configured site: {parser.canonical}")
    if not parser.lang:
        issues["missing_language"] += 1
        print(f"WARN {path}: missing html lang attribute")
    if parser.h1_count == 0:
        issues["missing_h1"] += 1
        print(f"WARN {path}: no H1 heading")
    if is_noindex:
        issues["noindex_pages"] += 1
        print(f"INFO {path}: robots meta contains noindex")
    if parser.jsonld_errors:
        issues["invalid_jsonld"] += parser.jsonld_errors
        print(f"WARN {path}: invalid JSON-LD block(s): {parser.jsonld_errors}")

for title, count in titles.items():
    if count > 1:
        issues["duplicate_titles"] += count - 1
        print(f"WARN duplicate title ({count} pages): {title}")
for canonical, count in canonicals.items():
    if count > 1:
        issues["duplicate_canonicals"] += count - 1
        print(f"WARN duplicate canonical ({count} pages): {canonical}")

if SITEMAP.exists():
    try:
        tree = ET.parse(SITEMAP)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = [n.text.strip() for n in tree.findall(".//sm:loc", ns) if n.text]
        if len(sitemap_urls) != len(set(sitemap_urls)):
            issues["duplicate_sitemap_urls"] += len(sitemap_urls) - len(set(sitemap_urls))
            print("WARN sitemap.xml contains duplicate URLs")
        for url in sitemap_urls:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "chitaseee.github.io":
                issues["invalid_sitemap_host"] += 1
                print(f"WARN sitemap URL has unexpected host: {url}")
                continue
            relative = parsed.path.removeprefix("/Cosmology/").strip("/")
            target = ROOT / relative / "index.html" if relative else ROOT / "index.html"
            if not target.is_file():
                issues["missing_sitemap_page"] += 1
                print(f"WARN sitemap URL has no local page: {url}")
    except (ET.ParseError, OSError) as exc:
        issues["invalid_sitemap"] += 1
        print(f"WARN sitemap.xml could not be parsed: {exc}")
else:
    issues["missing_sitemap"] += 1
    print("WARN sitemap.xml is missing")

print("\nKayhan SEO audit summary")
print(f"HTML pages checked: {len(pages)}")
print(f"URLs in sitemap: {len(sitemap_urls)}")
print(f"Structured data blocks parsed: {structured_data_blocks}")
if issues:
    print("Findings (warnings; deployment is not blocked):")
    for name, count in sorted(issues.items()):
        print(f"  {name}: {count}")
else:
    print("No issues detected by these automated checks.")
