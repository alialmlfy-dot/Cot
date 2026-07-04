# COT Crude + Metals Opportunity Finder (v1.1)

Weekly CFTC Disaggregated Futures-Only positioning monitor for WTI crude +
metals (CL, GC, SI, HG, PL; PA optional/disabled). Per-contract **time-series**
scoring against each contract's own measured history. Produces a scored
opportunity report for the operator's analysis layer — it never sizes or
places trades.

- **Host:** Raspberry Pi 4, Python 3.9+ · stdlib + `requests` + `sqlite3`
- **Philosophy:** MEASURE FIRST, THRESHOLD SECOND — no signal threshold is
  hardcoded before its measurement report is produced and approved.
- **Release-lag discipline:** every record carries both `report_date`
  (Tuesday snapshot) and `release_date` (Friday publication); all signal
  logic and backtests key off `release_date`.

## Build phases (approval-gated)

| Phase | Scope | Status |
|---|---|---|
| 0 | Discovery & plumbing: skeleton, config, DB init, live Socrata verification, price source test, heartbeat | ✅ built — **⛔ awaiting operator approval** |
| 1 | Backfill 2006→present + weekly ingest + systemd + staleness guard | not started |
| 2 | Features + measurement report + proposed cuts | not started |
| 3 | Composite + weekly report (approved cuts only) | not started |
| 4 | Backtest harness (IC report first, DSR-adjusted) | not started |

## Phase 0 usage

```bash
pip install -r requirements.txt
python3 scripts/phase0_verify.py
```

Writes `cot_cm.db` (schema + `contract_map` rows with `approved=0`) and
`reports/phase0_verification_report.md`. The operator reviews the contract
map and price-source results, then approves by setting `approved=1`:

```sql
UPDATE contract_map SET approved=1 WHERE cftc_code IN (...);
```

## Layout

```
config.json           # universe, sources, HTTP policy — all config-driven
cotcm/
  config.py           # config loading
  db.py               # SQLite schema (contract_map, cot_raw, prices_weekly,
                      #   features, scores, heartbeat), idempotent init
  http_client.py      # 30s timeout, 3 retries exponential backoff
  heartbeat.py        # heartbeat wrapper — every run writes a row, ok or error
  discovery.py        # live Socrata verification: dataset ID, field map,
                      #   contract name-matching (no invented constants)
  prices.py           # stooq weekly CSV source test
scripts/
  phase0_verify.py    # Phase 0 orchestrator → verification report
reports/              # generated verification/measurement reports
```

## Notes recorded during Phase 0

- The spec names `publicdata.cftc.gov`; `publicreporting.cftc.gov` serves the
  same Socrata catalog. Both are configured; discovery uses the first one that
  answers and records any fallback in the verification report.
- Dataset ID, column names, and contract market codes are **resolved at
  runtime** against the live API and stored for approval — never hardcoded.
