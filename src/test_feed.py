#!/usr/bin/env python3
"""
Basic unit tests for feed generation and normalization logic.
Run with: python3 src/test_feed.py
"""

import sys
import os
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from fetch import build_feed, _keyword_match, _fmt_dt
import xml.etree.ElementTree as ET


class TestKeywordMatch(unittest.TestCase):
    def test_case_insensitive(self):
        self.assertTrue(_keyword_match("Big AI Announcement", ["ai"]))

    def test_no_match(self):
        self.assertFalse(_keyword_match("Pokemon news", ["official", "update"]))

    def test_partial_match(self):
        self.assertTrue(_keyword_match("This is about ChatGPT models", ["ChatGPT"]))


class TestFmtDt(unittest.TestCase):
    def test_format(self):
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(_fmt_dt(dt), "2025-01-15T12:00:00Z")


class TestBuildFeed(unittest.TestCase):
    def _make_item(self, title="Test Title", link="https://example.com/1", summary="Summary text",
                   category="ai", source_label="Test Source"):
        return {
            "title": title,
            "link": link,
            "summary": summary,
            "published": datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            "category": category,
            "source_label": source_label,
        }

    def test_empty_feed_is_valid_xml(self):
        xml_bytes = build_feed([])
        root = ET.fromstring(xml_bytes)
        self.assertIn("feed", root.tag)

    def test_single_entry(self):
        items = [self._make_item()]
        xml_bytes = build_feed(items)
        root = ET.fromstring(xml_bytes)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entries = root.findall("a:entry", ns)
        self.assertEqual(len(entries), 1)
        title = entries[0].find("a:title", ns).text
        self.assertEqual(title, "Test Title")

    def test_entry_ids_are_links(self):
        items = [self._make_item(link="https://example.com/article")]
        xml_bytes = build_feed(items)
        root = ET.fromstring(xml_bytes)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entry = root.find("a:entry", ns)
        entry_id = entry.find("a:id", ns).text
        self.assertEqual(entry_id, "https://example.com/article")

    def test_summary_truncated(self):
        long_summary = "x" * 400
        items = [self._make_item(summary=long_summary)]
        xml_bytes = build_feed(items)
        root = ET.fromstring(xml_bytes)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entry = root.find("a:entry", ns)
        summary_el = entry.find("a:summary", ns)
        self.assertIsNotNone(summary_el)
        self.assertLessEqual(len(summary_el.text), 300)

    def test_multiple_entries_order_preserved(self):
        items = [
            self._make_item(title="First", link="https://example.com/1"),
            self._make_item(title="Second", link="https://example.com/2"),
        ]
        xml_bytes = build_feed(items)
        root = ET.fromstring(xml_bytes)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entries = root.findall("a:entry", ns)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].find("a:title", ns).text, "First")
        self.assertEqual(entries[1].find("a:title", ns).text, "Second")

    def test_feed_metadata(self):
        xml_bytes = build_feed([])
        root = ET.fromstring(xml_bytes)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        self.assertIn("dashboard-rss", root.find("a:id", ns).text)
        self.assertIsNotNone(root.find("a:title", ns).text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
