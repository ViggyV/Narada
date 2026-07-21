"""Turn fetched items into a short, prioritized 'what to implement' list.

If ANTHROPIC_API_KEY is set, Claude does the synthesis.
Otherwise, falls back to a ranked digest computed with simple heuristics —
no API call, no key, so the scheduled run still produces something useful.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone

from fetch_sources import FEEDS, LOOKBACK_HOURS, Item

log = logging.getLogger(__name__)

TRACK_ORDER = tuple(FEEDS)

MODEL = "claude-sonnet-4-6"

PROMPT = """You are producing a daily engineering briefing. Below are today's items \
across three tracks: AI news, coding best practices, and software factories \
(AI-driven software production / agentic development).

Your job:
1. Summarize the 3-5 most significant developments per track in one line each, with links.
2. End with a section titled "## Shortlist: What's Worth Implementing" containing at most \
5 concrete, actionable recommendations ranked by impact-vs-effort — things a small team \
could realistically adopt this week (a tool, a practice, a workflow change). For each: \
one sentence on what to do and one on why now.

Be concise, skeptical of hype, and concrete. Output clean Markdown only.

Today's items:

{items}
"""


def _items_block(items: list[Item]) -> str:
    lines = []
    current_track = None
    for it in items:
        if it.track != current_track:
            current_track = it.track
            lines.append(f"\n### {current_track}")
        date = it.published.strftime("%Y-%m-%d %H:%M UTC") if it.published else "undated"
        lines.append(f"- [{it.source}] {it.title} ({date}) {it.link}")
        if it.summary:
            lines.append(f"  > {it.summary}")
    return "\n".join(lines)


# Hand-tuned: editorial sources carry more signal per item than firehoses.
SOURCE_WEIGHT: dict[str, float] = {
    "Anthropic News": 3.0,
    "Anthropic Engineering": 3.0,
    "Martin Fowler": 3.0,
    "Pragmatic Engineer": 2.5,
    "MIT Tech Review AI": 2.5,
    "GitHub Blog": 2.5,
    "Google AI Blog": 2.0,
    "Hacker News: AI": 1.5,
    "Hacker News: engineering": 1.5,
    "HN: AI coding agents": 1.5,
    "HN: software factory": 1.5,
    "arXiv cs.AI": 1.0,
    "arXiv cs.SE": 1.0,
    "Dev.to top": 0.5,
}
DEFAULT_WEIGHT = 1.0

# Titles announcing something you can actually pick up and use.
SIGNAL_RE = re.compile(
    r"\b(released?|launch(?:es|ed)?|ship(?:s|ped)?|open[- ]sources?d?|"
    r"introducing|now available|benchmark|v\d+(?:\.\d+)*)\b",
    re.I,
)
STOPWORDS = frozenset(
    "a an and are as at be by for from how in is it its of on or that the "
    "this to via with what when why your you we our".split()
)
SHORTLIST_SIZE = 5
CLUSTER_THRESHOLD = 0.6  # Jaccard overlap above which two titles are one story


def _tokens(title: str) -> frozenset[str]:
    words = re.findall(r"[a-z0-9]+", title.lower())
    return frozenset(w for w in words if w not in STOPWORDS and len(w) > 2)


def _same_story(a: frozenset[str], b: frozenset[str]) -> bool:
    if not a or not b:
        return False
    return len(a & b) / len(a | b) >= CLUSTER_THRESHOLD


def _cluster(items: list[Item]) -> list[list[Item]]:
    """Group items whose titles overlap enough to be the same story.

    Feeds double up (a story hits HN and the source blog; Dev.to reposts
    itself), so a story appearing in several places is signal, not noise.
    """
    clusters: list[list[Item]] = []
    keys: list[frozenset[str]] = []
    for it in items:
        toks = _tokens(it.title)
        for i, key in enumerate(keys):
            if _same_story(toks, key):
                clusters[i].append(it)
                keys[i] = key | toks
                break
        else:
            clusters.append([it])
            keys.append(toks)
    return clusters


def _recency(cluster: list[Item], now: datetime) -> float:
    stamps = [i.published for i in cluster if i.published]
    if not stamps:
        return 0.5  # undated: neither rewarded nor buried
    hours = (now - max(stamps)).total_seconds() / 3600
    return 1.5 * max(0.0, 1 - hours / LOOKBACK_HOURS)


def _score(cluster: list[Item], now: datetime) -> float:
    best_source = max(
        SOURCE_WEIGHT.get(i.source, DEFAULT_WEIGHT) for i in cluster
    )
    distinct_sources = len({i.source for i in cluster})
    signal = 0.75 if any(SIGNAL_RE.search(i.title) for i in cluster) else 0.0
    return best_source + 2.0 * (distinct_sources - 1) + _recency(cluster, now) + signal


def _why(cluster: list[Item], now: datetime) -> str:
    reasons = []
    sources = {i.source for i in cluster}
    if len(sources) > 1:
        reasons.append(f"picked up by {len(sources)} sources")
    stamps = [i.published for i in cluster if i.published]
    if stamps:
        hours = int((now - max(stamps)).total_seconds() / 3600)
        reasons.append("posted today" if hours < 24 else f"{hours}h old")
    if any(SIGNAL_RE.search(i.title) for i in cluster):
        reasons.append("announces something shippable")
    if not reasons:
        reasons.append(f"from {next(iter(sources))}")
    return "; ".join(reasons)


def _fallback_digest(items: list[Item]) -> str:
    now = datetime.now(timezone.utc)
    out = [
        "_Ranked without LLM synthesis — scored by source weight, "
        "cross-source pickup, recency, and release signals._\n"
    ]

    clusters = _cluster(items)
    collapsed = len(items) - len(clusters)
    if collapsed:
        log.info("deduped %d items -> %d stories (%d repeats)", len(items), len(clusters), collapsed)
    # One line per story, not per repost — feeds duplicate themselves freely.
    leads = [
        max(c, key=lambda i: SOURCE_WEIGHT.get(i.source, DEFAULT_WEIGHT))
        for c in clusters
    ]

    current_track = None
    for it in sorted(leads, key=lambda i: list(TRACK_ORDER).index(i.track)):
        if it.track != current_track:
            current_track = it.track
            out.append(f"\n## {current_track}\n")
        out.append(f"- [{it.title}]({it.link}) — {it.source}")

    ranked = sorted(clusters, key=lambda c: _score(c, now), reverse=True)
    out.append("\n## Shortlist: What's Worth a Look\n")
    out.append(
        "_Ranked by signal, not editorial judgement — these are the most "
        "notable items, not vetted recommendations._\n"
    )
    for n, cluster in enumerate(ranked[:SHORTLIST_SIZE], 1):
        lead = max(cluster, key=lambda i: SOURCE_WEIGHT.get(i.source, DEFAULT_WEIGHT))
        out.append(f"{n}. [{lead.title}]({lead.link}) — {_why(cluster, now)}")
    return "\n".join(out)


def synthesize(items: list[Item]) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.info("no ANTHROPIC_API_KEY — ranking locally")
        return _fallback_digest(items)

    import anthropic

    log.info("synthesizing %d items with %s", len(items), MODEL)
    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": PROMPT.format(items=_items_block(items))}],
        )
    except Exception as exc:
        # A briefing ranked locally beats no briefing at all.
        log.warning("synthesis failed (%s: %s) — ranking locally", type(exc).__name__, exc)
        return _fallback_digest(items)

    log.info(
        "synthesis ok — %d in / %d out tokens",
        message.usage.input_tokens, message.usage.output_tokens,
    )
    return "".join(block.text for block in message.content if block.type == "text")
