"""Weekly report artifact (spec §5): markdown + JSON per release date, written
to a Drive-synced output folder on the Pi. Per-contract state, component
breakdown, WoW state changes (transitions are the actionable events), ETF
option mapping, and a machine-readable block for the operator's analysis layer.

This system produces context, not entries (operating rule 6)."""

import json
import os

STATE_ORDER = ["STRONG_LONG", "LEAN_LONG", "NEUTRAL", "LEAN_SHORT", "STRONG_SHORT"]


def _contract_meta(conn):
    return {r["cftc_code"]: dict(r) for r in conn.execute(
        "SELECT cftc_code, root, label, sector, etf_mapping, caveat, enabled "
        "FROM contract_map WHERE approved=1 AND enabled=1")}


def load_week(conn, release_date):
    """Scores for one release date plus the previous state per contract."""
    rows = conn.execute(
        "SELECT * FROM scores WHERE release_date=? ORDER BY cftc_code",
        (release_date,)).fetchall()
    out = []
    for r in rows:
        prev = conn.execute(
            "SELECT state, composite FROM scores WHERE cftc_code=? AND "
            "release_date < ? ORDER BY release_date DESC LIMIT 1",
            (r["cftc_code"], release_date)).fetchone()
        out.append({
            "cftc_code": r["cftc_code"],
            "composite": r["composite"],
            "state": r["state"],
            "prev_state": prev["state"] if prev else None,
            "prev_composite": prev["composite"] if prev else None,
            "transition": bool(prev and prev["state"] != r["state"]),
            "crowding_flag": r["crowding_flag"],
            "divergence_aligned": r["divergence_aligned"],
            "components": json.loads(r["components_json"]),
        })
    return out


def build_payload(conn, release_date, caveat=None):
    meta = _contract_meta(conn)
    week = load_week(conn, release_date)
    contracts = []
    for w in week:
        m = meta.get(w["cftc_code"], {})
        contracts.append({
            "root": m.get("root"), "label": m.get("label"),
            "sector": m.get("sector"), "cftc_code": w["cftc_code"],
            "etf_mapping": m.get("etf_mapping"), "caveat": m.get("caveat"),
            "composite": w["composite"], "state": w["state"],
            "prev_state": w["prev_state"], "transition": w["transition"],
            "crowding_flag": w["crowding_flag"],
            "divergence_aligned": w["divergence_aligned"],
            "components": w["components"],
        })
    contracts.sort(key=lambda c: (c["root"] or ""))
    return {
        "release_date": release_date,
        "engine": "cot-cm v1.1 time-series composite",
        "note": "Context, not entries. No sizing, no order routing.",
        "context_only_caveat": caveat,
        "transitions": [c["root"] for c in contracts if c["transition"]],
        "contracts": contracts,
    }


def render_markdown(payload):
    rd = payload["release_date"]
    L = ["# COT Weekly Opportunity Report — release %s" % rd, ""]
    L.append("*Time-series composite vs each contract's own history. Context "
             "for the analysis layer — never sizes or places trades.*")
    L.append("")
    if payload.get("context_only_caveat"):
        L.append("> ⚠ **Standing caveat (Phase 4 go-live condition):** %s"
                 % payload["context_only_caveat"])
        L.append("")
    trans = [c for c in payload["contracts"] if c["transition"]]
    L.append("## State transitions (the actionable events)")
    L.append("")
    if trans:
        for c in trans:
            L.append("- **%s**: %s → **%s** (composite %.3f)"
                     % (c["root"], c["prev_state"] or "—", c["state"], c["composite"]))
    else:
        L.append("- None this week.")
    L.append("")
    L.append("## Per-contract state")
    L.append("")
    L.append("| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for c in payload["contracts"]:
        cp = c["components"]
        L.append("| %s | %s%s | %+.3f | %+.2f | %+.2f | %+.2f | %+.2f | %s | %s | %s |"
                 % (c["root"], c["state"], " *(new)*" if c["transition"] else "",
                    c["composite"], cp["f_hp"], cp["g_comm"], cp["h_mm"], cp["k_flow"],
                    "YES" if c["divergence_aligned"] else "—",
                    "YES" if c["crowding_flag"] else "—",
                    c["etf_mapping"] or "—"))
    L.append("")
    div = [c for c in payload["contracts"] if c["divergence_aligned"]]
    if div:
        L.append("## Divergence-aligned setups (highest-quality class)")
        L.append("")
        for c in div:
            d = "bullish" if c["components"]["g_comm"] > 0 else "bearish"
            L.append("- **%s**: commercial and managed-money COT indices both at "
                     "contrarian extremes, aligned %s." % (c["root"], d))
        L.append("")
    crowd = [c for c in payload["contracts"] if c["crowding_flag"]]
    if crowd:
        L.append("## Crowding warnings (context only, never directional)")
        L.append("")
        for c in crowd:
            L.append("- **%s**: net-4-trader concentration ≥ 90th percentile of "
                     "own history (%.0f)." % (c["root"],
                     c["components"]["inputs"]["conc_pctile"]))
        L.append("")
    for c in payload["contracts"]:
        if c.get("caveat"):
            L.append("> ⚠ **%s caveat:** %s" % (c["root"], c["caveat"]))
            L.append("")
    L.append("## Machine-readable block")
    L.append("")
    L.append("```json")
    L.append(json.dumps(payload, indent=2))
    L.append("```")
    return "\n".join(L) + "\n"


def write_report(cfg, conn, release_date, out_dir=None):
    out_dir = out_dir or os.path.join(cfg["reports_dir"], "weekly")
    os.makedirs(out_dir, exist_ok=True)
    payload = build_payload(conn, release_date,
                            caveat=cfg["signal"].get("context_only_caveat"))
    md_path = os.path.join(out_dir, "cot_weekly_%s.md" % release_date)
    js_path = os.path.join(out_dir, "cot_weekly_%s.json" % release_date)
    with open(md_path, "w") as f:
        f.write(render_markdown(payload))
    with open(js_path, "w") as f:
        json.dump(payload, f, indent=2)
    return md_path, js_path, payload
