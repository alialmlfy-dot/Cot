"""Phase 4 — backtest harness (spec §6). Pure Python stdlib.

Discipline enforced here:
  - Signal timing: everything keys off release_date Friday close; forward
    returns are release_date -> release_date + h weeks. Anything else is
    lookahead (operating rule 3 / §6).
  - IC first: per-feature rank IC is computed on RAW features (which are
    causal by construction) and is delivered before any composite result.
  - Walk-forward: the live engine's hp anchors were measured on the full
    sample. The backtest does NOT use them. It re-derives anchors causally —
    expanding window, 2006–2014 burn-in, 1-year steps — so no test week is
    scored with information from its own future. The 20/80 band and
    0.35/0.20 cuts are held fixed (structural constants; their full-sample
    origin is disclosed in the report's honesty notes).
  - Costs: 5 bps per side (config) on position changes; gross and net.
  - Every Sharpe is accompanied by a Deflated Sharpe Ratio with the honest
    trial count (2 configurations tried: provisional 0.50 cut, approved 0.35).
"""

import math
from datetime import date, timedelta
from statistics import NormalDist

from . import scoring, stats

_ND = NormalDist()
EULER_GAMMA = 0.5772156649015329

FEATURES_FOR_IC = [
    "hp_index", "cot_idx_comm_3y", "cot_idx_comm_full",
    "cot_idx_mm_3y", "cot_idx_mm_full",
    "z_delta_mm", "z_delta_comm", "conc_pctile",
]


# ---------------------------------------------------------------- returns

def price_map(conn, code):
    return {r[0]: r[1] for r in conn.execute(
        "SELECT week_end_date, close FROM prices_weekly WHERE cftc_code=?", (code,))}


def forward_returns(conn, code, horizons):
    """{release_date: {h: fwd simple return}} using Friday closes only."""
    pm = price_map(conn, code)
    rds = [r[0] for r in conn.execute(
        "SELECT DISTINCT release_date FROM cot_raw WHERE cftc_code=? "
        "ORDER BY release_date", (code,))]
    out = {}
    for rd in rds:
        p0 = pm.get(rd)
        if not p0:
            continue
        d0 = date.fromisoformat(rd)
        fr = {}
        for h in horizons:
            p1 = pm.get((d0 + timedelta(weeks=h)).isoformat())
            if p1:
                fr[h] = p1 / p0 - 1.0
        if fr:
            out[rd] = fr
    return out


# ---------------------------------------------------------------- IC

def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            rk[order[k]] = avg
        i = j + 1
    return rk


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return None
    return cov / math.sqrt(vx * vy)


def ic_table(conn, code, fwd, horizons):
    """Rank IC of each raw feature vs forward returns, one contract."""
    feats = conn.execute(
        "SELECT * FROM features WHERE cftc_code=? ORDER BY release_date",
        (code,)).fetchall()
    out = {}
    for name in FEATURES_FOR_IC:
        out[name] = {}
        for h in horizons:
            xs, ys = [], []
            for ft in feats:
                v = ft[name]
                fr = fwd.get(ft["release_date"], {}).get(h)
                if v is not None and fr is not None:
                    xs.append(v)
                    ys.append(fr)
            rho = spearman(xs, ys)
            n = len(xs)
            t = (rho * math.sqrt((n - 2) / max(1e-12, 1 - rho * rho))
                 if rho is not None and n > 2 else None)
            out[name][h] = {"rho": rho, "n": n, "t": t}
    return out


# ---------------------------------------------------------------- walk-forward

def walk_forward_scores(conn, cfg, first_test_year=2015):
    """Causal re-scoring: for each test year Y, hp anchors are percentiles of
    hp_index observed strictly before Y-01-01 (expanding window, burn-in
    2006-2014). Returns rows {cftc_code, root, release_date, composite, state}."""
    sig_base = cfg["signal"]
    rows = []
    contracts = conn.execute(
        "SELECT cftc_code, root FROM contract_map WHERE approved=1 AND enabled=1 "
        "ORDER BY root").fetchall()
    for code, root in contracts:
        feats = conn.execute(
            "SELECT * FROM features WHERE cftc_code=? ORDER BY release_date",
            (code,)).fetchall()
        last_year = int(feats[-1]["release_date"][:4]) if feats else first_test_year
        for year in range(first_test_year, last_year + 1):
            cutoff = "%d-01-01" % year
            hist = [f["hp_index"] for f in feats
                    if f["hp_index"] is not None and f["release_date"] < cutoff]
            if len(hist) < 100:
                continue
            anchors = {"p10": stats.percentile(hist, 10),
                       "p50": stats.percentile(hist, 50),
                       "p90": stats.percentile(hist, 90)}
            sig = dict(sig_base)
            sig["hp_anchors"] = {root: anchors}
            for ft in feats:
                rd = ft["release_date"]
                if rd[:4] != str(year):
                    continue
                s = scoring.score_row(ft, root, sig)
                if s:
                    rows.append({"cftc_code": code, "root": root,
                                 "release_date": rd,
                                 "composite": s["composite"],
                                 "state": s["state"]})
    return rows


