#!/usr/bin/env python3
"""Build the Loop Engineering blog from content/*.md into this folder.

Usage:  python3 build.py        (requires: pip install markdown)
Then open index.html, or serve with:  python3 -m http.server 8000
"""
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"

POSTS = [
    # (md file, slug, num, title, one-liner, [stage chips])
    ("01-what-is-loop-engineering.md", "what-is-loop-engineering", "01",
     "What Is Loop Engineering?",
     "The concept, its origin, why it emerged in 2026 — and the corrected attribution.",
     ["CONCEPT"]),
    ("02-anatomy-of-a-loop.md", "anatomy-of-a-loop", "02",
     "Anatomy of a Loop",
     "The unified six-component architecture, seen through Anthropic's agent-harness lens.",
     ["TRIGGER", "WORK", "VERIFY", "MEMORY"]),
    ("03-triggers.md", "triggers", "03",
     "Triggers & Schedulers",
     "/loop, Routines, scheduled tasks, GitHub Actions, and Managed Agents schedules.",
     ["TRIGGER"]),
    ("04-skills-and-harness-design.md", "skills-and-harness-design", "04",
     "Skills-First Discipline & Harness Design",
     "No loop without a battle-tested skill — and the standing question: what can I stop doing?",
     ["WORK"]),
    ("05-verification.md", "verification", "05",
     "Verification: Maker vs. Checker",
     "/goal, Outcomes graders, self-preference bias, and the five-tier verification ladder.",
     ["VERIFY"]),
    ("06-memory.md", "memory", "06",
     "Memory & State",
     "The agent forgets; the repo doesn't. Memory layers, state files, and Dreaming.",
     ["MEMORY"]),
    ("07-parallelism-and-dynamic-workflows.md", "parallelism-and-dynamic-workflows", "07",
     "Parallelism, Worktrees & Dynamic Workflows",
     "Isolation lanes, multiagent orchestration, and the 750k-line Bun rewrite.",
     ["SCALE"]),
    ("08-safety-cost-security.md", "safety-cost-security", "08",
     "Safety, Cost & Security",
     "Stop rules, token economics, the MCP attack surface, and harness boundaries.",
     ["GUARD"]),
    ("09-playbook.md", "playbook", "09",
     "The Implementation Playbook",
     "Go/no-go test, the nine-step build sequence, anti-patterns, graduation benchmarks.",
     ["BUILD"]),
]

MD_TO_SLUG = {p[0]: p[1] + ".html" for p in POSTS}
MD_TO_SLUG["00-README.md"] = "index.html"

LOOP_MARK = """<svg class="loop-glyph" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
  <g class="rotor"><path d="M12 3a9 9 0 1 0 9 9" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M17.5 1.5 21 3l-1.5 3.5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>
</svg>"""

SCHEMATIC = """<svg class="schematic" width="340" height="330" viewBox="0 0 340 330" role="img"
  aria-label="Schematic of a loop: trigger, work, verify, remember, cycling, with a human review gate on the output">
  <circle class="orbit" cx="170" cy="160" r="112"/>
  <g class="loop-glyph"><g class="rotor">
    <path class="arrowline" d="M170 34 A126 126 0 0 1 296 160" />
    <path class="arrowline" d="M296 160 A126 126 0 0 1 170 286" />
    <path class="arrowline" d="M170 286 A126 126 0 0 1 44 160" />
    <path class="arrowline" d="M44 160 A126 126 0 0 1 170 34" />
    <path class="arrowline" d="M288 138 l8 22 l-22 8" fill="none" stroke-linejoin="round"/>
    <path class="arrowline" d="M52 182 l-8 -22 l22 -8" fill="none" stroke-linejoin="round"/>
  </g></g>
  <g>
    <rect class="stage-node" x="128" y="16" width="84" height="34" rx="3"/>
    <text class="stage-label" x="170" y="37" text-anchor="middle">TRIGGER</text>
    <rect class="stage-node" x="256" y="143" width="70" height="34" rx="3"/>
    <text class="stage-label" x="291" y="164" text-anchor="middle">WORK</text>
    <rect class="stage-node" x="132" y="269" width="76" height="34" rx="3"/>
    <text class="stage-label" x="170" y="290" text-anchor="middle">VERIFY</text>
    <rect class="stage-node" x="8" y="143" width="86" height="34" rx="3"/>
    <text class="stage-label" x="51" y="164" text-anchor="middle">REMEMBER</text>
  </g>
  <g>
    <path class="human" d="M208 292 h60" stroke-dasharray="4 4"/>
    <path class="human" d="M262 286 l8 6 l-8 6" fill="none"/>
    <text class="stage-label human-label" x="278" y="296">HUMAN REVIEW</text>
  </g>
</svg>"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800'
         '&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400..700'
         '&family=Spline+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">')

MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "smarty"])


def render(md_text: str) -> str:
    # rewrite internal .md links to .html slugs
    def relink(m):
        target = m.group(2)
        return f"{m.group(1)}{MD_TO_SLUG.get(target, target)}{m.group(3)}"
    md_text = re.sub(r"(\]\()([0-9]{2}-[a-z0-9\-]+\.md)(\))", relink, md_text)
    MD.reset()
    html = MD.convert(md_text)
    # card-style the TL;DR list; make tables scrollable on mobile
    html = html.replace("<h2>TL;DR</h2>\n<ul>", '<h2>TL;DR</h2>\n<ul class="tldr">', 1)
    html = html.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
    return html


def topbar(crumb: str, prev_href: str | None, next_href: str | None) -> str:
    nav = ""
    if prev_href is not None or next_href is not None:
        p = f'<a href="{prev_href}">&larr; prev</a>' if prev_href else '<a aria-disabled="true">&larr; prev</a>'
        n = f'<a href="{next_href}">next &rarr;</a>' if next_href else '<a aria-disabled="true">next &rarr;</a>'
        nav = f"<nav>{p} {n}</nav>"
    return (f'<header class="topbar"><a class="mark" href="index.html">{LOOP_MARK}'
            f'<span class="wordmark">Loop Engineering</span></a>'
            f'<span class="crumb">{crumb}</span><span class="spacer"></span>{nav}</header>')


def page(title: str, body: str, desc: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{FONTS}
<link rel="stylesheet" href="style.css">
</head>
<body>
{body}
<footer class="site">LOOP ENGINEERING FIELD MANUAL &middot; SOURCES CURRENT TO JUL 2026 &middot; BUILT FROM /content</footer>
</body>
</html>
"""


