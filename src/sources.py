SOURCES = [

    # ── POKÉMON GO ─────────────────────────────────────────────────────────

    {
        "label": "Pokémon GO Official News",
        "type": "scrape",
        "url": "https://pokemongolive.com/news/",
        "category": "pokemon",
        "icon": "⚡",
        "max_items": 15,
        "keyword_filter": None,
        "scrape_config": {
            "item_selector": "a[href*='/post/'], a[href*='/news/']",
            "title_child": "h2, h3, p, span",
            "base_url": "https://pokemongolive.com",
            "fetch_article_date": False,
        },
    },

    {
        "label": "The Silph Road (Pokémon GO)",
        "type": "rss",
        "url": "https://www.reddit.com/r/TheSilphRoad/.rss?limit=25",
        "category": "pokemon",
        "icon": "⚡",
        "max_items": 10,
        "keyword_filter": None,
    },

    # ── BRAWL STARS ─────────────────────────────────────────────────────────

    {
        "label": "Brawl Stars Official Blog",
        "type": "scrape",
        "url": "https://supercell.com/en/games/brawlstars/blog/",
        "category": "brawlstars",
        "icon": "🏆",
        "max_items": 10,
        "keyword_filter": None,
        "scrape_config": {
            "item_selector": "article a, .post-card a, .blog-card a, .news-item a",
            "title_child": "h2, h3, .title, .post-title",
            "base_url": "https://supercell.com",
            "fetch_article_date": False,
        },
    },

    {
        "label": "Brawl Stars — Reddit",
        "type": "rss",
        "url": "https://www.reddit.com/r/Brawlstars/.rss?limit=25",
        "category": "brawlstars",
        "icon": "🏆",
        "max_items": 8,
        "keyword_filter": ["official", "update", "patch", "balance", "season", "brawl pass", "release notes"],
    },

    # ── AI NEWS ─────────────────────────────────────────────────────────────

    {
        "label": "MIT AI News",
        "type": "rss",
        "url": "https://news.mit.edu/rss/topic/artificial-intelligence2",
        "category": "ai",
        "icon": "🤖",
        "max_items": 8,
        "keyword_filter": None,
    },

    {
        "label": "VentureBeat AI",
        "type": "rss",
        "url": "https://venturebeat.com/category/ai/feed/",
        "category": "ai",
        "icon": "🤖",
        "max_items": 8,
        "keyword_filter": None,
    },

    {
        "label": "The Verge — AI",
        "type": "rss",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "ai",
        "icon": "🤖",
        "max_items": 8,
        "keyword_filter": [
            "AI", "artificial intelligence", "LLM", "GPT", "Gemini", "Claude",
            "ChatGPT", "OpenAI", "Anthropic", "machine learning", "neural",
            "large language model", "generative",
        ],
    },

    {
        "label": "OpenAI Blog",
        "type": "rss",
        "url": "https://openai.com/news/rss.xml",
        "category": "ai",
        "icon": "🤖",
        "max_items": 5,
        "keyword_filter": None,
    },

    {
        "label": "The Batch — DeepLearning.AI",
        "type": "rss",
        "url": "https://www.deeplearning.ai/the-batch/feed/",
        "category": "ai",
        "icon": "🤖",
        "max_items": 5,
        "keyword_filter": None,
    },
]

# ── GLOBAL CONFIG ──────────────────────────────────────────────────────────
MAX_TOTAL_ITEMS = 60
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
OUTPUT_PATH = "docs/feed.xml"
FEED_ID = "https://web-projects-live.github.io/dashboard-rss/feed.xml"
FEED_TITLE = "HA News Feed — Pokémon GO, Brawl Stars & AI"
FEED_LINK = "https://web-projects-live.github.io/dashboard-rss/"
