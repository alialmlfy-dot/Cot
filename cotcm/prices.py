"""Price source test (Phase 0.3). Weekly closes, front-month continuous.

Two free candidate sources are tested — the operator picks one at the Phase 0
gate (fallback = operator-supplied files). We do not fabricate a source:
every result below comes from a live request.

- stooq CSV endpoint (spec's example source). NOTE: as of Phase 0 stooq
  serves a JavaScript proof-of-work challenge to non-browser clients from
  this network; the test records exactly what came back.
- Yahoo Finance chart API, interval=1wk. Weekly bars are labeled by week
  START (Monday); the bar's close is the last trade of that week (Friday
  close for a full week) — mapping to Friday dates is a Phase 1 concern.
"""

import csv
import io
from datetime import date

from . import http_client


def _headers(cfg):
    ua = cfg["prices"].get("user_agent")
    return {"User-Agent": ua} if ua else {}


def _test_stooq(cfg, source, symbol, out):
    resp = http_client.get_cfg(
        cfg, source["endpoint"],
        params={"s": symbol, "i": source["interval"]},
        headers=_headers(cfg))
    text = resp.text.strip()
    if resp.status_code != 200 or not text.lower().startswith("date"):
        out["error"] = "HTTP %d / body starts: %r" % (resp.status_code, text[:80])
        return
    reader = csv.DictReader(io.StringIO(text))
    rows = [r for r in reader if r.get("Date") and r.get("Close")]
    if not rows:
        out["error"] = "CSV parsed but zero data rows"
        return
    out.update(ok=True, rows=len(rows), first_date=rows[0]["Date"],
               last_date=rows[-1]["Date"], last_close=float(rows[-1]["Close"]))


def _test_yahoo(cfg, source, symbol, out):
    url = source["endpoint"].format(symbol=symbol)
    resp = http_client.get_cfg(
        cfg, url,
        params={"interval": source["interval"], "range": source["range"]},
        headers=_headers(cfg))
    if resp.status_code != 200:
        out["error"] = "HTTP %d: %s" % (resp.status_code, resp.text[:80])
        return
    chart = resp.json().get("chart", {})
    if chart.get("error"):
        out["error"] = str(chart["error"])
        return
    result = chart["result"][0]
    ts = result.get("timestamp") or []
    closes = result["indicators"]["quote"][0].get("close") or []
    pairs = [(t, c) for t, c in zip(ts, closes) if c is not None]
    if not pairs:
        out["error"] = "no non-null close bars"
        return
    out.update(
        ok=True, rows=len(pairs),
        first_date=date.fromtimestamp(pairs[0][0]).isoformat(),
        last_date=date.fromtimestamp(pairs[-1][0]).isoformat(),
        last_close=round(pairs[-1][1], 4),
        granularity=result["meta"].get("dataGranularity"),
    )


_TESTERS = {"stooq_csv": _test_stooq, "yahoo_chart": _test_yahoo}


def test_source(cfg, source, uni_entry):
    """Test one (source, contract) pair. Never raises — failures are data
    for the verification report, not crashes."""
    symbol = uni_entry.get(source["symbol_key"])
    out = {"source": source["name"], "root": uni_entry["root"], "symbol": symbol,
           "ok": False, "rows": 0, "first_date": None, "last_date": None,
           "last_close": None, "error": None}
    if not symbol:
        out["error"] = "no %s configured" % source["symbol_key"]
        return out
    try:
        _TESTERS[source["kind"]](cfg, source, symbol, out)
    except Exception as e:
        out["error"] = str(e)
    return out
