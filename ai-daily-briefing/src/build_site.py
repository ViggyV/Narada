"""Build a readable static blog from briefings/*.md into site/.

Run after main.py. No server needed: open site/index.html locally,
or serve via GitHub Pages (the workflow deploys site/ automatically).
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
BRIEFINGS = ROOT / "briefings"
SITE = ROOT / "site"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
    "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400"
    '&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">'
)

SUN = (
    '<svg class="horizon" viewBox="0 0 640 44" aria-hidden="true" '
    'preserveAspectRatio="xMidYMax meet">'
    '<circle cx="320" cy="44" r="26" fill="var(--marigold)"/>'
    '<rect x="0" y="42" width="640" height="2" fill="var(--ink)"/>'
    "</svg>"
)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{fonts}
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header class="masthead">
  {sun}
  <a class="wordmark" href="{root}index.html">Narada</a>
  <p class="tagline">The daily briefing &mdash; carried in at first light, 6:00&nbsp;AM</p>
</header>
<main>
{body}
</main>
<footer>
  <p>Gathered from AI news, coding practice, and the software-factory frontier.
  Generated each morning by the Narada pipeline.</p>
  <p class="sibling">Also here: <a href="{root}loop-engineering/">Loop Engineering</a>
  &mdash; a written guide to building agent loops.</p>
</footer>
</body>
</html>
"""


def _shortlist_markup(html: str) -> str:
    """Give the shortlist section its own styled block."""
    m = re.search(r"<h2[^>]*>\s*Shortlist[^<]*</h2>", html)
    if not m:
        return html
    head, tail = html[: m.start()], html[m.start() :]
    return head + '<section class="shortlist">' + tail + "</section>"


def _open_offsite(html: str) -> str:
    """Send outbound links to a new tab.

    Every link in a briefing points off-site, and readers work down the list —
    losing the page on each click is the wrong default. `noopener` also keeps
    the opened page from reaching back through `window.opener`.
    """
    # The lookahead keeps this idempotent: an anchor that already carries a
    # target is skipped, so re-running over built output can't stack duplicate
    # attributes onto the same tag.
    return re.sub(
        r'<a href="(https?://[^"]*)"(?![^>]*\btarget=)',
        r'<a href="\1" target="_blank" rel="noopener noreferrer"',
        html,
    )


def render_post(md_path: Path) -> tuple[str, str, datetime]:
    raw = md_path.read_text(encoding="utf-8")
    date = datetime.strptime(md_path.stem, "%Y-%m-%d")
    # Drop the H1; the page hero replaces it
    raw = re.sub(r"^# .*\n", "", raw, count=1)
    body_html = markdown.markdown(raw, extensions=["extra"])
    body_html = _shortlist_markup(body_html)
    body_html = _open_offsite(body_html)
    hero = (
        '<p class="eyebrow">Briefing &middot; No. {n}</p>'
        '<h1 class="date-hero">{pretty}</h1>'
    )
    article = f'<article>{hero}{body_html}</article>'
    back = '<nav class="crumb"><a href="../index.html">&larr; All briefings</a></nav>'
    return back + article, md_path.stem, date


