"""Daily briefing entrypoint.

Fetches sources, synthesizes, and writes briefings/YYYY-MM-DD.md.

DST guard: GitHub Actions cron is UTC-only, so the workflow fires at both
11:00 and 12:00 UTC. This script exits unless it's currently 6 AM in
America/Chicago, guaranteeing exactly one run per day at local 6:00 AM.
Set FORCE_RUN=1 to bypass the guard (e.g., manual runs).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fetch_sources import fetch_all
from synthesize import synthesize

TZ = ZoneInfo("America/Chicago")


def main() -> int:
    now_local = datetime.now(TZ)

    if os.environ.get("FORCE_RUN") != "1" and now_local.hour != 6:
        print(f"Local time is {now_local:%H:%M %Z}, not the 6 AM window. Skipping.")
        return 0

    print("Fetching sources...")
    items = fetch_all()
    print(f"Fetched {len(items)} items.")

    if not items:
        print("No items found; skipping briefing.")
        return 0

    print("Synthesizing briefing...")
    body = synthesize(items)

    out_dir = Path(__file__).resolve().parent.parent / "briefings"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{now_local:%Y-%m-%d}.md"
    header = f"# Daily Briefing — {now_local:%A, %B %d, %Y}\n\n"
    out_path.write_text(header + body + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
