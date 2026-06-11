import re
import requests
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from sources import USER_AGENT, REQUEST_TIMEOUT


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return s


def _extract_article_date(session, url):
    """Fetch article page and extract published date from meta tags."""
    try:
        r = session.get(url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        for prop in ("article:published_time", "og:published_time", "datePublished"):
            tag = soup.find("meta", property=prop) or soup.find("meta", itemprop=prop)
            if tag and tag.get("content"):
                from dateutil import parser as dtparser
                return dtparser.parse(tag["content"]).astimezone(timezone.utc)
        # Try <time datetime="...">
        time_tag = soup.find("time", {"datetime": True})
        if time_tag:
            from dateutil import parser as dtparser
            return dtparser.parse(time_tag["datetime"]).astimezone(timezone.utc)
    except Exception:
        pass
    return datetime.now(timezone.utc)


def _normalize_url(href, base_url):
    """Return an absolute URL given a possibly-relative href."""
    if not href:
        return None
    href = href.strip()
    if href.startswith("//"):
        scheme = urlparse(base_url).scheme or "https"
        return f"{scheme}:{href}"
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return urljoin(base_url, href)


def scrape_source(source):
    """
    Scrape an HTML page and return a list of normalized item dicts.
    """
    cfg = source["scrape_config"]
    base_url = cfg.get("base_url", source["url"])
    max_items = source.get("max_items", 10)

    session = make_session()

    try:
        resp = session.get(source["url"], timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch {source['url']}: {e}") from e

    soup = BeautifulSoup(resp.text, "lxml")
    candidates = soup.select(cfg["item_selector"])

    seen_links = set()
    items = []

    for el in candidates:
        # Ensure we're working with an <a> tag
        a_tag = el if el.name == "a" else el.find("a")
        if not a_tag:
            continue

        href = _normalize_url(a_tag.get("href"), base_url)
        if not href or href in seen_links:
            continue

        # Skip fragment-only or javascript: links
        parsed = urlparse(href)
        if not parsed.scheme or not parsed.netloc:
            continue

        seen_links.add(href)

        # Extract title
        title_text = ""
        title_selector = cfg.get("title_child")
        if title_selector:
            title_el = a_tag.select_one(title_selector)
            if title_el:
                title_text = title_el.get_text(strip=True)

        if not title_text:
            title_text = a_tag.get_text(strip=True)

        # Remove duplicate whitespace/newlines common in scraped text
        title_text = re.sub(r"\s+", " ", title_text).strip()

        if len(title_text) < 5:
            continue

        icon = source.get("icon", "")
        full_title = f"{icon} {title_text}" if icon else title_text

        if cfg.get("fetch_article_date"):
            published = _extract_article_date(session, href)
        else:
            published = datetime.now(timezone.utc)

        items.append({
            "title": full_title,
            "link": href,
            "summary": "",
            "published": published,
            "category": source["category"],
            "source_label": source["label"],
        })

        if len(items) >= max_items:
            break

    return items
