#!/usr/bin/env python3
"""Phase 4 — backtest harness (spec §6). Per-feature IC report FIRST, then
state-conditioned results, transition event study, tertiary cross-sectional
spread, and DSR-adjusted Sharpes. Walk-forward causal scoring throughout."""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import backtest, db, heartbeat, scoring
from cotcm.config import load_config

F = lambda v, d=3: "—" if v is None else ("%.*f" % (d, v))
STATES = ["STRONG_LONG", "LEAN_LONG", "NEUTRAL", "LEAN_SHORT", "STRONG_SHORT"]


def main():
    cfg = load_config()
    bt = cfg["backtest"]
    horizons = bt["horizons_weeks"]
    cost = bt["cost_bps_per_side"] / 10000.0
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)

    contracts = conn.execute(
        "SELECT cftc_code, root FROM contract_map WHERE approved=1 AND enabled=1 "
        "ORDER BY root").fetchall()

    def run():
        out = {}
        fwd = {code: backtest.forward_returns(conn, code, horizons)
               for code, _ in contracts}
        out["fwd_counts"] = {root: len(fwd[code]) for code, root in contracts}

        # 1. IC (FIRST)
        out["ic"] = {root: backtest.ic_table(conn, code, fwd[code], horizons)
                     for code, root in contracts}

        # 2. walk-forward scores (approved cuts)
        wf = backtest.walk_forward_scores(conn, cfg)
        out["wf_n"] = len(wf)
        out["wf_span"] = (min(r["release_date"] for r in wf),
                          max(r["release_date"] for r in wf))

        # 3. primary + secondary + tertiary
        out["cond"] = backtest.state_conditioned(wf, fwd, horizons)
        out["trans"] = backtest.transition_events(wf, fwd, horizons)
        out["xsec"] = backtest.xsec_spread(wf, fwd, cost)

        # 4. strategy + DSR; trial #1 re-classifies with the provisional 0.50 cut
        strat = backtest.state_strategy(wf, fwd, cost)
        wf_050 = [dict(r, state=scoring.classify(
            r["composite"], {"strong": 0.50, "lean": 0.20})) for r in wf]
        strat_050 = backtest.state_strategy(wf_050, fwd, cost)
        sh = {
            "gross": backtest.ann_sharpe(strat["gross"]),
            "net": backtest.ann_sharpe(strat["net"]),
            "gross_050": backtest.ann_sharpe(strat_050["gross"]),
            "net_050": backtest.ann_sharpe(strat_050["net"]),
        }
        trials = [sh["net"], sh["net_050"]]
        sh["dsr_net"] = backtest.deflated_sharpe(strat["net"], trials)
        out["strategy"] = sh
        out["xsec_sharpe"] = {
            "gross": backtest.ann_sharpe(out["xsec"]["gross"]),
            "net": backtest.ann_sharpe(out["xsec"]["net"]),
            "dsr_net": backtest.deflated_sharpe(out["xsec"]["net"], trials),
        }
        return out, {"message": "phase4 backtest: wf %d rows, strat net SR %.2f"
                                % (out["wf_n"], sh["net"] or float("nan"))}

    holder = {}

    def job():
        res, hb = run()
        holder["res"] = res
        return hb

    heartbeat.run_job(conn, "phase4_backtest", job)
    res = holder["res"]

    # ---------------- render
    L = ["# Phase 4 Deliverable — Backtest Harness Results", ""]
    L.append("Walk-forward throughout: hp anchors re-derived causally per test "
             "year (expanding window, burn-in 2006–2014, 1-year steps); no "
             "fitting inside test windows. Costs %g bps/side. Configurations "
             "tried: %d (0.50 provisional cut, 0.35 approved) — used as the DSR "
             "trial count." % (cfg["backtest"]["cost_bps_per_side"],
                               cfg["backtest"]["trials_count"]))
    L.append("")
    L.append("## 1. Per-feature IC report (delivered before any composite result)")
    L.append("")
    L.append("Spearman rank IC of each RAW feature vs forward returns. Expected "
             "signs: hp_index + (risk premium), cot_idx_comm + (contrarian "
             "commercial), cot_idx_mm − at extremes (crowding), z_delta_mm + "
             "(flow momentum), conc_pctile ~0 (context only, never directional).")
    for h in cfg["backtest"]["horizons_weeks"]:
        L.append("")
        L.append("### Horizon %dw (rho, |t|>2 flagged)" % h)
        L.append("")
        L.append("| Feature | " + " | ".join(r for _, r in contracts) + " | avg |")
        L.append("|---|" + "---|" * (len(contracts) + 1))
        for feat in backtest.FEATURES_FOR_IC:
            cells, vals = [], []
            for _, root in contracts:
                e = res["ic"][root][feat][h]
                rho, t = e["rho"], e["t"]
                if rho is None:
                    cells.append("—")
                else:
                    vals.append(rho)
                    mark = "**" if (t is not None and abs(t) > 2) else ""
                    cells.append("%s%+.3f%s" % (mark, rho, mark))
            avg = sum(vals) / len(vals) if vals else None
            L.append("| %s | %s | %s |" % (feat, " | ".join(cells), F(avg)))
    L.append("")
    L.append("## 2. Primary — state-conditioned forward returns (walk-forward)")
    L.append("")
    L.append("Walk-forward sample: %d contract-weeks, %s → %s."
             % (res["wf_n"], res["wf_span"][0], res["wf_span"][1]))
    for h in horizons:
        L.append("")
        L.append("### %dw forward returns by state (pooled)" % h)
        L.append("")
        L.append("| State | n | mean | median | hit% | t (overlap-adj) |")
        L.append("|---|---|---|---|---|---|")
        for s in STATES:
            d = res["cond"]["pooled"][h][s]
            if not d["n"]:
                L.append("| %s | 0 | — | — | — | — |" % s)
            else:
                L.append("| %s | %d | %s%% | %s%% | %.1f | %s |"
                         % (s, d["n"], F(d["mean"] * 100), F(d["median"] * 100),
                            d["hit"], F(d["t"], 2)))
        sg = res["cond"]["signed"][h]
        L.append("| **signed (dir. states)** | %d | %s%% | %s%% | %.1f | %s |"
                 % (sg["n"], F(sg["mean"] * 100), F(sg["median"] * 100),
                    sg["hit"], F(sg["t"], 2)))
    L.append("")
    L.append("### Per-contract signed 4w mean (directional states only)")
    L.append("")
    L.append("| Root | STRONG_LONG mean/n | STRONG_SHORT mean/n | LEAN_LONG mean/n | LEAN_SHORT mean/n |")
    L.append("|---|---|---|---|---|")
    for _, root in contracts:
        row = ["| " + root]
        pc = res["cond"]["per_contract"].get(root, {}).get(4, {})
        for s in ["STRONG_LONG", "STRONG_SHORT", "LEAN_LONG", "LEAN_SHORT"]:
            d = pc.get(s, {"n": 0})
            row.append("%s%% / %d" % (F(d.get("mean", 0) * 100) if d["n"] else "—",
                                      d["n"]))
        L.append(" | ".join(row) + " |")
    L.append("")
    L.append("## 3. Secondary — state-transition event study")
    L.append("")
    L.append("Forward returns after a transition INTO a directional state, vs "
             "the unconditional baseline (transitions are the actionable events).")
    for h in horizons:
        base = res["trans"]["baseline"][h]
        L.append("")
        L.append("**%dw** — baseline: n=%d, mean %s%%, hit %.1f%%"
                 % (h, base["n"], F(base["mean"] * 100), base["hit"]))
        L.append("")
        L.append("| → State | n | mean | median | hit% | t |")
        L.append("|---|---|---|---|---|---|")
        for s in ["STRONG_LONG", "LEAN_LONG", "LEAN_SHORT", "STRONG_SHORT"]:
            d = res["trans"]["events"].get(s, {}).get(h, {"n": 0})
            if not d["n"]:
                L.append("| %s | 0 | — | — | — | — |" % s)
            else:
                L.append("| %s | %d | %s%% | %s%% | %.1f | %s |"
                         % (s, d["n"], F(d["mean"] * 100), F(d["median"] * 100),
                            d["hit"], F(d["t"], 2)))
    L.append("")
    L.append("## 4. Strategy Sharpes (state-following convention) + DSR")
    L.append("")
    st = res["strategy"]
    L.append("| Config | ann. Sharpe gross | ann. Sharpe net (5bps/side) |")
    L.append("|---|---|---|")
    L.append("| approved cuts 0.35/0.20 | %s | %s |" % (F(st["gross"], 2), F(st["net"], 2)))
    L.append("| provisional cuts 0.50/0.20 (trial) | %s | %s |" % (F(st["gross_050"], 2), F(st["net_050"], 2)))
    d = st["dsr_net"]
    if d:
        L.append("")
        L.append("Deflated Sharpe (net, approved config): **DSR = %.3f** "
                 "(SR* benchmark %.2f ann., %d trials, skew %.2f, kurt %.2f, "
                 "T=%d weeks). DSR is the probability the true Sharpe exceeds "
                 "the expected-max-of-trials benchmark."
                 % (d["dsr"], d["sr_star_ann"], d["n_trials"], d["skew"],
                    d["kurt"], d["n_weeks"]))
    L.append("")
    L.append("## 5. Tertiary — 5-name cross-sectional spread (LOW CONFIDENCE)")
    L.append("")
    xs = res["xsec_sharpe"]
    L.append("Top-1 vs bottom-1 by composite, 1w hold, %d weeks: gross SR %s, "
             "net SR %s%s. Flagged low-confidence: 5 names is insufficient "
             "breadth for cross-sectional inference (v1.1 design note) — "
             "context only, not a signal."
             % (res["xsec"]["n_weeks"], F(xs["gross"], 2), F(xs["net"], 2),
                (", DSR %.3f" % xs["dsr_net"]["dsr"]) if xs["dsr_net"] else ""))
    L.append("")
    L.append("## 6. Honesty notes (residual lookahead & conventions)")
    L.append("")
    L.append("- hp anchors: fully walk-forward in this backtest (the live "
             "engine's frozen full-sample anchors are NOT used here).")
    L.append("- The 20/80 band and 0.35/0.20 cuts are held fixed across all "
             "windows; 0.35 was chosen from the full-sample composite "
             "distribution — a mild selection effect, mitigated by the 0.50 "
             "trial being counted in the DSR and both configs reported.")
    L.append("- Weights 0.40/0.25/0.20/0.15 are the spec's priors — never "
             "fitted, per-contract or otherwise.")
    L.append("- Multi-week t-stats use a conservative sqrt(h) SE inflation for "
             "overlapping observations.")
    L.append("- ETF-execution proxy costs only (5 bps/side); futures/options "
             "microstructure not modeled — consistent with 'context, not entries'.")
    L.append("")
    L.append("## ⛔ STOP — Phase 4 gate")
    L.append("")
    L.append("Operator decides: (a) go/no-go on live operation; (b) the single "
             "permitted weight-revision round — the §1 IC table identifies any "
             "component with no standalone IC whose weight should be considered "
             "for zeroing. After that, weights freeze.")

    report = "\n".join(L) + "\n"
    md = os.path.join(cfg["reports_dir"], "phase4_backtest_report.md")
    with open(md, "w") as f:
        f.write(report)
    with open(os.path.join(cfg["reports_dir"], "phase4_backtest.json"), "w") as f:
        json.dump(res, f, indent=2, default=str)
    print(report)
    print("Written: %s" % md)


if __name__ == "__main__":
    main()
