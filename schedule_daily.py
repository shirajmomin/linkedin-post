"""Optional long-running scheduler: runs the LinkedIn agent daily."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime

import schedule

from common import ROOT, load_config


def job() -> None:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] Starting scheduled LinkedIn run…")
    subprocess.run([sys.executable, str(ROOT / "run_agent.py")], check=False)


def main() -> None:
    cfg = load_config().get("schedule", {})
    when = cfg.get("daily_at", "08:30")
    print(f"Scheduler armed — daily at {when} (process must stay running)")
    print("Prefer Windows Task Scheduler for production.")
    schedule.every().day.at(when).do(job)
    if "--now" in sys.argv:
        job()
    import time

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
