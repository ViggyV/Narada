# Narada Daily Briefing — Product Requirements

Status: **shipped, running daily**. Live at
[viggyv.github.io/Narada](https://viggyv.github.io/Narada/).

## Problem

Keeping up with AI tooling means checking a dozen sources that mostly repeat
each other. The signal is real but thinly spread, and skimming it costs more
time each week than it returns.

## What this does

Once a day, pull from a curated set of feeds across three tracks, collapse the
duplication, rank what's left, and publish a page short enough to read with a
coffee.

## Who it's for

One reader — the repo owner. That constraint is load-bearing: there are no
accounts, no preferences, no per-user state, and adding any of those would
change what this is. Anyone else finding the page is welcome to it.

## Tracks

| Track | Question it answers |
| --- | --- |
| AI News | What shipped or changed in the field? |
| Coding Best Practices | What should I do differently at the keyboard? |
| Software Factories | How is AI-driven software production evolving? |

## Requirements

**Runs unattended.** GitHub Actions fires two cron entries (11:00 and 12:00
UTC) so 6 AM Chicago is hit in both CST and CDT; `main.py` exits unless it is
actually the 6 AM local hour. `FORCE_RUN=1` bypasses the guard.

**Degrades instead of failing.** A dead feed is skipped, not fatal. A missing
or failing Anthropic API key falls back to local ranking. The only hard failure
is fetching zero items, which exits non-zero rather than overwriting a good
briefing with an empty one.

**Costs nothing to run.** The default path makes no paid API calls. Claude
synthesis is an upgrade, not a dependency.

**One story, once.** Feeds repeat each other and themselves. Near-identical
titles are clustered so a story appears on a single line — and repetition
across *different* sources is treated as signal rather than noise.

**Ranks honestly.** Without a key the shortlist is scored heuristically, and
says so. It does not claim editorial judgement it cannot exercise.

## How ranking works (no-key path)

```
score = source_weight                    # curated 3.0 … aggregator 0.5
      + 2.0 × (distinct_sources − 1)     # cross-source pickup
      + recency_decay(newest in cluster) # linear across the 30h window
      + 0.75 if title announces a release
```

Titles are clustered by token overlap (Jaccard ≥ 0.6) before scoring.

## Non-goals

- Full-text article fetching or summarization of source content
- Multiple users, accounts, or personalization
- A comment system, newsletter, or social distribution
- Real-time or intraday updates — this is a once-a-day artifact
- Any paid dependency in the default path

## Known issues

| Issue | Impact | Notes |
| --- | --- | --- |
| `anthropic.com/rss.xml` 404s | The two highest-weighted sources (3.0) never contribute | Anthropic appears not to publish RSS at any obvious path; needs a replacement source or removal |
| Recency dominates on quiet days | Shortlist becomes "today's items" with little differentiation | Lower the `1.5` coefficient in `_recency`, or widen the lookback |
| Dev.to reposts heavily | Absorbs slots in Coding Best Practices | Clustering collapses exact repeats; near-duplicates by the same author still get through |
| Site is light-theme only | Glares in dark mode | `site/style.css` defines no dark tokens |
| Archive is one flat list | Fine at N=1, poor at N=100 | `build_site.py` groups by month but does not paginate |

## Potential future work

Ordered roughly by value-to-effort, not committed to.

**Cheap, high value**
- Drop or replace the dead Anthropic feeds so the top weights actually apply
- Dark-theme tokens in `site/style.css`
- Emit fetch stats into the page footer (feeds live/dead, item count) so
  degradation is visible to the reader, not just in CI logs
- A `--dry-run` flag that prints the briefing without writing files

**Moderate**
- Per-source health tracking across runs — a feed that returns nothing for
  N consecutive days is probably dead, not quiet
- Tune ranking weights against a hand-labelled sample rather than by feel
- Deduplicate across *days*, so a story trending for 48h stops reappearing
- RSS/Atom output so the briefing can be read in a reader

**Larger**
- Fetch article text and rank on content rather than titles
- Let Claude select sources, not just summarize them
- Track which links actually get clicked and feed that back into weights
