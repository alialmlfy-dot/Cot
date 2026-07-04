#!/usr/bin/env python3
"""Phase 0 — Discovery & plumbing.

Runs live Socrata verification (dataset ID, columns, contract codes
name-matched, stored approved=0), tests the price source for every enabled
symbol, initializes the DB, and writes the verification report the operator
must approve before Phase 1 begins.
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cotcm import db, discovery, heartbeat, prices
from cotcm.config import load_config


def run(cfg, conn):
    result = {
        "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "domain_errors": [],
    }

    # 0.1 domain + dataset
    domain, domain_errors = discovery.find_working_domain(cfg)
    result["domain"] = domain
    result["domain_errors"] = domain_errors
    dataset = discovery.find_dataset(cfg, domain)
    result["dataset"] = dataset

    # 0.2 columns
    fields, all_fields = discovery.resolve_fields(cfg, domain, dataset["id"])
    result["field_map"] = fields
    result["live_field_count"] = len(all_fields)

    # 0.3 contract name-matching (all universe entries incl. disabled PA,
    # so the operator sees the optional contract too)
    result["contracts"] = []
    for uni in cfg["universe"]:
        cands = discovery.find_contract_candidates(cfg, domain, dataset["id"], fields, uni)
        entry = {"root": uni["root"], "label": uni["label"],
                 "enabled": bool(uni.get("enabled")), "candidates": cands}
        if cands:
            discovery.upsert_contract_map(conn, uni, cands[0])
            entry["selected"] = cands[0]["cftc_code"]
        else:
            entry["selected"] = None
        result["contracts"].append(entry)

    unmatched = [c["root"] for c in result["contracts"]
                 if c["enabled"] and not c["selected"]]
    if unmatched:
        raise discovery.DiscoveryError(
            "No live contract match for enabled roots: %s — halting, not guessing."
            % unmatched)

    # 0.4 price source test — every configured source x every contract
    result["prices"] = [prices.test_source(cfg, src, u)
                        for src in cfg["prices"]["sources"]
                        for u in cfg["universe"]]

    n_price_ok = sum(1 for p in result["prices"] if p["ok"])
    return result, {
        "message": "phase0 verify: dataset=%s, %d/%d contracts matched, %d/%d price tests ok"
                   % (dataset["id"],
                      sum(1 for c in result["contracts"] if c["selected"]),
                      len(result["contracts"]),
                      n_price_ok, len(result["prices"])),
        "rows_written": sum(1 for c in result["contracts"] if c["selected"]),
    }


def render_report(cfg, result):
    L = []
    L.append("# Phase 0 Verification Report — COT Crude + Metals v1.1")
    L.append("")
    L.append("Generated: %s" % result["run_at"])
    L.append("")
    L.append("## 1. Socrata source")
    L.append("")
    L.append("- **Domain used:** `%s`" % result["domain"])
    for e in result["domain_errors"]:
        L.append("- Domain fallback note: `%s`" % e)
    L.append("- **Dataset resolved by live name-match (not hardcoded):** `%s` — \"%s\" "
             "(data updated %s)"
             % (result["dataset"]["id"], result["dataset"]["name"],
                result["dataset"].get("data_updated_at", "?")))
    for rc in result["dataset"].get("rejected_candidates", []):
        L.append("- Rejected same-name candidate: `%s` (row access: %s, data updated %s)"
                 % (rc["id"], rc["row_access"], rc.get("data_updated_at")))
    L.append("- Live column count: %d; all %d required field concepts resolved."
             % (result["live_field_count"], len(result["field_map"])))
    L.append("")
    L.append("## 2. Resolved field map (concept → live API field)")
    L.append("")
    L.append("| Concept | Live field |")
    L.append("|---|---|")
    for k, v in result["field_map"].items():
        L.append("| %s | `%s` |" % (k, v))
    L.append("")
    L.append("## 3. Contract map (stored with `approved=0` — awaiting operator approval)")
    L.append("")
    L.append("| Root | Label | Enabled | Selected code | Market name (live) | History | Weeks | Other candidates |")
    L.append("|---|---|---|---|---|---|---|---|")
    for c in result["contracts"]:
        sel = next((x for x in c["candidates"] if x["cftc_code"] == c["selected"]), None)
        others = ", ".join("`%s` (%s)" % (x["cftc_code"], x["market_name"])
                           for x in c["candidates"][1:4]) or "—"
        if sel:
            L.append("| %s | %s | %s | `%s` | %s | %s → %s | %d | %s |"
                     % (c["root"], c["label"], "yes" if c["enabled"] else "no",
                        sel["cftc_code"], sel["market_name"],
                        sel["first_report_date"], sel["last_report_date"],
                        sel["n_weeks"], others))
        else:
            L.append("| %s | %s | %s | **NO MATCH** | — | — | — | — |"
                     % (c["root"], c["label"], "yes" if c["enabled"] else "no"))
    L.append("")
    L.append("Selection rule: candidates merged by contract code across historical "
             "renames, ranked by most-recent report date then history length. "
             "The operator approves or overrides each code before Phase 1.")
    L.append("")
    L.append("## 4. Price source test (weekly closes, all configured sources)")
    L.append("")
    L.append("| Source | Root | Symbol | OK | Rows | First | Last | Last close | Error |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in result["prices"]:
        err = (p["error"] or "—").replace("|", "\\|")
        if len(err) > 90:
            err = err[:90] + "…"
        L.append("| %s | %s | `%s` | %s | %d | %s | %s | %s | %s |"
                 % (p["source"], p["root"], p["symbol"],
                    "yes" if p["ok"] else "NO", p["rows"],
                    p["first_date"] or "—", p["last_date"] or "—",
                    p["last_close"] if p["last_close"] is not None else "—",
                    err))
    L.append("")
    L.append("Note: Yahoo weekly bars are labeled by week-start (Monday); the "
             "bar close is the week's final trade (Friday close for full weeks). "
             "Friday-date mapping is implemented in Phase 1 for whichever source "
             "is approved.")
    L.append("")
    L.append("## 5. Plumbing checks")
    L.append("")
    L.append("- SQLite schema initialized (contract_map, cot_raw, prices_weekly, "
             "features, scores, heartbeat) — idempotent, WAL mode.")
    L.append("- This run itself executed under the heartbeat wrapper; see the "
             "`heartbeat` table for the row.")
    L.append("")
    L.append("## 6. ⛔ STOP — Phase 0 gate")
    L.append("")
    L.append("Operator must approve: (a) the contract map above (then set "
             "`approved=1`), (b) the price source choice. Phase 1 (backfill + "
             "weekly ingest) does not begin until approval.")
    return "\n".join(L) + "\n"


def main():
    cfg = load_config()
    os.makedirs(cfg["reports_dir"], exist_ok=True)
    conn = db.connect(cfg["db_path"])
    db.init_db(conn)

    holder = {}

    def job():
        result, hb = run(cfg, conn)
        holder["result"] = result
        return hb

    heartbeat.run_job(conn, "phase0_verify", job)
    result = holder["result"]

    report_md = render_report(cfg, result)
    md_path = os.path.join(cfg["reports_dir"], "phase0_verification_report.md")
    json_path = os.path.join(cfg["reports_dir"], "phase0_verification.json")
    with open(md_path, "w") as f:
        f.write(report_md)
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(report_md)
    print("Written: %s\nWritten: %s" % (md_path, json_path))


if __name__ == "__main__":
    main()
