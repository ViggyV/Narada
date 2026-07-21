"""Daily briefing entrypoint.

Fetches sources, synthesizes, and writes briefings/YYYY-MM-DD.md.

DST guard: GitHub Actions cron is UTC-only, so the workflow fires at both
11:00 and 12:00 UTC. This script exits unless it's currently 6 AM in
America/Chicago, guaranteeing exactly one run per day at local 6:00 AM.
Set FORCE_RUN=1 to bypass the guard (e.g., manual runs).
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fetch_sources import fetch_all
from synthesize import synthesize

TZ = ZoneInfo("America/Chicago")

log = logging.getLogger("narada")


def _setup_logging() -> None:
    """Timestamped logs; LOG_LEVEL=DEBUG for per-feed detail."""
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


def main() -> int:
    _setup_logging()
    now_local = datetime.now(TZ)

    if os.environ.get("FORCE_RUN") != "1" and now_local.hour != 6:
        log.info("local time is %s, not the 6 AM window — skipping", f"{now_local:%H:%M %Z}")
        return 0

    items = fetch_all()
    if not items:
        # Every feed failed or everything was stale; leave yesterday's briefing
        # in place rather than overwriting it with an empty one.
        log.error("no items fetched — not writing a briefing")
        return 1

    body = synthesize(items)

    out_dir = Path(__file__).resolve().parent.parent / "briefings"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{now_local:%Y-%m-%d}.md"
    header = f"# Daily Briefing — {now_local:%A, %B %d, %Y}\n\n"
    out_path.write_text(header + body + "\n", encoding="utf-8")
    log.info("wrote %s (%d bytes)", out_path.name, out_path.stat().st_size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
