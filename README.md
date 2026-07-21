# Narada

A monorepo of independent projects. Each top-level directory stands alone — they
share no code and can be worked on separately.

## Contents

| Path | What it is |
| --- | --- |
| [`ai-daily-briefing/`](ai-daily-briefing/) | Python pipeline that fetches AI news sources, synthesizes a briefing with Claude, and publishes a static blog. Runs daily at 6:00 AM Chicago via GitHub Actions. |
| [`loop-engineering/`](loop-engineering/) | Nine-chapter written guide on loop engineering, plus `build.py` which renders the markdown in `content/` into the static HTML site. |
| [`files/`](files/) | Standalone reference material: the software-factory blog post and playbook archive. |

## ai-daily-briefing

Automated by [`.github/workflows/daily-briefing.yml`](.github/workflows/daily-briefing.yml).
The workflow runs on two cron entries (11:00 and 12:00 UTC) to cover both CST and
CDT; `src/main.py` exits early unless it is actually 6 AM in Chicago.

To run it locally:

```bash
pip install -r ai-daily-briefing/requirements.txt
ANTHROPIC_API_KEY=... FORCE_RUN=1 python ai-daily-briefing/src/main.py
python ai-daily-briefing/src/build_site.py
open ai-daily-briefing/site/index.html
```

Repository setup the workflow depends on:

- Add `ANTHROPIC_API_KEY` as a repository secret.
- Set Pages source to **GitHub Actions**.

## loop-engineering

```bash
python loop-engineering/build.py
open loop-engineering/index.html
```

Edit the markdown in `loop-engineering/content/` and re-run the build; the
top-level `.html` files are generated output.
