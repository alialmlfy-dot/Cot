"""Phase 2 feature computation (spec section 4). Computed over full history and
stored in the `features` table — NO thresholds, NO scores here.

Rules honoured:
  - Every feature is keyed to release_date (operating rule 3), computed per
    contract in release_date order.
  - Rolling windows are in weekly observations; NO partial-window values —
    a feature emits NULL until its full window exists (spec section 4 preamble).
  - Idempotent writes: INSERT OR REPLACE on (cftc_code, release_date) so a
    recompute overwrites cleanly rather than duplicating.

Window / burn-in choices (documented so the measurement report can cite them):
  hp_index          52-week SMA                      -> from obs 52
  cot_idx_*_3y      156-week rolling min/max          -> from obs 156
  cot_idx_*_full    inception-to-date (expanding)     -> from obs 156 (aligned
                    min/max                              with the 3y series so the
                                                         two are directly comparable)
  z_delta_*         z-score vs trailing 156 WoW deltas -> from obs 157
  oi_flag           26-week trailing median of |dOI|   -> from obs 27
  conc_pctile       causal expanding percentile,        -> from obs 52 (burn-in)
                    52-week burn-in
"""

from datetime import datetime, timezone

from . import stats

W_HP = 52
W_COT = 156
W_ZDELTA = 156
W_OIMED = 26
CONC_BURNIN = 52


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cot_index(net_window, current):
    mn, mx = min(net_window), max(net_window)
    if mx == mn:
        return None
    return (current - mn) / (mx - mn) * 100.0


def _oi_flag(d_oi, d_mm, med_abs_oi):
    if abs(d_oi) < med_abs_oi:
        return "mixed"
    if d_oi > 0:
        return "new_longs" if d_mm > 0 else "new_shorts"
    else:
        return "short_covering" if d_mm > 0 else "long_liquidation"


def compute_contract(conn, cftc_code):
    """Compute all §4 features for one contract; returns list of row dicts."""
    rows = conn.execute(
        "SELECT release_date, report_date, open_interest, prod_merc_long, "
        "prod_merc_short, mm_long, mm_short, conc_net_4_long, conc_net_4_short "
        "FROM cot_raw WHERE cftc_code=? ORDER BY release_date ASC", (cftc_code,)
    ).fetchall()
    n = len(rows)
    if n == 0:
        return []

    rel = [r["release_date"] for r in rows]
    oi = [r["open_interest"] for r in rows]
    comm_net = [(r["prod_merc_long"] or 0) - (r["prod_merc_short"] or 0) for r in rows]
    mm_net = [(r["mm_long"] or 0) - (r["mm_short"] or 0) for r in rows]
    # Hedging-pressure raw: (short - long)/OI, positive = producers net short.
    hp_raw = [((r["prod_merc_short"] or 0) - (r["prod_merc_long"] or 0)) / r["open_interest"]
              if r["open_interest"] else None for r in rows]
    # Concentration: the more crowded of the two net-4 legs (squeeze context).
    conc4 = [max(r["conc_net_4_long"] or 0, r["conc_net_4_short"] or 0) for r in rows]

    # WoW deltas (index i defined for i>=1)
    d_comm = [None] + [comm_net[i] - comm_net[i - 1] for i in range(1, n)]
    d_mm = [None] + [mm_net[i] - mm_net[i - 1] for i in range(1, n)]
    d_oi = [None] + [oi[i] - oi[i - 1] for i in range(1, n)]

    out = []
    for t in range(n):
        f = {"cftc_code": cftc_code, "release_date": rel[t],
             "hp_index": None, "cot_idx_comm_3y": None, "cot_idx_comm_full": None,
             "cot_idx_mm_3y": None, "cot_idx_mm_full": None,
             "z_delta_mm": None, "z_delta_comm": None, "oi_flag": None,
             "conc_pctile": None}

        # 4.1 hp_index — 52-week SMA of hp_raw
        if t >= W_HP - 1:
            win = hp_raw[t - W_HP + 1: t + 1]
            if all(v is not None for v in win):
                f["hp_index"] = stats.mean(win)

        # 4.2 COT index (Williams) — MM and Commercial, 3y and full
        if t >= W_COT - 1:
            f["cot_idx_comm_3y"] = _cot_index(comm_net[t - W_COT + 1: t + 1], comm_net[t])
            f["cot_idx_mm_3y"] = _cot_index(mm_net[t - W_COT + 1: t + 1], mm_net[t])
            f["cot_idx_comm_full"] = _cot_index(comm_net[: t + 1], comm_net[t])
            f["cot_idx_mm_full"] = _cot_index(mm_net[: t + 1], mm_net[t])

        # 4.3 z-scored WoW delta vs trailing 156-week delta distribution
        if t >= W_ZDELTA:  # need 156 deltas ending at t (deltas start at index 1)
            win_mm = d_mm[t - W_ZDELTA + 1: t + 1]
            win_comm = d_comm[t - W_ZDELTA + 1: t + 1]
            sd_mm, sd_comm = stats.pstdev(win_mm), stats.pstdev(win_comm)
            if sd_mm:
                f["z_delta_mm"] = (d_mm[t] - stats.mean(win_mm)) / sd_mm
            if sd_comm:
                f["z_delta_comm"] = (d_comm[t] - stats.mean(win_comm)) / sd_comm

        # 4.4 OI confirmation flag
        if t >= W_OIMED:  # 26 |dOI| values ending at t
            med = stats.median([abs(x) for x in d_oi[t - W_OIMED + 1: t + 1]])
            f["oi_flag"] = _oi_flag(d_oi[t], d_mm[t], med)

        # 4.5 concentration percentile (causal, expanding, 52wk burn-in)
        if t >= CONC_BURNIN - 1:
            f["conc_pctile"] = stats.pct_rank_leq(conc4[t], conc4[: t + 1])

        out.append(f)
    return out


_INSERT = (
    "INSERT OR REPLACE INTO features (cftc_code, release_date, hp_index, "
    "cot_idx_comm_3y, cot_idx_comm_full, cot_idx_mm_3y, cot_idx_mm_full, "
    "z_delta_mm, z_delta_comm, oi_flag, conc_pctile, computed_at) "
    "VALUES (:cftc_code, :release_date, :hp_index, :cot_idx_comm_3y, "
    ":cot_idx_comm_full, :cot_idx_mm_3y, :cot_idx_mm_full, :z_delta_mm, "
    ":z_delta_comm, :oi_flag, :conc_pctile, :computed_at)"
)


def compute_all(cfg, conn):
    ts = _utcnow()
    codes = conn.execute(
        "SELECT cftc_code, root FROM contract_map WHERE approved=1 AND enabled=1 "
        "ORDER BY root").fetchall()
    total = 0
    per = []
    for code, root in codes:
        rows = compute_contract(conn, code)
        for r in rows:
            r["computed_at"] = ts
        conn.executemany(_INSERT, rows)
        conn.commit()
        nonnull = sum(1 for r in rows if r["hp_index"] is not None)
        per.append({"root": root, "cftc_code": code, "rows": len(rows),
                    "hp_nonnull": nonnull})
        total += len(rows)
    return {"rows_written": total, "per_contract": per,
            "message": "features computed for %d contracts, %d rows"
                       % (len(codes), total)}
