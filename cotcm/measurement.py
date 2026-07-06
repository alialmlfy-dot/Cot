"""Phase 2 measurement analysis. Reads the computed `features` table and
produces distributions, dated historical extremes, and PROPOSED cut points.

This module proposes; it never decides. Nothing here writes a score or freezes
a threshold — the operator approves the cuts at the Phase 2 gate, and Phase 3
implements them.
"""

from datetime import datetime

from . import stats

NUMERIC_FEATURES = [
    "hp_index", "cot_idx_comm_3y", "cot_idx_comm_full",
    "cot_idx_mm_3y", "cot_idx_mm_full",
    "z_delta_mm", "z_delta_comm", "conc_pctile",
]
PCTLES = [0, 5, 10, 25, 50, 75, 90, 95, 100]


def _mon(d):
    return datetime.strptime(d[:10], "%Y-%m-%d").strftime("%b-%Y")


def load_feature_series(conn, cftc_code):
    rows = conn.execute(
        "SELECT release_date, hp_index, cot_idx_comm_3y, cot_idx_comm_full, "
        "cot_idx_mm_3y, cot_idx_mm_full, z_delta_mm, z_delta_comm, oi_flag, "
        "conc_pctile FROM features WHERE cftc_code=? ORDER BY release_date",
        (cftc_code,)).fetchall()
    return rows


def distribution(rows, feature):
    vals = [r[feature] for r in rows if r[feature] is not None]
    if not vals:
        return {"n": 0}
    d = {"n": len(vals)}
    for p in PCTLES:
        d["p%d" % p] = stats.percentile(vals, p)
    d["mean"] = stats.mean(vals)
    d["std"] = stats.pstdev(vals)
    return d


def episodes(rows, feature, predicate):
    """Group consecutive qualifying weeks into episodes with the peak value."""
    eps, cur = [], None
    for r in rows:
        v = r[feature]
        if v is not None and predicate(v):
            if cur is None:
                cur = {"start": r["release_date"], "end": r["release_date"],
                       "peak": v, "peak_date": r["release_date"], "weeks": 1}
            else:
                cur["end"] = r["release_date"]
                cur["weeks"] += 1
                if abs(v - 50) > abs(cur["peak"] - 50):  # for 0-100 indices
                    cur["peak"], cur["peak_date"] = v, r["release_date"]
        else:
            if cur:
                eps.append(cur)
                cur = None
    if cur:
        eps.append(cur)
    return eps


def extreme_episodes_summary(rows, feature, hi=95, lo=5):
    highs = episodes(rows, feature, lambda v: v > hi)
    lows = episodes(rows, feature, lambda v: v < lo)
    return {
        "high": [{"span": "%s..%s" % (_mon(e["start"]), _mon(e["end"])),
                  "weeks": e["weeks"], "peak": round(e["peak"], 1)} for e in highs],
        "low": [{"span": "%s..%s" % (_mon(e["start"]), _mon(e["end"])),
                 "weeks": e["weeks"], "trough": round(e["peak"], 1)} for e in lows],
    }


def oi_flag_freq(rows):
    from collections import Counter
    c = Counter(r["oi_flag"] for r in rows if r["oi_flag"] is not None)
    tot = sum(c.values())
    return {k: {"n": v, "pct": round(100.0 * v / tot, 1)} for k, v in c.items()} if tot else {}


def zdelta_tail_counts(rows, feature):
    vals = [r[feature] for r in rows if r[feature] is not None]
    n = len(vals) or 1
    return {
        "n": len(vals),
        "abs_gt_1": round(100.0 * sum(1 for v in vals if abs(v) > 1) / n, 1),
        "abs_gt_2": round(100.0 * sum(1 for v in vals if abs(v) > 2) / n, 1),
        "abs_gt_3": round(100.0 * sum(1 for v in vals if abs(v) > 3) / n, 1),
    }


def proposed_hp_anchors(rows):
    """Per-contract rescale anchors for f(hp_index): p10 -> -1, p50 -> 0,
    p90 -> +1 (time-series 'extreme for this market')."""
    d = distribution(rows, "hp_index")
    if not d.get("n"):
        return None
    return {"p10": d["p10"], "p50": d["p50"], "p90": d["p90"]}
