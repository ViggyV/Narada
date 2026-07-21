"""Fetch recent items from curated feeds across three tracks:
1. AI news
2. Coding best practices
3. Software factories (AI-driven software production / agentic dev)
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import feedparser

log = logging.getLogger(__name__)

# Each track maps to a list of (source_name, feed_url)
FEEDS: dict[str, list[tuple[str, str]]] = {
    "AI News": [
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
    """Fetch every configured feed.

    A dead feed is survivable — the briefing still ships from whatever else
    responded — but it must not be *silent*, or the digest quietly narrows
    and nobody notices which source stopped reporting.
    """
    started = time.monotonic()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    items: list[Item] = []
    ok = failed = 0

    for track, feeds in FEEDS.items():
        track_items: list[Item] = []
        for source, url in feeds:
            try:
                parsed = feedparser.parse(url)
            except Exception as exc:  # network, parser, or malformed payload
                log.warning("feed errored: %s — %s: %s", source, type(exc).__name__, exc)
                failed += 1
                continue

            # feedparser reports most failures via `bozo` rather than raising.
            if getattr(parsed, "bozo", False) and not parsed.entries:
                log.warning("feed unreadable: %s — %s", source, parsed.get("bozo_exception"))
                failed += 1
                continue
            if not parsed.entries:
                log.warning("feed empty: %s", source)
                failed += 1
                continue

            kept = stale = 0
            for entry in parsed.entries[:20]:
                published = _parse_time(entry)
                # Keep undated items (some feeds omit dates) but drop stale ones
                if published and published < cutoff:
                    stale += 1
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
                kept += 1
            ok += 1
            log.info("%s: %d kept, %d older than %dh", source, kept, stale, LOOKBACK_HOURS)

        # Newest first, cap per track
        track_items.sort(key=lambda i: i.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        if len(track_items) > MAX_ITEMS_PER_TRACK:
            log.info(
                "%s: capped %d -> %d items", track, len(track_items), MAX_ITEMS_PER_TRACK
            )
        items.extend(track_items[:MAX_ITEMS_PER_TRACK])

    total = ok + failed
    level = logging.WARNING if failed else logging.INFO
    log.log(
        level,
        "fetched %d items from %d/%d feeds in %.1fs (%d failed)",
        len(items), ok, total, time.monotonic() - started, failed,
    )
    return items