def build_posts():
    for i, (mdfile, slug, num, title, sub, chips) in enumerate(POSTS):
        text = (CONTENT / mdfile).read_text()
        # strip the H1 (rebuilt in template) and trailing nav arrows
        text = re.sub(r"^# .+?\n", "", text, count=1)
        text = re.sub(r"\n(→|←) (Next|Back to).*$", "", text.strip(), flags=re.S)
        body_html = render(text)
        prev_p = POSTS[i - 1] if i > 0 else None
        next_p = POSTS[i + 1] if i < len(POSTS) - 1 else None
        pager = '<nav class="pager">'
        if prev_p:
            pager += (f'<a href="{prev_p[1]}.html"><span class="dir">&larr; FILE {prev_p[2]}</span>'
                      f'<span class="ptitle">{prev_p[3]}</span></a>')
        if next_p:
            pager += (f'<a class="next" href="{next_p[1]}.html"><span class="dir">FILE {next_p[2]} &rarr;</span>'
                      f'<span class="ptitle">{next_p[3]}</span></a>')
        pager += "</nav>"
        chips_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
        body = (topbar(f"FILE {num} / 09",
                       f"{prev_p[1]}.html" if prev_p else None,
                       f"{next_p[1]}.html" if next_p else None)
                + f'''<main class="article-wrap"><article>
<div class="article-head">
  <div class="file-eyebrow"><span>FILE {num} / 09</span><span class="rule"></span><span class="chips">{chips_html}</span></div>
  <h1>{title}</h1>
</div>
{body_html}
</article></main>''' + pager)
        (ROOT / f"{slug}.html").write_text(page(f"{title} — Loop Engineering", body, sub))
        print(f"  built {slug}.html")


def build_index():
    readme = (CONTENT / "00-README.md").read_text()
    # keep only the sections after the series table (what's new + sources)
    tail = readme.split("## What's new in this edition", 1)[1]
    appendix_html = render("## What's new in this edition" + tail)
    entries = ""
    for mdfile, slug, num, title, sub, chips in POSTS:
        chips_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
        entries += (f'<a class="entry" href="{slug}.html"><span class="num mono">{num}</span>'
                    f'<span><span class="title">{title}</span><span class="sub">{sub}</span></span>'
                    f'<span class="chips">{chips_html}</span></a>\n')
    body = topbar("SERIES INDEX", None, None) + f'''
<section class="hero"><div class="hero-inner">
  <div>
    <span class="eyebrow">A field manual &middot; 9 files &middot; sources verified Jul 2026</span>
    <h1>Stop prompting.<br>Start <span class="accent">writing loops.</span></h1>
    <p class="lede">Loop engineering is designing the system that prompts the agent for you —
    it finds work, hands it out, verifies it, records progress, and decides the next step.
    <em>This series covers every component with verified Claude Code and Claude Platform primitives.</em></p>
  </div>
  {SCHEMATIC}
</div></section>
<main class="runlog">
  <div class="runlog-head"><h2>The series</h2><span class="count mono">RUN ORDER 01&ndash;09</span></div>
  {entries}
</main>
<section class="appendix"><article>{appendix_html}</article></section>'''
    (ROOT / "index.html").write_text(page(
        "Loop Engineering — a field manual for self-running agent systems", body,
        "A nine-part field manual on loop engineering with Claude Code: triggers, skills, verification, memory, parallelism, and safety."))
    print("  built index.html")


if __name__ == "__main__":
    print("Building Loop Engineering site…")
    build_posts()
    build_index()
    print("Done. Open index.html (or: python3 -m http.server 8000)")
