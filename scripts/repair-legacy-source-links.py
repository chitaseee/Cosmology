#!/usr/bin/env python3
"""Repair broken NASA source links in legacy Kayhan guide pages before deployment."""
from pathlib import Path
import re

fixed_files = 0
fixed_links = 0
unresolved = []

for path in sorted(Path(".").glob("**/index.html")):
    if ".git" in path.parts:
        continue
    html = path.read_text(encoding="utf-8")
    if 'href="undefined"' not in html:
        continue

    match = re.search(r'https://science\.nasa\.gov/[^\s"<>]+', html)
    if not match:
        unresolved.append(str(path))
        continue

    source_url = match.group(0).rstrip(".,;)")
    count = html.count('href="undefined"')
    html = html.replace('href="undefined"', f'href="{source_url}"')

    # Turn bare NASA URLs in paragraphs into actual, accessible source links.
    html = re.sub(
        r'<p>(https://science\.nasa\.gov/[^\s<]+)</p>',
        lambda m: (
            '<p><a href="' + m.group(1).rstrip('.,;)') +
            '" target="_blank" rel="noopener noreferrer">NASA Science — '
            + m.group(1).rstrip('/').split('/')[-1].replace('-', ' ').title()
            + '</a></p>'
        ),
        html,
    )
    path.write_text(html, encoding="utf-8")
    fixed_files += 1
    fixed_links += count

if unresolved:
    raise SystemExit("Could not determine a NASA source URL for: " + ", ".join(unresolved))

remaining = []
for path in Path(".").glob("**/index.html"):
    if ".git" not in path.parts and 'href="undefined"' in path.read_text(encoding="utf-8"):
        remaining.append(str(path))
if remaining:
    raise SystemExit("Broken undefined links remain: " + ", ".join(remaining))

print(f"SEO build repair: fixed {fixed_links} broken NASA links across {fixed_files} pages.")
