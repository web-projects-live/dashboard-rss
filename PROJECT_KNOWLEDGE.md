# dashboard-rss — Project Knowledge

## What This Is
A Python RSS/Atom feed aggregator that runs on GitHub Actions (cron schedule), fetches news from multiple sources, and publishes a single combined Atom feed to GitHub Pages. A Raspberry Pi family dashboard (running at `http://florin.local:8088`) fetches that feed directly and displays it in a swipeable HTML panel.

---

## Live Feed URL
```
https://web-projects-live.github.io/dashboard-rss/feed.xml
```

---

## GitHub Repo
**Repo:** `web-projects-live/dashboard-rss` (public)  
**Main branch:** `main`  
**GitHub Pages:** branch `main`, folder `/docs`

---

## Repo Structure
```
dashboard-rss/
├── .github/
│   └── workflows/
│       └── build-feed.yml    # Cron workflow — runs at 6am, 9am, 4pm EST
├── docs/
│   ├── .gitkeep
│   └── feed.xml              # Auto-generated Atom 1.0 — DO NOT edit manually
├── src/
│   ├── fetch.py              # Main entry point — fetches, merges, writes feed
│   ├── sources.py            # All source definitions + global config
│   ├── scraper.py            # BeautifulSoup scraper for non-RSS sites
│   └── test_feed.py          # 10 unit tests (run: python3 src/test_feed.py)
├── requirements.txt          # feedparser, requests, beautifulsoup4, lxml, python-dateutil
└── README.md
```

> **Important:** `index.html` (the dashboard UI) lives ONLY on the Pi at  
> `/home/pogslam/dashboard/index.html` — it is NOT in this repo (contains credentials).

---

## Feed Schedule
GitHub Actions cron (UTC):
- `0 11 * * *` → 6:00 AM EST
- `0 14 * * *` → 9:00 AM EST  
- `0 21 * * *` → 4:00 PM EST

Plus `workflow_dispatch` for manual runs from GitHub Actions UI.

---

## Sources
| Label | Type | Category | Max Items |
|-------|------|----------|-----------|
| Pokémon GO Official News | scrape | pokemon | 15 |
| The Silph Road (Pokémon GO) | rss | pokemon | 10 |
| Brawl Stars Official Blog | scrape | brawlstars | 10 |
| Brawl Stars — Reddit | rss | brawlstars | 8 (keyword filtered) |
| MIT AI News | rss | ai | 8 |
| VentureBeat AI | rss | ai | 8 |
| The Verge — AI | rss | ai | 8 (keyword filtered) |
| OpenAI Blog | rss | ai | 5 |
| The Batch — DeepLearning.AI | rss | ai | 5 |

**Global cap:** 60 most recent items total.

---

## How the Feed is Generated
1. `fetch.py` iterates `SOURCES` in `sources.py`
2. RSS sources → `feedparser`; HTML sources → `scraper.py` (BeautifulSoup + CSS selectors)
3. All items normalized to: `{title, link, summary, published, category, source_label}`
4. Deduplicated by URL, sorted newest-first, truncated to 60
5. Written as valid Atom 1.0 XML using Python stdlib `xml.etree.ElementTree` (no feedgen dependency)
6. GitHub Actions commits `docs/feed.xml` and pushes — Pages serves it instantly

---

## Dashboard (Pi) Integration
- **Device:** Raspberry Pi running Raspberry Pi OS Lite — hostname `florin`
- **Served by:** `python3 -m http.server 8088 --directory /home/pogslam/dashboard`
- **Service:** `dashboard.service` (systemd, enabled, auto-starts on boot)
- **File to edit:** `/home/pogslam/dashboard/index.html`
- **Reload after edit:** just refresh the browser — no service restart needed

### Dashboard Layout (3 swipe panels)
| Panel | Content |
|-------|---------|
| Dashboard (default) | Clock, weather, presence chips, calendar agenda, verse + joke feeds |
| Controls | Light/lock/garage buttons, family to-do list, add calendar event |
| News | Category tabs (All/Pokémon/Brawl/AI), rotating hero card (1hr), scrollable list |

### News Panel Behavior
- Fetches Atom XML directly from GitHub Pages URL (no Home Assistant dependency)
- Hero card auto-advances every 1 hour; manual Prev/Next buttons available
- Feed data auto-refreshes every 30 minutes in background
- Category tabs filter both hero and list simultaneously
- Status bar shows last update time and article count

---

## Key Files to Know
- **Add/edit sources:** `src/sources.py` — add a dict to `SOURCES`, push to main
- **Scraper selectors:** `src/scraper.py` — CSS selectors may need updating if sites redesign
- **Feed config:** constants at bottom of `src/sources.py` (MAX_TOTAL_ITEMS, timeouts, feed metadata)
- **Workflow:** `.github/workflows/build-feed.yml` — schedule, Node.js 24 env var set

---

## Things That Could Break
| Issue | Fix |
|-------|-----|
| Pokémon GO 403 errors | Site blocks scrapers — check selector or switch to `pokemon.com/us/pokemon-news` |
| Supercell blog selector fails | Site redesign — inspect in DevTools, update `item_selector` in sources.py |
| Reddit returns empty | Rate limit — 30min cron is safe, don't go faster than 5min |
| Feed shows 0 items | Check Actions run logs at `github.com/web-projects-live/dashboard-rss/actions` |
| News panel shows "Feed unavailable" | GitHub Pages may be rebuilding — refreshes automatically in 30min |

---

## Secrets / Credentials
- **HA token** and **Pi IP address** are in `index.html` on the Pi only — never committed to repo
- If HA token is ever exposed, regenerate at: HA → Profile → Security → Long-Lived Access Tokens
- Repo is public (required for free GitHub Pages) — never commit credentials here

---

## Useful Commands (SSH to Pi)
```bash
# Edit dashboard
nano /home/pogslam/dashboard/index.html

# Check dashboard service
sudo systemctl status dashboard

# Restart dashboard service (rarely needed)
sudo systemctl restart dashboard

# Watch live server logs
sudo journalctl -u dashboard -f
```

## Useful Links
- Actions runs: `https://github.com/web-projects-live/dashboard-rss/actions`
- Live feed: `https://web-projects-live.github.io/dashboard-rss/feed.xml`
- Pages settings: `https://github.com/web-projects-live/dashboard-rss/settings/pages`
