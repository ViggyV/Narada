# Narada Daily Briefing

Runs every day at **6:00 AM (America/Chicago)** via GitHub Actions. Scans the last ~30 hours across three tracks — AI news, coding best practices, and software factories (AI-driven/agentic development) — has Claude distill a ranked "Shortlist: What's Worth Implementing," writes `briefings/YYYY-MM-DD.md`, and rebuilds the blog in `site/`.

## Read it

- **Locally:** open `ai-daily-briefing/site/index.html` in a browser.
- **On the web:** repo Settings → Pages → Source: **GitHub Actions**. The workflow deploys `site/` automatically.

## Enable the schedule

1. Push to GitHub.
2. Add repo secret `ANTHROPIC_API_KEY` (Settings → Secrets and variables → Actions). Without it the briefing is a raw link digest instead of a ranked shortlist.
3. Test via Actions → Daily Briefing → **Run workflow** (manual runs skip the 6 AM guard).

## DST note

GitHub cron is UTC-only, so the workflow fires at 11:00 and 12:00 UTC; `src/main.py` proceeds only when it's genuinely 6 AM in Chicago — exactly one run per day, year-round. Change `TZ` in `src/main.py` and the cron lines to move it.

## Customize

- Feeds: `src/fetch_sources.py` (`FEEDS` dict — any RSS/Atom URL).
- Shortlist prompt: `src/synthesize.py`.
- Blog design: `src/build_site.py` (`CSS` block).

## Run locally

```bash
pip install -r ai-daily-briefing/requirements.txt
ANTHROPIC_API_KEY=sk-... FORCE_RUN=1 python ai-daily-briefing/src/main.py
python ai-daily-briefing/src/build_site.py
```
