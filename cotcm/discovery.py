"""Phase 0.2 — live Socrata verification.

Operating rule 2 (no invented constants): the dataset ID, column names and
contract market codes are all resolved at runtime against the live API and
recorded for operator approval. If anything fails to resolve, we halt and
report — we do not guess.
"""

import re
from datetime import datetime, timezone

from . import http_client


class DiscoveryError(Exception):
    pass


# Concept -> regex over Socrata fieldName. We resolve the ACTUAL field names
# at runtime and record them; nothing downstream hardcodes a field name.
FIELD_CONCEPTS = {
    "report_date": r"^report_date_as_yyyy_mm_dd$|^report_date",
    "cftc_code": r"^cftc_contract_market_code$",
    "market_name": r"^market_and_exchange_names$",
    "open_interest": r"^open_interest_all$",
    "prod_merc_long": r"^prod_merc_positions_long",
    "prod_merc_short": r"^prod_merc_positions_short",
    "swap_long": r"^swap_+positions_long",
    "swap_short": r"^swap_+positions_short",
    "swap_spread": r"^swap_+positions_spread",
    "mm_long": r"^m_money_positions_long",
    "mm_short": r"^m_money_positions_short",
    "mm_spread": r"^m_money_positions_spread",
    "other_rept_long": r"^other_rept_positions_long",
    "other_rept_short": r"^other_rept_positions_short",
    "other_rept_spread": r"^other_rept_positions_spread",
    "nonrept_long": r"^nonrept_positions_long",
    "nonrept_short": r"^nonrept_positions_short",
    "conc_gross_4_long": r"^conc_gross_le_4_tdr_long",
    "conc_gross_4_short": r"^conc_gross_le_4_tdr_short",
    "conc_gross_8_long": r"^conc_gross_le_8_tdr_long",
    "conc_gross_8_short": r"^conc_gross_le_8_tdr_short",
    "conc_net_4_long": r"^conc_net_le_4_tdr_long",
    "conc_net_4_short": r"^conc_net_le_4_tdr_short",
    "conc_net_8_long": r"^conc_net_le_8_tdr_long",
    "conc_net_8_short": r"^conc_net_le_8_tdr_short",
    "traders_total": r"^traders_tot_all$",
}


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_working_domain(cfg):
    """Return the first configured Socrata domain that answers the catalog API."""
    errors = []
    for domain in cfg["socrata"]["domains"]:
        url = "https://%s/api/views/metadata/v1" % domain
        try:
            resp = http_client.get_cfg(cfg, url, params={"limit": 1})
            if resp.status_code == 200:
                return domain, errors
            errors.append("%s -> HTTP %d" % (domain, resp.status_code))
        except Exception as e:
            errors.append("%s -> %s" % (domain, e))
    raise DiscoveryError("No Socrata domain reachable: %s" % "; ".join(errors))


def find_dataset(cfg, domain):
    """Locate the Disaggregated Futures-Only dataset by name in the live
    catalog. Name-matches can be ambiguous (the CFTC catalog contains a stale
    non-tabular twin of the real dataset), so each candidate is probed for
    actual row access via /resource. Halts unless exactly one queryable
    candidate survives — we do not guess."""
    must = [s.lower() for s in cfg["socrata"]["dataset_name_must_contain"]]
    must_not = [s.lower() for s in cfg["socrata"]["dataset_name_must_not_contain"]]
    url = "https://%s/api/views/metadata/v1" % domain
    candidates, offset = [], 0
    while True:
        resp = http_client.get_cfg(cfg, url, params={"limit": 100, "offset": offset})
        page = resp.json()
        if not page:
            break
        for item in page:
            name = (item.get("name") or "").lower()
            if all(m in name for m in must) and not any(m in name for m in must_not):
                candidates.append({
                    "id": item["id"],
                    "name": item["name"],
                    "data_updated_at": item.get("dataUpdatedAt"),
                })
        offset += len(page)
        if len(page) < 100:
            break
    if not candidates:
        raise DiscoveryError("No Disaggregated Futures-Only dataset found in catalog on %s" % domain)

    queryable = []
    for c in candidates:
        probe = http_client.get_cfg(
            cfg, "https://%s/resource/%s.json" % (domain, c["id"]),
            params={"$limit": 1})
        c["row_access"] = probe.status_code == 200 and isinstance(probe.json(), list)
        if c["row_access"]:
            queryable.append(c)
    if len(queryable) != 1:
        raise DiscoveryError(
            "Expected exactly 1 queryable Disaggregated Futures-Only dataset, "
            "found %d. All candidates: %s" % (len(queryable), candidates))
    chosen = queryable[0]
    chosen["rejected_candidates"] = [c for c in candidates if c is not chosen]
    return chosen


