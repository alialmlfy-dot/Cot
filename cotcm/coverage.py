"""Coverage & gap analysis for the Phase 1 deliverable (row counts, coverage,
gap list per contract). A weekly series should step ~7 days; any consecutive
report_date jump beyond `max_gap_days` is reported as a gap (the 2019 US
government shutdown, for instance, delayed several CFTC releases)."""

from .release_date import parse_date

MAX_GAP_DAYS = 10


def cot_coverage(conn, max_gap_days=MAX_GAP_DAYS):
    out = []
    codes = conn.execute(
        "SELECT cm.cftc_code, cm.root, cm.label, cm.enabled "
        "FROM contract_map cm WHERE cm.approved=1 ORDER BY cm.root").fetchall()
    for code, root, label, enabled in codes:
        dates = [r[0] for r in conn.execute(
            "SELECT report_date FROM cot_raw WHERE cftc_code=? ORDER BY report_date",
            (code,)).fetchall()]
        gaps = []
        for a, b in zip(dates, dates[1:]):
            d = (parse_date(b) - parse_date(a)).days
            if d > max_gap_days:
                gaps.append({"from": a, "to": b, "days": d,
                             "missing_weeks": max(0, round(d / 7) - 1)})
        out.append({
            "root": root, "cftc_code": code, "label": label, "enabled": bool(enabled),
            "rows": len(dates),
            "first": dates[0] if dates else None,
            "last": dates[-1] if dates else None,
            "gaps": gaps,
        })
    return out


def price_coverage(conn):
    out = []
    codes = conn.execute(
        "SELECT cftc_code, root FROM contract_map WHERE approved=1 AND enabled=1 "
        "ORDER BY root").fetchall()
    for code, root in codes:
        row = conn.execute(
            "SELECT count(1), min(week_end_date), max(week_end_date), "
            "count(DISTINCT source) FROM prices_weekly WHERE cftc_code=?",
            (code,)).fetchone()
        src = conn.execute(
            "SELECT DISTINCT source FROM prices_weekly WHERE cftc_code=?",
            (code,)).fetchall()
        out.append({"root": root, "cftc_code": code, "rows": row[0],
                    "first": row[1], "last": row[2],
                    "sources": [s[0] for s in src]})
    return out
