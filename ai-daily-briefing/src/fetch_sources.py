"""Fetch recent items from curated feeds across three tracks:
1. AI news
2. Coding best practices
3. Software factories (AI-driven software production / agentic dev)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import feedparser

# Each track maps to a list of (source_name, feed_url)
FEEDS: dict[str, list[tuple[str, str]]] = {
    "AI News": [
        ("Anthropic News", "https://www.anthropic.com/rss.xml"),
        ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
        ("Hacker News: AI", "https://hnrss.org/newest?q=AI&points=100"),
        ("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
        ("arXiv cs.AI", "https://rss.arxiv.org/rss/cs.AI"),
    ],
    "Coding Best Practices": [
        ("Martin Fowler", "https://martinfowler.com/feed.atom"),
        ("Pragmatic Engineer", "https://blog.pragmaticengineer.com/rss/"),
        ("Hacker News: engineering", "https://hnrss.org/newest?q=engineering+practices&points=50"),
        ("Dev.to top", "https://dev.to/feed"),
        ("arXiv cs.SE", "https://rss.arxiv.org/rss/cs.SE"),
    ],
    "Software Factories": [
        ("HN: AI coding agents", "https://hnrss.org/newest?q=coding+agent&points=50"),
        ("HN: software factory", "https://hnrss.org/newest?q=%22software+factory%22"),
        ("GitHub Blog", "https://github.blog/feed/"),
        ("Anthropic Engineering", "https://www.anthropic.com/rss.xml"),
    ],
}

LOOKBACK_HOURS = 30  # slightly more than a day so nothing falls in the cracks
MAX_ITEMS_PER_TRACK = 15


@dataclass
class Item:
    track: str
    source: str
    title: str
    link: str
    published: datetime | None
    summary: str = field(default="")


def _parse_time(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
    return None


def fetch_all() -> list[Item]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    items: list[Item] = []
    for track, feeds in FEEDS.items():
        track_items: list[Item] = []
        for source, url in feeds:
            try:
                parsed = feedparser.parse(url)
            except Exception:
                continue
            for entry in parsed.entries[:20]:
                published = _parse_time(entry)
                # Keep undated items (some feeds omit dates) but drop stale ones
                if published and published < cutoff:
                    continue
                summary = (entry.get("summary") or "")[:400]
                track_items.append(
                    Item(
                        track=track,
                        source=source,
                        title=entry.get("title", "(untitled)").strip(),
                        link=entry.get("link", ""),
                        published=published,
                        summary=summary,
                    )
                )
        # Newest first, cap per track
        track_items.sort(key=lambda i: i.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        items.extend(track_items[:MAX_ITEMS_PER_TRACK])
    return items
