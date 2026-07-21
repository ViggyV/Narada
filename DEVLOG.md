# Dev log

Newest first. Records what changed and *why* — the reasoning that the diff
itself doesn't carry.

---

## 2026-07-21 — Logging, PRD, dev log

Added real logging to the pipeline. It paid for itself immediately: the first
run surfaced that **both Anthropic feeds have been dead the whole time**.
`https://www.anthropic.com/rss.xml` returns HTML with a 404, and
`fetch_sources.fetch_all()` had a bare `except Exception: continue` that
swallowed it silently. Those two sources carry the highest weight in the
ranking (3.0), so the scoring table's top tier was never contributing.

Probed five plausible replacement paths (`/news/rss.xml`, `/feed.xml`,
`/index.xml`, `/engineering/rss.xml`) — all 404. Left the feeds in place and
documented it rather than guessing a URL or quietly deleting sources someone
chose on purpose.

Two behavioural changes worth flagging:

- `feedparser` reports most failures via a `bozo` flag rather than raising, so
  the old `try/except` never fired for the most common failure mode. Now checks
  `bozo` and empty-entry cases explicitly.
- Fetching **zero** items now exits non-zero instead of silently succeeding.
  Previously an all-feeds-down day would overwrite a good briefing with an
  empty one and report success. Now the job fails loudly and yesterday's
  briefing stays up. This makes CI red on a total outage — deliberate.

Also wrapped the Claude call in a `try/except` that falls back to local
ranking. A synthesis failure shouldn't cost the whole briefing.

Wrote `ai-daily-briefing/PRD.md` (scope, non-goals, known issues, roadmap) and
this log.

## 2026-07-21 — Security cleanup

Deleted `install.sh`. It copied files into a repo that already contained them —
its job was done the moment the layout was flattened — and it hard-coded
`/Users/<name>/dev/Narada`, which became a public detail when the repo went
public.

Moved commit identity to `36783496+ViggyV@users.noreply.github.com` as a
**repo-local** config, leaving the global config alone so other projects are
unaffected. Later rewrote history to scrub the old address from earlier commits.

Bumped four workflow actions off Node 20 (`checkout@v4→v7`,
`setup-python@v5→v7`, `upload-pages-artifact@v3→v5`, `deploy-pages@v4→v5`) and
re-ran CI to confirm the major bumps didn't break anything.

## 2026-07-21 — Public + GitHub Pages

Repo made public and Pages enabled with `build_type: workflow` (the existing
workflow uploads an artifact, so branch-deploy wouldn't have worked). Site live
at `https://viggyv.github.io/Narada/`.

Scanned for secrets before flipping visibility — none. Two minor exposures
found and dealt with in the cleanup above.

## 2026-07-21 — Links open in a new tab

Every link in a briefing is outbound and readers work down the list, so
navigating away on each click was wrong. Added `target="_blank"` plus
`rel="noopener noreferrer"` in `build_site.py`; relative in-site links are left
alone.

Verified by clicking through on the deployed site, not by reading the markup.

Worth recording because the same change **breaks** links inside a sandboxed
frame: the Claude artifact preview runs with
`sandbox="allow-scripts allow-same-origin allow-forms"` — no `allow-popups` —
so `target="_blank"` clicks are inert there. Removing `target` is worse: the
click navigates the frame, the destination refuses to be framed, and the page
goes blank. GitHub Pages is the only host where these links behave properly.

## 2026-07-21 — Rank the no-key digest

`synthesize.py`'s fallback path emitted a placeholder where the shortlist
should be, so every run without `ANTHROPIC_API_KEY` produced a briefing with
its most useful section empty.

Replaced it with heuristic scoring: source weight, cross-source pickup,
recency, release-signal keywords. Titles are clustered by token overlap so a
story carried by several feeds counts once and scores *higher* for the pickup.

The clustering turned out to matter more than the ranking — it caught that
Dev.to reposts the same article repeatedly (one piece appeared four times,
another three). 32 items collapsed to 27 stories.

Renamed the section from "What's Worth Implementing" to "What's Worth a Look".
A keyword-and-recency score can tell you a story got traction; it can't tell
you whether to adopt it, and the old title claimed judgement the code doesn't
have.

## 2026-07-20 — Repo setup

Three unrelated projects (`ai-daily-briefing`, `loop-engineering`, `files`)
committed as a monorepo in five logical commits.

`narada/` turned out to be a staging bundle rather than a project: its
`install.sh` showed the intended layout put `ai-daily-briefing/` and `.github/`
at the *repo root*, which is exactly what the workflow's paths already assumed.
Flattening it meant **zero** path edits to the CI file — keeping the wrapper
would have broken every path in it.
