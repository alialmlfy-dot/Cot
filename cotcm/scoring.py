"""Phase 3 — §5 time-series composite, implemented with the cuts approved at
the Phase 2 gate (recorded in config.json under "signal"):

  composite = 0.40·f(hp_index)            risk-premium condition
            + 0.25·g(cot_idx_comm_3y)     commercial extreme (contrarian)
            + 0.20·h(cot_idx_mm_3y)       MM crowding (contrarian at extremes)
            + 0.15·k(z_delta_mm, oi_flag) flow confirmation/divergence

Approved cuts:
  f: per-contract anchors p10→−1, p50→0, p90→+1, piecewise linear, clipped.
     (Per-contract is structurally necessary: PL's median hedging pressure
     exceeds CL's p90 — a global anchor would misread structure as signal.)
  g/h: global contrarian band [20, 80] — 0 inside, linear ramp outside;
     g → +1 as commercial index → 100, −1 as → 0; h has the opposite sign
     (MM crowded long → bearish).
  k: clip(z_delta_mm / 2, −1, +1), gated ×1.0 for new_longs/new_shorts,
     ×0.5 for long_liquidation/short_covering/mixed.
  states: |composite| ≥ 0.50 STRONG, ≥ 0.20 LEAN, else NEUTRAL (provisional —
     confirmed against the measured composite distribution in the dry-run).
  divergence_aligned: g and h both non-zero with the same sign.
  crowding_flag: conc_pctile ≥ 90.

NULL policy: the composite requires hp_index, cot_idx_comm_3y and
cot_idx_mm_3y (the positioning core). If any is NULL (burn-in), no score row
is emitted. The flow component alone being NULL degrades to k=0 rather than
suppressing the score. Scores key off release_date (operating rule 3).
"""

import json
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clip(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


def f_hp(hp, anchors):
    p10, p50, p90 = anchors["p10"], anchors["p50"], anchors["p90"]
    if hp <= p50:
        if p50 == p10:
            return 0.0
        return _clip((hp - p50) / (p50 - p10))
    if p90 == p50:
        return 0.0
    return _clip((hp - p50) / (p90 - p50))


def g_comm(idx, band):
    lo, hi = band["low"], band["high"]
    if idx >= hi:
        return (idx - hi) / (100.0 - hi)
    if idx <= lo:
        return (idx - lo) / lo  # 0 at lo, −1 at 0
    return 0.0


def h_mm(idx, band):
    return -g_comm(idx, band)  # crowded long → bearish, crowded short → bullish


def k_flow(z, oi_flag, flow_cfg):
    if z is None:
        return 0.0
    base = _clip(z / flow_cfg["z_saturation"])
    gate = flow_cfg["oi_gate"].get(oi_flag, 0.5)
    return base * gate


def classify(composite, cuts):
    a = abs(composite)
    if a >= cuts["strong"]:
        side = "STRONG"
    elif a >= cuts["lean"]:
        side = "LEAN"
    else:
        return "NEUTRAL"
    return "%s_%s" % (side, "LONG" if composite > 0 else "SHORT")


def score_row(feat, root, sig):
    """feat: a `features` table row (sqlite3.Row). Returns score dict or None
    if the positioning core is incomplete (burn-in)."""
    hp = feat["hp_index"]
    ci_comm = feat["cot_idx_comm_3y"]
    ci_mm = feat["cot_idx_mm_3y"]
    if hp is None or ci_comm is None or ci_mm is None:
        return None
    comp_f = f_hp(hp, sig["hp_anchors"][root])
    comp_g = g_comm(ci_comm, sig["cot_band"])
    comp_h = h_mm(ci_mm, sig["cot_band"])
    comp_k = k_flow(feat["z_delta_mm"], feat["oi_flag"], sig["flow"])
    w = sig["weights"]
    composite = (w["hp"] * comp_f + w["comm"] * comp_g
                 + w["mm"] * comp_h + w["flow"] * comp_k)
    conc = feat["conc_pctile"]
    components = {
        "f_hp": round(comp_f, 4), "g_comm": round(comp_g, 4),
        "h_mm": round(comp_h, 4), "k_flow": round(comp_k, 4),
        "inputs": {"hp_index": hp, "cot_idx_comm_3y": ci_comm,
                   "cot_idx_mm_3y": ci_mm, "z_delta_mm": feat["z_delta_mm"],
                   "oi_flag": feat["oi_flag"], "conc_pctile": conc},
    }
    return {
        "cftc_code": feat["cftc_code"],
        "release_date": feat["release_date"],
        "composite": round(composite, 6),
        "state": classify(composite, sig["state_cuts"]),
        "crowding_flag": 1 if (conc is not None and conc >= sig["crowding_pctile"]) else 0,
        "divergence_aligned": 1 if (comp_g != 0.0 and comp_h != 0.0
                                    and (comp_g > 0) == (comp_h > 0)) else 0,
        "components_json": json.dumps(components),
    }


def score_all(cfg, conn):
    """Score full history for all approved+enabled contracts (needed for state
    transitions and the composite-distribution check). Idempotent
    INSERT OR REPLACE on (cftc_code, release_date)."""
    sig = cfg["signal"]
    contracts = conn.execute(
        "SELECT cftc_code, root FROM contract_map WHERE approved=1 AND enabled=1"
    ).fetchall()
    total = 0
    for code, root in contracts:
        feats = conn.execute(
            "SELECT cftc_code, release_date, hp_index, cot_idx_comm_3y, "
            "cot_idx_mm_3y, z_delta_mm, oi_flag, conc_pctile "
            "FROM features WHERE cftc_code=? ORDER BY release_date", (code,)
        ).fetchall()
        rows = []
        for ft in feats:
            s = score_row(ft, root, sig)
            if s:
                rows.append(s)
        conn.executemany(
            "INSERT OR REPLACE INTO scores (cftc_code, release_date, composite, "
            "state, crowding_flag, divergence_aligned, components_json) "
            "VALUES (:cftc_code, :release_date, :composite, :state, "
            ":crowding_flag, :divergence_aligned, :components_json)", rows)
        conn.commit()
        total += len(rows)
    return {"rows_written": total,
            "message": "scored %d contract-weeks across %d contracts"
                       % (total, len(contracts))}