# ---------------------------------------------------------------- conditioned stats

def _tstat(vals, h):
    """Mean t-stat with conservative sqrt(h) SE inflation for overlapping
    multi-week horizons."""
    n = len(vals)
    if n < 3:
        return None
    m = stats.mean(vals)
    sd = stats.pstdev(vals)
    if not sd:
        return None
    return m / (sd / math.sqrt(n) * math.sqrt(h))


def cond_stats(pairs, h):
    """pairs: list of returns. Returns summary dict."""
    if not pairs:
        return {"n": 0}
    return {"n": len(pairs),
            "mean": stats.mean(pairs), "median": stats.median(pairs),
            "hit": 100.0 * sum(1 for v in pairs if v > 0) / len(pairs),
            "t": _tstat(pairs, h)}


def state_conditioned(wf_rows, fwd_by_code, horizons):
    """Primary test: forward returns conditional on state, per contract and
    pooled, plus a signed-pooled row (long-states long, short-states short)."""
    states = ["STRONG_LONG", "LEAN_LONG", "NEUTRAL", "LEAN_SHORT", "STRONG_SHORT"]
    per, pooled, signed = {}, {}, {}
    for h in horizons:
        pooled[h] = {s: [] for s in states}
        signed[h] = []
    for r in wf_rows:
        fr = fwd_by_code[r["cftc_code"]].get(r["release_date"], {})
        for h in horizons:
            v = fr.get(h)
            if v is None:
                continue
            per.setdefault(r["root"], {}).setdefault(h, {s: [] for s in states})
            per[r["root"]][h][r["state"]].append(v)
            pooled[h][r["state"]].append(v)
            if r["state"] != "NEUTRAL":
                signed[h].append(v if r["state"].endswith("LONG") else -v)
    result = {"pooled": {}, "per_contract": {}, "signed": {}}
    for h in horizons:
        result["pooled"][h] = {s: cond_stats(pooled[h][s], h) for s in states}
        result["signed"][h] = cond_stats(signed[h], h)
    for root, hs in per.items():
        result["per_contract"][root] = {
            h: {s: cond_stats(vals, h) for s, vals in hmap.items()}
            for h, hmap in hs.items()}
    return result


def transition_events(wf_rows, fwd_by_code, horizons):
    """Secondary: event study on state transitions, grouped by destination
    state, vs the unconditional baseline."""
    by_contract = {}
    for r in wf_rows:
        by_contract.setdefault(r["cftc_code"], []).append(r)
    events = {}
    baseline = {h: [] for h in horizons}
    for code, rows in by_contract.items():
        rows.sort(key=lambda r: r["release_date"])
        for prev, cur in zip(rows, rows[1:]):
            fr = fwd_by_code[code].get(cur["release_date"], {})
            for h in horizons:
                v = fr.get(h)
                if v is None:
                    continue
                baseline[h].append(v)
                if prev["state"] != cur["state"] and cur["state"] != "NEUTRAL":
                    events.setdefault(cur["state"], {h2: [] for h2 in horizons})
                    events[cur["state"]][h].append(v)
    return {
        "baseline": {h: cond_stats(baseline[h], h) for h in horizons},
        "events": {st: {h: cond_stats(vals, h) for h, vals in hs.items()}
                   for st, hs in events.items()},
    }


# ---------------------------------------------------------------- strategies

def _weekly_grid(wf_rows):
    grid = {}
    for r in wf_rows:
        grid.setdefault(r["release_date"], {})[r["cftc_code"]] = r
    return grid


