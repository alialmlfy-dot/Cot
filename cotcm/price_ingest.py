"""Weekly price ingest. Yahoo chart API is the operator-approved primary
source; stooq and operator-supplied files remain as configured fallbacks.

Yahoo weekly bars are labeled by week-start; each bar's close is the week's
final trade. We store it against that week's Friday (friday_of_week) so price
weeks align with COT release_date Fridays. Idempotent on (cftc_code,
week_end_date)."""

import csv
import io
from datetime import date, datetime, timezone

from .http_client import get_cfg
from .release_date import friday_of_week


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _headers(cfg):
    ua = cfg["prices"].get("user_agent")
    return {"User-Agent": ua} if ua else {}


def _source_by_name(cfg, name):
    for s in cfg["prices"]["sources"]:
        if s["name"] == name:
            return s
    raise KeyError("price source %r not configured" % name)


def _fetch_yahoo(cfg, source, symbol):
    url = source["endpoint"].format(symbol=symbol)
    resp = get_cfg(cfg, url,
                   params={"interval": source["interval"], "range": source["range"]},
                   headers=_headers(cfg))
    chart = resp.json().get("chart", {})
    if chart.get("error"):
        raise RuntimeError("yahoo error for %s: %s" % (symbol, chart["error"]))
    result = chart["result"][0]
    ts = result.get("timestamp") or []
    closes = result["indicators"]["quote"][0].get("close") or []
    out = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        wk = friday_of_week(date.fromtimestamp(t))
        out.append((wk.isoformat(), float(c)))
    return out


def _fetch_stooq(cfg, source, symbol):
    resp = get_cfg(cfg, source["endpoint"],
                   params={"s": symbol, "i": source["interval"]},
                   headers=_headers(cfg))
    text = resp.text.strip()
    if not text.lower().startswith("date"):
        raise RuntimeError("stooq non-CSV response for %s: %r" % (symbol, text[:80]))
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        if not (r.get("Date") and r.get("Close")):
            continue
        wk = friday_of_week(r["Date"])
        out.append((wk.isoformat(), float(r["Close"])))
    return out


_FETCHERS = {"yahoo_chart": _fetch_yahoo, "stooq_csv": _fetch_stooq}


def _symbol_for(cfg, source, root):
    key = source["symbol_key"]
    for u in cfg["universe"]:
        if u["root"] == root:
            return u.get(key)
    return None


def _approved_universe(conn):
    return conn.execute(
        "SELECT root, cftc_code FROM contract_map WHERE approved=1 AND enabled=1"
    ).fetchall()


def ingest_prices(cfg, conn, order=("yahoo", "stooq")):
    """Fetch weekly closes for every approved+enabled contract, trying sources
    in preference order until one yields data. Latest bar (current partial week)
    is included; it is overwritten on the next run via de-dup on week_end_date.
    Returns per-contract results and never leaves a partial row set for a
    contract — each contract's rows are written in one executemany."""
    results = []
    total_written = 0
    ts = _utcnow()
    for root, code in _approved_universe(conn):
        entry = {"root": root, "cftc_code": code, "source": None,
                 "rows": 0, "written": 0, "first": None, "last": None, "error": None}
        last_err = None
        for name in order:
            source = _source_by_name(cfg, name)
            symbol = _symbol_for(cfg, source, root)
            if not symbol:
                continue
            try:
                bars = _FETCHERS[source["kind"]](cfg, source, symbol)
                if not bars:
                    last_err = "%s: 0 bars" % name
                    continue
                before = conn.total_changes
                # Upsert, not INSERT OR IGNORE: the newest bar is the current
                # partial week — its close must be refreshed by later runs
                # (the Saturday run replaces it with the true Friday close).
                # Still idempotent: one row per (cftc_code, week_end_date).
                conn.executemany(
                    "INSERT INTO prices_weekly "
                    "(cftc_code, week_end_date, close, source, ingested_at) "
                    "VALUES (?, ?, ?, ?, ?) "
                    "ON CONFLICT(cftc_code, week_end_date) DO UPDATE SET "
                    "close=excluded.close, source=excluded.source, "
                    "ingested_at=excluded.ingested_at",
                    [(code, d, c, name, ts) for d, c in bars])
                conn.commit()
                w = conn.total_changes - before
                entry.update(source=name, rows=len(bars), written=w,
                             first=bars[0][0], last=bars[-1][0])
                total_written += w
                break
            except Exception as e:
                last_err = "%s: %s" % (name, e)
                continue
        else:
            entry["error"] = last_err
        if entry["source"] is None:
            entry["error"] = last_err or "no source produced data"
        results.append(entry)
    latest = max((r["last"] for r in results if r["last"]), default=None)
    return {"per_contract": results, "rows_written": total_written,
            "latest_week": latest,
            "message": "prices: %d rows written across %d contracts"
                       % (total_written, len(results))}
