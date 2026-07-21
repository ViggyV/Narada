"""Turn fetched items into a short, prioritized 'what to implement' list.

If ANTHROPIC_API_KEY is set, Claude does the synthesis.
Otherwise, falls back to a plain grouped digest so the pipeline never fails.
"""
from __future__ import annotations

import os

from fetch_sources import Item

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


def _fallback_digest(items: list[Item]) -> str:
    out = ["_Generated without LLM synthesis (no ANTHROPIC_API_KEY set)._\n"]
    current_track = None
    for it in items:
        if it.track != current_track:
            current_track = it.track
            out.append(f"\n## {current_track}\n")
        out.append(f"- [{it.title}]({it.link}) — {it.source}")
    out.append("\n## Shortlist: What's Worth Implementing\n")
    out.append("_Add an `ANTHROPIC_API_KEY` repo secret to enable the ranked shortlist._")
    return "\n".join(out)


def synthesize(items: list[Item]) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_digest(items)

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT.format(items=_items_block(items))}],
    )
    return "".join(block.text for block in message.content if block.type == "text")