def _pos_for_state(state):
    if state.endswith("LONG"):
        return 1.0
    if state.endswith("SHORT"):
        return -1.0
    return 0.0


def state_strategy(wf_rows, fwd_by_code, cost_per_side):
    """Unit-notional state-following: +1 in LONG states, -1 in SHORT states,
    flat NEUTRAL; equal-weight across contracts; 1-week rebalancing on
    release dates. Backtest convention only — the live system never sizes."""
    grid = _weekly_grid(wf_rows)
    dates = sorted(grid)
    codes = sorted({r["cftc_code"] for r in wf_rows})
    prev_pos = {c: 0.0 for c in codes}
    gross, net = [], []
    for rd in dates:
        week = grid[rd]
        pnl, turn = 0.0, 0.0
        for c in codes:
            pos = _pos_for_state(week[c]["state"]) if c in week else 0.0
            r1 = fwd_by_code[c].get(rd, {}).get(1)
            if r1 is not None:
                pnl += pos * r1 / len(codes)
            turn += abs(pos - prev_pos[c]) / len(codes)
            prev_pos[c] = pos
        gross.append(pnl)
        net.append(pnl - turn * cost_per_side)
    return {"dates": dates, "gross": gross, "net": net}


def xsec_spread(wf_rows, fwd_by_code, cost_per_side):
    """Tertiary (context only, low confidence at 5 names): long top-1 short
    bottom-1 by composite each week, 1-week hold."""
    grid = _weekly_grid(wf_rows)
    dates = sorted(grid)
    prev_pos = {}
    gross, net = [], []
    for rd in dates:
        week = grid[rd]
        avail = [(c, r) for c, r in week.items()
                 if fwd_by_code[c].get(rd, {}).get(1) is not None]
        if len(avail) < 4:
            continue
        avail.sort(key=lambda cr: cr[1]["composite"])
        pos = {avail[-1][0]: 0.5, avail[0][0]: -0.5}
        pnl = sum(w * fwd_by_code[c][rd][1] for c, w in pos.items())
        turn = sum(abs(pos.get(c, 0.0) - prev_pos.get(c, 0.0))
                   for c in set(pos) | set(prev_pos))
        gross.append(pnl)
        net.append(pnl - turn * cost_per_side)
        prev_pos = pos
    return {"gross": gross, "net": net, "n_weeks": len(gross)}


# ---------------------------------------------------------------- Sharpe / DSR

def ann_sharpe(weekly):
    m, sd = stats.mean(weekly), stats.pstdev(weekly)
    if not sd:
        return None
    return m / sd * math.sqrt(52)


def _moments(xs):
    n = len(xs)
    m = stats.mean(xs)
    sd = stats.pstdev(xs)
    if not sd:
        return 0.0, 3.0
    skew = sum((x - m) ** 3 for x in xs) / n / sd ** 3
    kurt = sum((x - m) ** 4 for x in xs) / n / sd ** 4
    return skew, kurt


def deflated_sharpe(weekly, trial_sharpes):
    """Bailey & Lopez de Prado DSR. trial_sharpes: the (annualized) Sharpe of
    every configuration tried, used for the expected-max benchmark SR*."""
    sd_w = stats.pstdev(weekly)
    if not sd_w or len(weekly) < 10:
        return None
    sr_w = stats.mean(weekly) / sd_w                      # per-period SR
    t = len(weekly)
    skew, kurt = _moments(weekly)
    n_trials = max(2, len(trial_sharpes))
    sr_trials_w = [s / math.sqrt(52) for s in trial_sharpes if s is not None]
    var_trials = (stats.pstdev(sr_trials_w) ** 2) if len(sr_trials_w) >= 2 else 0.0
    sr_star = math.sqrt(var_trials) * (
        (1 - EULER_GAMMA) * _ND.inv_cdf(1 - 1.0 / n_trials)
        + EULER_GAMMA * _ND.inv_cdf(1 - 1.0 / (n_trials * math.e)))
    denom = math.sqrt(max(1e-12, 1 - skew * sr_w + (kurt - 1) / 4.0 * sr_w ** 2))
    z = (sr_w - sr_star) * math.sqrt(t - 1) / denom
    return {"dsr": _ND.cdf(z), "sr_star_ann": sr_star * math.sqrt(52),
            "skew": skew, "kurt": kurt, "n_weeks": t, "n_trials": n_trials}
