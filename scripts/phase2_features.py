#!/usr/bin/env python3
"""Phase 2 — compute §4 features over full history and produce the MEASUREMENT
REPORT with PROPOSED cut points. No scores are computed; no thresholds are
frozen. Runs under the heartbeat wrapper."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import db, features, heartbeat, measurement
from cotcm.config import load_config

FMT = lambda v: "—" if v is None else ("%.4g" % v)


def _contracts(conn):
    return conn.execute(
        "SELECT cftc_code, root, label FROM contract_map "
        "WHERE approved=1 AND enabled=1 ORDER BY root").fetchall()


def render(conn):
    contracts = _contracts(conn)
    series = {code: measurement.load_feature_series(conn, code)
              for code, _, _ in contracts}

    L = ["# Phase 2 Measurement Report — Features & Proposed Cuts", ""]
    L.append("MEASURE FIRST, THRESHOLD SECOND. This report computes the §4 "
             "features over full history and distributions per feature per "
             "contract. The cut points in section 7 are **proposals** for "
             "operator approval — no score is computed and no threshold is "
             "frozen until the Phase 2 gate is passed.")
    L.append("")
    L.append("Window/burn-in: hp_index 52wk SMA · COT index 156wk (3y) and "
             "inception-to-date (full), both from obs 156 · z-delta vs trailing "
             "156 WoW deltas · oi_flag 26wk median · conc_pctile causal "
             "expanding, 52wk burn-in. No partial-window values.")
    L.append("")

    # Section 1-N: per-feature distribution tables
    L.append("## 1. Feature distributions (per contract)")
    for feat in measurement.NUMERIC_FEATURES:
        L.append("")
        L.append("### %s" % feat)
        L.append("")
        L.append("| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for code, root, _ in contracts:
            d = measurement.distribution(series[code], feat)
            if not d.get("n"):
                L.append("| %s | 0 | — | — | — | — | — | — | — | — | — | — | — |" % root)
                continue
            L.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                     % (root, d["n"], FMT(d["p0"]), FMT(d["p5"]), FMT(d["p10"]),
                        FMT(d["p25"]), FMT(d["p50"]), FMT(d["p75"]), FMT(d["p90"]),
                        FMT(d["p95"]), FMT(d["p100"]), FMT(d["mean"]), FMT(d["std"])))

    # Section 2: COT-index dated extremes (spec's sanity-check requirement)
    L.append("")
    L.append("## 2. Commercial COT-index extremes (dated, full-history lookback)")
    L.append("")
    L.append("Episodes where `cot_idx_comm_full` > 95 (commercials at a "
             "record net-long extreme → contrarian-bullish) or < 5 (record "
             "net-short → contrarian-bearish). Consecutive weeks grouped.")
    for code, root, _ in contracts:
        s = measurement.extreme_episodes_summary(series[code], "cot_idx_comm_full")
        L.append("")
        L.append("- **%s** — high (>95): %s" % (root,
                 ", ".join("%s (%dw, peak %.0f)" % (e["span"], e["weeks"], e["peak"])
                           for e in s["high"]) or "none"))
        L.append("  - low (<5): %s"
                 % (", ".join("%s (%dw, trough %.0f)" % (e["span"], e["weeks"], e["trough"])
                              for e in s["low"]) or "none"))

    # Section 3: MM COT-index extremes
    L.append("")
    L.append("## 3. Managed-Money COT-index extremes (dated)")
    L.append("")
    L.append("Episodes where `cot_idx_mm_full` > 95 (MM crowded long) or < 5 "
             "(MM crowded short).")
    for code, root, _ in contracts:
        s = measurement.extreme_episodes_summary(series[code], "cot_idx_mm_full")
        L.append("")
        L.append("- **%s** — high (>95): %s" % (root,
                 ", ".join("%s (%dw, peak %.0f)" % (e["span"], e["weeks"], e["peak"])
                           for e in s["high"]) or "none"))
        L.append("  - low (<5): %s"
                 % (", ".join("%s (%dw, trough %.0f)" % (e["span"], e["weeks"], e["trough"])
                              for e in s["low"]) or "none"))

    # Section 4: z-delta tail behaviour
    L.append("")
    L.append("## 4. WoW z-delta tail frequency (% of weeks beyond |z|)")
    L.append("")
    L.append("| Root | z_delta_mm n | >1σ | >2σ | >3σ | z_delta_comm n | >1σ | >2σ | >3σ |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for code, root, _ in contracts:
        m = measurement.zdelta_tail_counts(series[code], "z_delta_mm")
        c = measurement.zdelta_tail_counts(series[code], "z_delta_comm")
        L.append("| %s | %d | %s | %s | %s | %d | %s | %s | %s |"
                 % (root, m["n"], m["abs_gt_1"], m["abs_gt_2"], m["abs_gt_3"],
                    c["n"], c["abs_gt_1"], c["abs_gt_2"], c["abs_gt_3"]))

    # Section 5: OI-flag frequencies
    L.append("")
    L.append("## 5. OI-confirmation flag frequency")
    L.append("")
    L.append("| Root | new_longs | new_shorts | long_liquidation | short_covering | mixed |")
    L.append("|---|---|---|---|---|---|")
    order = ["new_longs", "new_shorts", "long_liquidation", "short_covering", "mixed"]
    for code, root, _ in contracts:
        fr = measurement.oi_flag_freq(series[code])
        L.append("| %s | %s |" % (root, " | ".join(
            "%s%%" % fr.get(k, {}).get("pct", 0) for k in order)))

    # Section 6: concentration extremes
    L.append("")
    L.append("## 6. Concentration percentile — crowding context (never directional)")
    L.append("")
    L.append("conc_pctile is the causal percentile of the more-crowded net-4-trader "
             "leg vs the contract's own history. Weeks at the 100th percentile "
             "(a fresh concentration record) per contract:")
    for code, root, _ in contracts:
        recs = [r["release_date"] for r in series[code]
                if r["conc_pctile"] is not None and r["conc_pctile"] >= 99.5]
        L.append("- **%s**: %d record-concentration weeks; most recent %s"
                 % (root, len(recs), recs[-1] if recs else "—"))

    # Section 7: PROPOSED cut points
    L.append("")
    L.append("## 7. ⬅ PROPOSED cut points (for operator approval)")
    L.append("")
    L.append("### 7.1 Component rescaling to [−1, +1]")
    L.append("")
    L.append("**f(hp_index)** — time-series, centered on each contract's own "
             "median (\"extreme *for this market*\"). Proposed anchors: "
             "p10 → −1, p50 → 0, p90 → +1, clipped. Sign preserves structural "
             "meaning (more net-short-than-usual producers → bullish).")
    L.append("")
    L.append("| Root | p10 (→−1) | p50 (→0) | p90 (→+1) |")
    L.append("|---|---|---|---|")
    for code, root, _ in contracts:
        a = measurement.proposed_hp_anchors(series[code])
        L.append("| %s | %s | %s | %s |" % (root, FMT(a["p10"]), FMT(a["p50"]),
                                            FMT(a["p90"])) if a else "| %s | — | — | — |" % root)
    L.append("")
    L.append("**g(cot_idx_comm_3y)** — commercial contrarian. Proposed: 0 inside "
             "the [10, 90] band, ramping to +1 as the index → 100 (commercials "
             "record net-long → bullish) and to −1 as it → 0. Extreme band "
             "endpoints proposed at the measured p10/p90 per contract (see §1); "
             "a round-number fallback of 20/80 is offered for a single global rule.")
    L.append("")
    L.append("**h(cot_idx_mm_3y)** — MM crowding, contrarian *at extremes only*. "
             "Proposed: 0 inside [10, 90]; as MM index → 100 (crowded long) h → "
             "−1; as → 0 (crowded short) h → +1. Note the sign is opposite to g.")
    L.append("")
    L.append("**k(z_delta_mm, oi_flag)** — flow confirmation/divergence. Proposed: "
             "base = clip(z_delta_mm / 2, −1, +1) (±2σ saturates), gated by "
             "oi_flag quality — new_longs/new_shorts → full weight (conviction), "
             "mixed → ×0.5, long_liquidation/short_covering → ×0.5 (position "
             "unwind, not fresh conviction). §4 tail freqs and §5 flag mix "
             "support the 2σ and gating choices.")
    L.append("")
    L.append("### 7.2 State classification")
    L.append("")
    L.append("With weights (0.40/0.25/0.20/0.15) summing to 1 and each component "
             "in [−1,+1], the composite is bounded in [−1,+1]. **Proposed rule:** "
             "STRONG at |composite| ≥ 0.50, LEAN at 0.20 ≤ |composite| < 0.50, "
             "NEUTRAL at |composite| < 0.20 (sign gives LONG/SHORT). These "
             "provisional cuts are to be **confirmed against the measured "
             "composite distribution in the Phase 3 dry-run** (outer deciles → "
             "STRONG), per spec §5 — no composite is computed in Phase 2.")
    L.append("")
    L.append("### 7.3 Setup-quality flag thresholds")
    L.append("")
    L.append("- `divergence_aligned`: commercial COT index and MM COT index BOTH "
             "in their contrarian-extreme bands (comm and MM both >90 or both <10) "
             "pointing the same way — proposed band = [10,90] as above.")
    L.append("- `crowding_flag`: conc_pctile ≥ 90 (contract in the top decile of "
             "its own concentration history) — proposed extreme = p90.")
    L.append("")
    L.append("## ⛔ STOP — Phase 2 gate")
    L.append("")
    L.append("Operator approves the rescaling anchors (§7.1), state cuts (§7.2) "
             "and flag thresholds (§7.3). Phase 3 implements §5 with the approved "
             "cuts — not before.")
    return "\n".join(L) + "\n", {"contracts": [c[1] for c in contracts]}


def main():
    cfg = load_config()
    os.makedirs(cfg["reports_dir"], exist_ok=True)
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)

    heartbeat.run_job(conn, "features", lambda: features.compute_all(cfg, conn))

    report, meta = render(conn)
    md = os.path.join(cfg["reports_dir"], "phase2_measurement_report.md")
    with open(md, "w") as f:
        f.write(report)
    print(report)
    print("Written: %s" % md)


if __name__ == "__main__":
    main()
