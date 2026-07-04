"""Heartbeat wrapper. Every scheduled run writes a heartbeat row whether it
succeeds or fails — silent death is the failure mode we design against."""

import time
import traceback
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_heartbeat(conn, job, status, message=None, latest_report_date=None,
                    rows_written=None, duration_s=None):
    conn.execute(
        "INSERT INTO heartbeat (run_ts, job, status, latest_report_date, "
        "rows_written, duration_s, message) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (_utcnow(), job, status, latest_report_date, rows_written, duration_s, message),
    )
    conn.commit()


def run_job(conn, job, fn):
    """Run fn() under a heartbeat. fn returns an optional dict with keys
    latest_report_date / rows_written / message. Exceptions are recorded as
    status='error' with the traceback, then re-raised (loud failure)."""
    t0 = time.time()
    try:
        result = fn() or {}
        write_heartbeat(
            conn, job, "ok",
            message=result.get("message"),
            latest_report_date=result.get("latest_report_date"),
            rows_written=result.get("rows_written"),
            duration_s=round(time.time() - t0, 2),
        )
        return result
    except Exception:
        write_heartbeat(
            conn, job, "error",
            message=traceback.format_exc()[-2000:],
            duration_s=round(time.time() - t0, 2),
        )
        raise