def resolve_fields(cfg, domain, dataset_id):
    """Fetch the dataset's live column list and resolve every concept in
    FIELD_CONCEPTS to an actual fieldName. Missing concepts -> halt."""
    url = "https://%s/api/views/%s.json" % (domain, dataset_id)
    resp = http_client.get_cfg(cfg, url)
    view = resp.json()
    field_names = [c["fieldName"] for c in view.get("columns", [])]
    resolved, missing = {}, []
    for concept, pattern in FIELD_CONCEPTS.items():
        matches = [f for f in field_names if re.match(pattern, f)]
        # Prefer the _all variant and the shortest (avoids _old / pct variants).
        matches.sort(key=lambda f: (0 if f.endswith("_all") else 1, len(f)))
        pct_free = [f for f in matches if "pct" not in f]
        pick = (pct_free or matches)[0] if matches else None
        if pick:
            resolved[concept] = pick
        else:
            missing.append(concept)
    if missing:
        raise DiscoveryError(
            "Could not resolve field concepts against live dataset %s: %s. "
            "Live fields: %s" % (dataset_id, missing, field_names)
        )
    return resolved, field_names


def find_contract_candidates(cfg, domain, dataset_id, fields, uni_entry):
    """Name-match one universe entry against the live dataset. Returns all
    candidates (grouped by contract code) ordered by recency then history
    length; the caller records the top pick with approved=0."""
    url = "https://%s/resource/%s.json" % (domain, dataset_id)
    f_name, f_code, f_date, f_oi = (
        fields["market_name"], fields["cftc_code"],
        fields["report_date"], fields["open_interest"],
    )
    seen = {}
    seen_pairs = set()  # (code, name) — overlapping patterns must not double-count
    for pattern in uni_entry["name_patterns"]:
        params = {
            "$select": "%s, %s, min(%s) AS first_rd, max(%s) AS last_rd, "
                       "count(1) AS n_weeks, max(%s) AS max_oi"
                       % (f_code, f_name, f_date, f_date, f_oi),
            "$where": "upper(%s) like '%%%s%%'" % (f_name, pattern.upper().replace("'", "''")),
            "$group": "%s, %s" % (f_code, f_name),
            "$limit": 100,
        }
        resp = http_client.get_cfg(cfg, url, params=params)
        for row in resp.json():
            code = row[f_code]
            if (code, row[f_name]) in seen_pairs:
                continue
            seen_pairs.add((code, row[f_name]))
            cand = {
                "cftc_code": code,
                "market_name": row[f_name],
                "first_report_date": row["first_rd"][:10],
                "last_report_date": row["last_rd"][:10],
                "n_weeks": int(row["n_weeks"]),
                "matched_pattern": pattern,
            }
            # A contract can appear under several names over time (renames).
            # Merge by code, keep widest date range and total weeks.
            if code in seen:
                prev = seen[code]
                prev["first_report_date"] = min(prev["first_report_date"], cand["first_report_date"])
                prev["last_report_date"] = max(prev["last_report_date"], cand["last_report_date"])
                prev["n_weeks"] += cand["n_weeks"]
                if cand["last_report_date"] >= prev["latest_name_date"]:
                    prev["market_name"] = cand["market_name"]
                    prev["latest_name_date"] = cand["last_report_date"]
            else:
                cand["latest_name_date"] = cand["last_report_date"]
                seen[code] = cand
    candidates = sorted(
        seen.values(),
        key=lambda c: (c["last_report_date"], c["n_weeks"]),
        reverse=True,
    )
    return candidates


def resolve_source(cfg):
    """Re-verify the live source at the start of every ingest run (operating
    rule 2). Returns (domain, dataset_id, fields). Cheap enough for the weekly
    job and robust to CFTC schema drift — nothing about the source is trusted
    from a previous run."""
    domain, _ = find_working_domain(cfg)
    dataset = find_dataset(cfg, domain)
    fields, _ = resolve_fields(cfg, domain, dataset["id"])
    return domain, dataset["id"], fields


def upsert_contract_map(conn, uni_entry, candidate):
    """Store the selected candidate with approved=0 (operator gate)."""
    conn.execute(
        "INSERT INTO contract_map (cftc_code, root, label, sector, market_name_api, "
        "etf_mapping, stooq_symbol, enabled, approved, first_report_date, "
        "last_report_date, n_weeks, matched_at, caveat) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?) "
        "ON CONFLICT(cftc_code) DO UPDATE SET "
        "market_name_api=excluded.market_name_api, "
        "first_report_date=excluded.first_report_date, "
        "last_report_date=excluded.last_report_date, "
        "n_weeks=excluded.n_weeks, matched_at=excluded.matched_at",
        (
            candidate["cftc_code"], uni_entry["root"], uni_entry["label"],
            uni_entry["sector"], candidate["market_name"],
            uni_entry.get("etf_mapping"), uni_entry.get("stooq_symbol"),
            1 if uni_entry.get("enabled") else 0,
            candidate["first_report_date"], candidate["last_report_date"],
            candidate["n_weeks"], _utcnow(), uni_entry.get("caveat"),
        ),
    )
    conn.commit()
