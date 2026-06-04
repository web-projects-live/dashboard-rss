#!/usr/bin/env python3
"""
Main aggregator entry point.
Fetches RSS feeds and scrapes HTML sources, merges them into a single
Atom 1.0 feed, and writes it to docs/feed.xml.
"""

import sys
import calendar
import feedparser
from datetime import datetime, timezone
from dateutil import parser as dtparser
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

from sources import (
    SOURCES, MAX_TOTAL_ITEMS, REQUEST_TIMEOUT, USER_AGENT,
    OUTPUT_PATH, FEED_ID, FEED_TITLE, FEED_LINK,
)
from scraper import scrape_source


ATOM_NS = "http://www.w3.org/2005/Atom"


def _parse_date(entry):
    """Extract a timezone-aware UTC datetime from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return dtparser.parse(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def _keyword_match(text, keywords):
    lower = text.lower()
    return any(kw.lower() in lower for kw in keywords)


def _strip_html(text):
    try:
        from bs4 import BeautifulSoup
        return BeautifulSoup(text, "lxml").get_text(separator=" ", strip=True)
    except Exception:
        return text


def fetch_rss(source):
    """Fetch and normalize items from an RSS/Atom feed."""
    d = feedparser.parse(
        source["url"],
        agent=USER_AGENT,
        request_headers={"Accept": "application/rss+xml, application/atom+xml, */*"},
    )

    if d.get("bozo") and not d.get("entries"):
        raise RuntimeError(
            f"feedparser bozo error: {d.get('bozo_exception')}"
        )

    items = []
    icon = source.get("icon", "")
    kf = source.get("keyword_filter")

    for entry in d.entries:
        title = getattr(entry, "title", "") or ""
        summary = (
            getattr(entry, "summary", "")
            or getattr(entry, "description", "")
            or ""
        )
        link = getattr(entry, "link", "") or ""

        if not link:
            continue

        summary = _strip_html(summary)[:500]

        if kf and not _keyword_match(title + " " + summary, kf):
            continue

        full_title = f"{icon} {title}".strip() if icon else title

        items.append({
            "title": full_title,
            "link": link,
            "summary": summary,
            "published": _parse_date(entry),
            "category": source["category"],
            "source_label": source["label"],
        })

        if len(items) >= source["max_items"]:
            break

    return items


def _fmt_dt(dt):
    """Format datetime as RFC 3339 / Atom timestamp."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_feed(all_items):
    """Build an Atom 1.0 feed as a pretty-printed XML bytes string."""
    feed = Element("feed")
    feed.set("xmlns", ATOM_NS)
    feed.set("xml:lang", "en")

    def _sub(parent, tag, text=None, **attrs):
        el = SubElement(parent, tag)
        if text is not None:
            el.text = text
        for k, v in attrs.items():
            el.set(k, v)
        return el

    _sub(feed, "id", FEED_ID)
    _sub(feed, "title", FEED_TITLE)
    _sub(feed, "updated", _fmt_dt(datetime.now(timezone.utc)))
    _sub(feed, "link", rel="alternate", href=FEED_LINK)
    _sub(feed, "link", rel="self", href=FEED_ID)
    author = SubElement(feed, "author")
    _sub(author, "name", "ha-news-feed-bot")
    _sub(feed, "subtitle", "Aggregated news: Pokémon GO, Brawl Stars & AI")

    for item in all_items:
        entry = SubElement(feed, "entry")
        _sub(entry, "id", item["link"])
        _sub(entry, "title", item["title"])
        _sub(entry, "link", rel="alternate", href=item["link"])
        _sub(entry, "published", _fmt_dt(item["published"]))
        _sub(entry, "updated", _fmt_dt(item["published"]))

        if item["summary"]:
            summary_el = SubElement(entry, "summary")
            summary_el.set("type", "text")
            summary_el.text = item["summary"][:300]

        cat = SubElement(entry, "category")
        cat.set("term", item["category"])

        entry_author = SubElement(entry, "author")
        _sub(entry_author, "name", item["source_label"])

    raw = tostring(feed, encoding="unicode", xml_declaration=False)
    dom = xml.dom.minidom.parseString(
        '<?xml version="1.0" encoding="utf-8"?>' + raw
    )
    return dom.toprettyxml(indent="  ", encoding="utf-8")


def main():
    all_items = []
    errors = []

    print("Fetching sources...")
    for source in SOURCES:
        label = source["label"]
        try:
            if source["type"] == "rss":
                items = fetch_rss(source)
            elif source["type"] == "scrape":
                items = scrape_source(source)
            else:
                print(f"  [SKIP] Unknown type for {label}", file=sys.stderr)
                continue

            print(f"  [OK]   {label}: {len(items)} items")
            all_items.extend(items)

        except Exception as e:
            msg = f"{label}: {e}"
            errors.append(msg)
            print(f"  [ERR]  {msg}", file=sys.stderr)

    # Deduplicate by link URL (keep first occurrence)
    seen = set()
    deduped = []
    for item in all_items:
        if item["link"] not in seen:
            seen.add(item["link"])
            deduped.append(item)

    # Sort newest-first and truncate
    deduped.sort(key=lambda x: x["published"], reverse=True)
    deduped = deduped[:MAX_TOTAL_ITEMS]

    feed_bytes = build_feed(deduped)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(feed_bytes)

    print(f"\nWrote {len(deduped)} items to {OUTPUT_PATH}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if len(errors) == len(SOURCES):
        sys.exit(1)


if __name__ == "__main__":
    main()
