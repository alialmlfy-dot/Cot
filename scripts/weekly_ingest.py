#!/usr/bin/env python3
"""Weekly incremental ingest — the scheduled job (systemd timer, Saturday
06:00 Asia/Riyadh, after the Friday 15:30 ET CFTC release). Pulls the latest
COT report date and refreshes weekly prices. Runs under the heartbeat wrapper;
a failure writes an error heartbeat and exits non-zero (loud failure)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import cftc_ingest, db, heartbeat, price_ingest
from cotcm.config import load_config


def main():
    cfg = load_config()
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)
    failed = False
    try:
        r = heartbeat.run_job(conn, "weekly_cot", lambda: cftc_ingest.incremental(cfg, conn))
        print(r.get("message"))
    except Exception as e:
        failed = True
        print("weekly_cot FAILED: %s" % e, file=sys.stderr)
    try:
        r = heartbeat.run_job(conn, "weekly_prices", lambda: price_ingest.ingest_prices(cfg, conn))
        print(r.get("message"))
    except Exception as e:
        failed = True
        print("weekly_prices FAILED: %s" % e, file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
