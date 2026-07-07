#!/usr/bin/env python3
"""Weekly pipeline — the scheduled job (systemd timer, Saturday 06:00
Asia/Riyadh, after the Friday 15:30 ET CFTC release).

Live as of the Phase 4 go-live (2026-07-07, context-only operation):
  1. incremental COT ingest        (integrity-gated, idempotent)
  2. weekly price refresh          (Yahoo primary, stooq fallback)
  3. feature recompute             (§4, keyed to release_date)
  4. composite scoring             (§5, frozen weights and cuts)
  5. weekly report artifact        (md + json, standing caveat included)

Each step runs under its own heartbeat; a step failure writes an error
heartbeat, skips the dependent steps, and exits non-zero (loud failure).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import cftc_ingest, db, features, heartbeat, price_ingest, scoring, weekly_report
from cotcm.config import load_config


def main():
    cfg = load_config()
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)
    failed = False

    def step(job, fn, skip=False):
        nonlocal failed
        if skip:
            print("%s: skipped (COT ingest failed)" % job, file=sys.stderr)
            return None
        try:
            r = heartbeat.run_job(conn, job, fn)
            print(r.get("message"))
            return r
        except Exception as e:
            failed = True
            print("%s FAILED: %s" % (job, e), file=sys.stderr)
            return None

    cot_ok = step("weekly_cot", lambda: cftc_ingest.incremental(cfg, conn)) is not None
    # Prices are not an input to scoring — a price-source outage is recorded
    # (failure heartbeat + non-zero exit) but must not block the report.
    step("weekly_prices", lambda: price_ingest.ingest_prices(cfg, conn))
    # Features/scores/report depend on COT data being intact.
    step("weekly_features", lambda: features.compute_all(cfg, conn), skip=not cot_ok)
    step("weekly_scores", lambda: scoring.score_all(cfg, conn), skip=not cot_ok)

    def report():
        row = conn.execute("SELECT max(release_date) FROM scores").fetchone()
        if not row or not row[0]:
            raise RuntimeError("no scored release dates — nothing to report")
        md, js, payload = weekly_report.write_report(cfg, conn, row[0])
        return {"latest_report_date": row[0],
                "message": "weekly report written: %s (transitions: %s)"
                           % (md, ", ".join(payload["transitions"]) or "none")}

    step("weekly_report", report, skip=not cot_ok)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
