#!/usr/bin/env python3
"""Temporary diagnostic script to inspect the Brawl Stars blog page structure."""

import sys
import os
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))

from scraper import make_session
from sources import REQUEST_TIMEOUT

URL = "https://supercell.com/en/games/brawlstars/blog/"


def main():
    session = make_session()
    resp = session.get(URL, timeout=REQUEST_TIMEOUT)
    print(f"Status: {resp.status_code}")
    print(f"Length: {len(resp.text)}")

    soup = BeautifulSoup(resp.text, "lxml")

    next_data = soup.find("script", {"id": "__NEXT_DATA__"})
    print(f"__NEXT_DATA__ present: {next_data is not None}")
    if next_data:
        content = next_data.string or ""
        print(f"__NEXT_DATA__ length: {len(content)}")
        print(f"__NEXT_DATA__ snippet: {content[:1000]}")

    # All scripts
    scripts = soup.find_all("script")
    print(f"Total <script> tags: {len(scripts)}")

    # All links containing /blog/
    links = soup.find_all("a", href=True)
    print(f"Total <a> tags: {len(links)}")
    blog_links = [a for a in links if "/blog/" in a["href"]]
    print(f"<a> tags with '/blog/' in href: {len(blog_links)}")
    for a in blog_links[:20]:
        print(f"  href={a['href']!r} class={a.get('class')!r} text={a.get_text(strip=True)[:80]!r}")

    # Print body snippet
    body = soup.find("body")
    if body:
        print("Body snippet (first 2000 chars):")
        print(str(body)[:2000])


if __name__ == "__main__":
    main()
