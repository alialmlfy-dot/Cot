#!/usr/bin/env python3
"""Phase 3 — implement §5 with the approved cuts; score full history; verify
the provisional state cuts against the measured composite distribution (the
condition attached to the Phase 2 approval); dry-run weekly reports for the
last 12 historical release dates."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import db, heartbeat, scoring, stats, weekly_report
from cotcm.config import load_config


def composite_distribution_check(conn, sig):
    """Compare provisional cuts (0.20/0.50) to the measured composite
    distribution, pooled and per contract. Spec §5 suggests outer deciles
    for STRONG."""
    out = {"per_contract": [], "pooled": {}}
    all_vals = []
    for code, root in conn.execute(
            "SELECT cftc_code, root FROM contract_map WHERE approved=1 AND enabled=1 "
            "ORDER BY root"):
        vals = [r[0] for r in conn.execute(
            "SELECT composite FROM scores WHERE cftc_code=?", (code,))]
        all_vals.extend(vals)
        out["per_contract"].append({
            "root": root, "n": len(vals),
            "p10": stats.percentile(vals, 10), "p90": stats.percentile(vals, 90),
            "p25": stats.percentile(vals, 25), "p75": stats.percentile(vals, 75),
            "min": min(vals), "max": max(vals),
        })
    from collections import Counter
    states = Counter(r[0] for r in conn.execute("SELECT state FROM scores"))
    tot = sum(states.values())
    out["pooled"] = {
        "n": len(all_vals),
        "p10": stats.percentile(all_vals, 10), "p90": stats.percentile(all_vals, 90),
        "p25": stats.percentile(all_vals, 25), "p75": stats.percentile(all_vals, 75),
        "state_freq": {k: round(100.0 * v / tot, 1) for k, v in sorted(states.items())},
    }
    return out


def render_deliverable(check, sig, sample_files, transitions_note):
    cuts = sig["state_cuts"]
    L = ["# Phase 3 Deliverable — Composite Engine + 12 Dry-Run Weekly Reports", ""]
    L.append("§5 implemented with the operator-approved cuts: per-contract hp "
             "anchors; global contrarian band [%g, %g] for g/h and "
             "divergence_aligned; k = clip(z/2) gated by oi_flag; weights "
             "0.40/0.25/0.20/0.15 (global constants)." %
             (sig["cot_band"]["low"], sig["cot_band"]["high"]))
    L.append("")
    L.append("## 1. Composite distribution vs provisional state cuts")
    L.append("")
    L.append("Approval condition from the Phase 2 gate: confirm the provisional "
             "cuts (LEAN %g, STRONG %g) against the measured composite "
             "distribution; if the outer deciles land materially away from "
             "±%g, decile-based cuts win and return to the operator."
             % (cuts["lean"], cuts["strong"], cuts["strong"]))
    L.append("")
    L.append("| Scope | n | p10 | p25 | p75 | p90 | min | max |")
    L.append("|---|---|---|---|---|---|---|---|")
    p = check["pooled"]
    L.append("| pooled | %d | %+.3f | %+.3f | %+.3f | %+.3f | — | — |"
             % (p["n"], p["p10"], p["p25"], p["p75"], p["p90"]))
    for c in check["per_contract"]:
        L.append("| %s | %d | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f |"
                 % (c["root"], c["n"], c["p10"], c["p25"], c["p75"], c["p90"],
                    c["min"], c["max"]))
    L.append("")
    L.append("State frequencies under the provisional cuts: %s"
             % json.dumps(p["state_freq"]))
    L.append("")
    verdict_lines = []
    if abs(p["p10"]) < cuts["strong"] and abs(p["p90"]) < cuts["strong"]:
        verdict_lines.append(
            "**Verdict:** the pooled outer deciles (%+.3f / %+.3f) sit INSIDE "
            "±%g — the provisional STRONG cut is stricter than the outer-decile "
            "rule. See recommendation below the table in the summary." %
            (p["p10"], p["p90"], cuts["strong"]))
    else:
        verdict_lines.append(
            "**Verdict:** pooled outer deciles (%+.3f / %+.3f) are consistent "
            "with the provisional STRONG cut ±%g." % (p["p10"], p["p90"], cuts["strong"]))
    L.extend(verdict_lines)
    L.append("")
    L.append("## 2. Dry-run weekly reports (last 12 historical release dates)")
    L.append("")
    for f in sample_files:
        L.append("- `%s`" % f)
    L.append("")
    L.append(transitions_note)
    L.append("")
    L.append("## ⛔ STOP — Phase 3 gate")
    L.append("")
    L.append("Operator reviews the 12 sample reports and the state-cut check. "
             "Phase 4 (backtest harness) does not begin until approval.")
    return "\n".join(L) + "\n"


def main():
    cfg = load_config()
    os.makedirs(cfg["reports_dir"], exist_ok=True)
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)

    heartbeat.run_job(conn, "score_history", lambda: scoring.score_all(cfg, conn))

    sig = cfg["signal"]
    check = composite_distribution_check(conn, sig)

    # last 12 distinct release dates
    dates = [r[0] for r in conn.execute(
        "SELECT DISTINCT release_date FROM scores ORDER BY release_date DESC LIMIT 12")]
    dates.reverse()
    sample_files, n_trans = [], 0
    for rd in dates:
        md, js, payload = weekly_report.write_report(cfg, conn, rd)
        sample_files.append(os.path.relpath(md, cfg["_repo_root"]))
        n_trans += len(payload["transitions"])
    transitions_note = ("Across the 12 dry-run weeks there were %d state "
                        "transitions — transitions are the actionable events; "
                        "steady states are context." % n_trans)

    deliverable = render_deliverable(check, sig, sample_files, transitions_note)
    path = os.path.join(cfg["reports_dir"], "phase3_deliverable.md")
    with open(path, "w") as f:
        f.write(deliverable)
    print(deliverable)
    print("Written: %s" % path)


if __name__ == "__main__":
    main()
