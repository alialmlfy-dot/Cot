#!/usr/bin/env python3
"""Staleness guard (spec section 7) — own Sunday timer, separate from the
ingest. Alerts (non-zero exit + error heartbeat) if the latest report_date is
more than `--max-age-days` (default 12) old. This is the silent-crash guard:
if the weekly ingest dies quietly, the data goes stale and this job is what
notices."""

import argparse
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import db, heartbeat
from cotcm.config import load_config
from cotcm.release_date import parse_date

MAX_AGE_DAYS = 12


def check(conn, max_age_days):
    row = conn.execute("SELECT max(report_date) FROM cot_raw").fetchone()
    latest = row[0] if row else None
    if latest is None:
        raise RuntimeError("staleness: cot_raw is empty — no data ingested")
    age = (date.today() - parse_date(latest)).days
    if age > max_age_days:
        raise RuntimeError(
            "staleness: latest report_date %s is %d days old (> %d) — weekly "
            "ingest may have died silently" % (latest, age, max_age_days))
    return {"latest_report_date": latest,
            "message": "staleness ok: latest %s, %d days old" % (latest, age)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age-days", type=int, default=MAX_AGE_DAYS)
    args = ap.parse_args()
    cfg = load_config()
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)
    try:
        r = heartbeat.run_job(conn, "staleness_check",
                              lambda: check(conn, args.max_age_days))
        print(r["message"])
    except Exception as e:
        print("STALENESS ALERT: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
