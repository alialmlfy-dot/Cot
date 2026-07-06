"""CFTC Disaggregated Futures-Only ingest — backfill (2006->present) and
incremental (latest report date only).

Backfill strategy (documented per spec section 2): paginated Socrata pulls
filtered to the approved contract codes, ordered by report_date. The universe
is only ~6 contracts x ~1,040 weeks (~6k rows), so a handful of 50k-row pages
covers full history — annual CFTC archive files are unnecessary and would add
a second parser to maintain.

Release-lag discipline (operating rule 3): every row stores both report_date
and the computed release_date. Idempotent writes via INSERT OR IGNORE on the
(cftc_code, report_date) natural key (operating rule 4).
"""

from datetime import datetime, timezone

from . import discovery, integrity
from .http_client import get_cfg
from .release_date import parse_date, release_date_for

# concept -> cot_raw column. report_date/cftc_code/market_name handled separately.
_VALUE_CONCEPTS = [
    "open_interest", "prod_merc_long", "prod_merc_short",
    "swap_long", "swap_short", "swap_spread",
    "mm_long", "mm_short", "mm_spread",
    "other_rept_long", "other_rept_short", "other_rept_spread",
    "nonrept_long", "nonrept_short",
    "conc_gross_4_long", "conc_gross_4_short", "conc_gross_8_long", "conc_gross_8_short",
    "conc_net_4_long", "conc_net_4_short", "conc_net_8_long", "conc_net_8_short",
    "traders_total",
]

PAGE_SIZE = 50000


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _approved_codes(conn):
    rows = conn.execute(
        "SELECT cftc_code FROM contract_map WHERE approved=1 AND enabled=1"
    ).fetchall()
    if not rows:
        raise RuntimeError(
            "No approved+enabled contracts in contract_map — run Phase 0 and "
            "approve before ingesting.")
    return [r[0] for r in rows]


def _parse_record(rec, fields):
    row = {
        "cftc_code": rec[fields["cftc_code"]],
        "report_date": parse_date(rec[fields["report_date"]]).isoformat(),
    }
    for concept in _VALUE_CONCEPTS:
        row[concept] = _num(rec.get(fields[concept]))
    rd = release_date_for(row["report_date"])
    row["release_date"] = rd.isoformat()
    return row


def _fetch(cfg, domain, dataset_id, fields, codes, where_extra=None, order="ASC"):
    url = "https://%s/resource/%s.json" % (domain, dataset_id)
    f_code, f_date = fields["cftc_code"], fields["report_date"]
    quoted = ",".join("'%s'" % c for c in codes)
    where = "%s in (%s)" % (f_code, quoted)
    if where_extra:
        where += " AND (%s)" % where_extra
    rows, offset = [], 0
    while True:
        params = {
            "$where": where,
            "$order": "%s %s, %s" % (f_date, order, f_code),
            "$limit": PAGE_SIZE,
            "$offset": offset,
        }
        page = get_cfg(cfg, url, params=params).json()
        rows.extend(_parse_record(r, fields) for r in page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


_INSERT = (
    "INSERT OR IGNORE INTO cot_raw (cftc_code, report_date, release_date, "
    "release_date_estimated, open_interest, prod_merc_long, prod_merc_short, "
    "swap_long, swap_short, swap_spread, mm_long, mm_short, mm_spread, "
    "other_rept_long, other_rept_short, other_rept_spread, nonrept_long, "
    "nonrept_short, conc_gross_4_long, conc_gross_4_short, conc_gross_8_long, "
    "conc_gross_8_short, conc_net_4_long, conc_net_4_short, conc_net_8_long, "
    "conc_net_8_short, traders_total, ingested_at) "
    "VALUES (:cftc_code, :report_date, :release_date, 1, :open_interest, "
    ":prod_merc_long, :prod_merc_short, :swap_long, :swap_short, :swap_spread, "
    ":mm_long, :mm_short, :mm_spread, :other_rept_long, :other_rept_short, "
    ":other_rept_spread, :nonrept_long, :nonrept_short, :conc_gross_4_long, "
    ":conc_gross_4_short, :conc_gross_8_long, :conc_gross_8_short, "
    ":conc_net_4_long, :conc_net_4_short, :conc_net_8_long, :conc_net_8_short, "
    ":traders_total, :ingested_at)"
)


def _write(conn, rows):
    ts = _utcnow()
    for r in rows:
        r["ingested_at"] = ts
    before = conn.total_changes
    conn.executemany(_INSERT, rows)
    conn.commit()
    return conn.total_changes - before


def backfill(cfg, conn):
    """Full 2006->present pull for all approved+enabled contracts. Integrity is
    checked on the whole parsed batch before any write (no partial commit)."""
    domain, dataset_id, fields = discovery.resolve_source(cfg)
    codes = _approved_codes(conn)
    rows = _fetch(cfg, domain, dataset_id, fields, codes, order="ASC")
    integrity.assert_ok(rows, min_contracts=min(5, len(codes)),
                        expect_full_universe=True)
    written = _write(conn, rows)
    latest = max((r["report_date"] for r in rows), default=None)
    return {"rows_written": written, "rows_seen": len(rows),
            "latest_report_date": latest,
            "message": "backfill: %d rows seen, %d new, %d contracts, latest %s"
                       % (len(rows), written, len(codes), latest)}


def incremental(cfg, conn):
    """Pull only the most recent report date and any newer than what we hold.
    Integrity requires the full approved universe present in the new snapshot."""
    domain, dataset_id, fields = discovery.resolve_source(cfg)
    codes = _approved_codes(conn)
    row = conn.execute("SELECT max(report_date) FROM cot_raw").fetchone()
    have_latest = row[0] if row else None
    f_date = fields["report_date"]
    where_extra = "%s > '%s'" % (f_date, have_latest) if have_latest else None
    rows = _fetch(cfg, domain, dataset_id, fields, codes,
                  where_extra=where_extra, order="ASC")
    if not rows:
        return {"rows_written": 0, "rows_seen": 0,
                "latest_report_date": have_latest,
                "message": "incremental: no new report date (latest still %s)"
                           % have_latest}
    # New snapshot must carry the full approved universe for each new date.
    for rd in sorted({r["report_date"] for r in rows}):
        batch = [r for r in rows if r["report_date"] == rd]
        integrity.assert_ok(batch, min_contracts=len(codes),
                            expect_full_universe=True)
    written = _write(conn, rows)
    latest = max(r["report_date"] for r in rows)
    return {"rows_written": written, "rows_seen": len(rows),
            "latest_report_date": latest,
            "message": "incremental: %d new rows through report_date %s"
                       % (written, latest)}