def build() -> None:
    SITE.mkdir(exist_ok=True)
    (SITE / "posts").mkdir(exist_ok=True)
    (SITE / "style.css").write_text(CSS, encoding="utf-8")

    posts = sorted(BRIEFINGS.glob("????-??-??.md"), reverse=True)
    total = len(posts)

    entries = []
    for i, p in enumerate(posts):
        body, slug, date = render_post(p)
        number = total - i
        body = body.replace("{n}", str(number)).replace(
            "{pretty}", date.strftime("%A, %B %-d, %Y")
        )
        html = PAGE.format(
            title=f"Narada &mdash; {date:%B %-d, %Y}",
            fonts=FONTS, sun=SUN, root="../", body=body,
        )
        (SITE / "posts" / f"{slug}.html").write_text(html, encoding="utf-8")
        entries.append((date, slug, number))

    # Index: archive grouped by month
    items, current_month = [], None
    for date, slug, number in entries:
        month = date.strftime("%B %Y")
        if month != current_month:
            if current_month is not None:
                items.append("</ul>")
            items.append(f'<h2 class="month">{month}</h2><ul class="archive">')
            current_month = month
        items.append(
            f'<li><span class="no">No. {number}</span>'
            f'<a href="posts/{slug}.html">{date.strftime("%A, %B %-d")}</a></li>'
        )
    if entries:
        items.append("</ul>")
    else:
        items.append('<p class="empty">No briefings yet. The first one arrives at 6:00 AM.</p>')

    index = PAGE.format(
        title="Narada &mdash; Daily Briefing",
        fonts=FONTS, sun=SUN, root="", body="\n".join(items),
    )
    (SITE / "index.html").write_text(index, encoding="utf-8")
    print(f"Built site with {total} briefing(s) -> {SITE}")


CSS = """:root {
  --paper: #F2F4F8;
  --ink: #212842;
  --marigold: #DD9C2E;
  --peacock: #24736E;
  --muted: #6C7387;
  --line: #D9DEE9;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Newsreader", Georgia, serif;
  font-size: 1.125rem;
  line-height: 1.65;
}
.masthead { max-width: 42rem; margin: 0 auto; padding: 3rem 1.25rem 0; text-align: center; }
.horizon { display: block; width: 100%; height: 44px; margin-bottom: 1.4rem; }
.wordmark {
  font-family: "Instrument Serif", serif;
  font-size: clamp(2.6rem, 7vw, 4rem);
  letter-spacing: 0.02em;
  color: var(--ink);
  text-decoration: none;
}
.tagline {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0.4rem 0 0;
}
main { max-width: 42rem; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
.crumb { margin-bottom: 2rem; }
.crumb a, .archive a { color: var(--peacock); text-decoration: none; }
.crumb a:hover, .archive a:hover, article a:hover { text-decoration: underline; }
.eyebrow {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--marigold);
  margin: 0 0 0.3rem;
}
.date-hero {
  font-family: "Instrument Serif", serif;
  font-weight: 400;
  font-size: clamp(2rem, 6vw, 3.1rem);
  line-height: 1.1;
  margin: 0 0 2rem;
}
article h2 {
  font-family: "Instrument Serif", serif;
  font-weight: 400;
  font-size: 1.7rem;
  margin: 2.4rem 0 0.8rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.35rem;
}
article a { color: var(--peacock); text-decoration: none; }
article li { margin: 0.45rem 0; }
article blockquote {
  margin: 0.6rem 0 0.6rem 0;
  padding-left: 1rem;
  border-left: 2px solid var(--line);
  color: var(--muted);
  font-style: italic;
}
.shortlist {
  margin-top: 2.6rem;
  padding: 0.4rem 1.4rem 1.1rem;
  background: #FFFFFF;
  border-left: 4px solid var(--marigold);
  border-radius: 0 6px 6px 0;
}
.shortlist h2 { border-bottom: none; }
.month {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 2.2rem 0 0.6rem;
}
.archive { list-style: none; margin: 0; padding: 0; }
.archive li {
  display: flex;
  gap: 1rem;
  align-items: baseline;
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--line);
}
.archive .no {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.78rem;
  color: var(--marigold);
  min-width: 4.2rem;
}
.archive a { font-size: 1.2rem; }
.empty { color: var(--muted); text-align: center; margin-top: 3rem; }
footer {
  max-width: 42rem;
  margin: 0 auto;
  padding: 0 1.25rem 3rem;
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.72rem;
  color: var(--muted);
  text-align: center;
}
footer a { color: var(--peacock); text-decoration: none; }
footer a:hover, footer a:focus-visible { text-decoration: underline; }
.sibling { margin-top: 1.1rem; }
@media (prefers-reduced-motion: no-preference) {
  article, .archive { animation: rise 0.5s ease-out; }
  @keyframes rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; } }
}
"""

if __name__ == "__main__":
    build()
