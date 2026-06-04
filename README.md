# dashboard-rss

Custom RSS/Atom feed aggregator for Home Assistant. Fetches news from Pokémon GO, Brawl Stars, and AI sources every 30 minutes via GitHub Actions and publishes a combined Atom feed to GitHub Pages.

## Feed URL

```
https://web-projects-live.github.io/dashboard-rss/feed.xml
```

## Sources

| Source | Type | Category |
|--------|------|----------|
| Pokémon GO Official News | Scrape | pokemon |
| The Silph Road | RSS | pokemon |
| Brawl Stars Official Blog | Scrape | brawlstars |
| Brawl Stars — Reddit | RSS | brawlstars |
| MIT AI News | RSS | ai |
| VentureBeat AI | RSS | ai |
| The Verge — AI | RSS | ai |
| OpenAI Blog | RSS | ai |
| The Batch — DeepLearning.AI | RSS | ai |

## Home Assistant Setup

### `configuration.yaml`

```yaml
feedreader:
  urls:
    - https://web-projects-live.github.io/dashboard-rss/feed.xml
  scan_interval:
    minutes: 30
  max_entries: 60
```

### Dashboard card (no HACS)

```yaml
type: markdown
title: 📰 Latest News
content: |
  {% for state in states.feedreader | sort(attribute='last_changed', reverse=True) | list %}
  **{{ state.attributes.title }}**
  {{ state.attributes.feed_name }} · {{ relative_time(state.last_changed) }} ago
  [Read →]({{ state.attributes.link }})

  ---
  {% endfor %}
```

### RSS News Card (HACS)

```yaml
type: custom:rss-news-card
urls:
  - https://web-projects-live.github.io/dashboard-rss/feed.xml
number_of_items: 20
title: 📰 News Feed
```

## GitHub Pages Setup

1. Go to **Settings → Pages → Source**: Deploy from branch `main`, folder `/docs`.
2. After the first workflow run, the feed is live at the URL above.

## Adding Sources

Edit `src/sources.py` and add a new dict to `SOURCES`. Supports:
- `"type": "rss"` — native RSS/Atom feeds via feedparser
- `"type": "scrape"` — HTML scraping via BeautifulSoup + CSS selectors

Useful free RSS patterns:
- Reddit: `https://www.reddit.com/r/{subreddit}/.rss`
- YouTube channel: `https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}`
- GitHub releases: `https://github.com/{owner}/{repo}/releases.atom`
