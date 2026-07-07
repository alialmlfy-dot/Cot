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
| 0 | Discovery & plumbing: skeleton, config, DB init, live Socrata verification, price source test, heartbeat | ✅ approved (6 contracts, Yahoo prices) |
| 1 | Backfill 2006→present + weekly ingest + systemd + staleness guard | ✅ approved |
| 2 | Features + measurement report + proposed cuts | ✅ approved (global 20/80 band; per-contract hp anchors) |
| 3 | Composite + weekly report (approved cuts only) | ✅ approved (STRONG 0.35 / LEAN 0.20) |
| 4 | Backtest harness (IC report first, DSR-adjusted) | ✅ approved — **LIVE (context-only)** since 2026-07-07 |

## Live operation (Phase 4 go-live decision)

- **Context-only:** the 2015–2026 walk-forward backtest found no directional
  edge in the states (signed t = −2.1, net SR −0.51, DSR 0.04). Every weekly
  report carries a standing caveat; states describe positioning vs the
  contract's own history and must not be read as return forecasts.
- **Weights frozen:** the single permitted revision round was declined —
  revising on the same test set that produced the negative result would be
  curve-fitting. v1.1 weights are final.
- **Saturday pipeline** (`scripts/weekly_ingest.py`): COT ingest → price
  refresh → features → scores → weekly report (md + json in
  `reports/weekly/`). Every step heartbeats; the Sunday staleness guard
  watches for silent death.
- **v1.2 research threads** (pre-registered, untested): PL is the only
  contract with standalone contrarian COT IC; commercial-flow IC is
  consistently positive while MM-flow IC is consistently negative.

## Usage

```bash
pip install -r requirements.txt

# Phase 0 — discovery & plumbing; writes contract_map (approved=0)
python3 scripts/phase0_verify.py
# operator approves the picks:
sqlite3 cot_cm.db "UPDATE contract_map SET approved=1;"

# Phase 1 — one-time backfill + coverage/gap deliverable
python3 scripts/phase1_backfill.py

# Scheduled jobs (installed via systemd/, see systemd/README.md)
python3 scripts/weekly_ingest.py       # incremental COT + prices
python3 scripts/staleness_check.py     # silent-crash guard
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
  release_date.py     # report_date (Tue) -> release_date (Fri) — rule 3
  integrity.py        # per-ingest checks: >=5 contracts, OI>0, legs <= OI
  cftc_ingest.py      # backfill + incremental Socrata pulls
  price_ingest.py     # Yahoo (primary) / stooq weekly close ingest
  coverage.py         # row counts + gap detection for deliverables
  stats.py            # pure-python percentile/mean/stdev helpers (no numpy)
  features.py         # §4 feature computation (keyed to release_date)
  measurement.py      # distributions, dated extremes, proposed-cut helpers
  scoring.py          # §5 composite with approved cuts (config "signal")
  weekly_report.py    # weekly md+json artifact (states, transitions, ETF map)
  backtest.py         # §6 harness: IC, walk-forward, event studies, DSR
scripts/
  phase0_verify.py    # Phase 0 orchestrator → verification report
  phase1_backfill.py  # Phase 1 backfill → coverage/gap deliverable
  phase2_features.py  # Phase 2 features → measurement report + proposed cuts
  phase3_score.py     # Phase 3 scoring → cut check + 12 dry-run weekly reports
  phase4_backtest.py  # Phase 4 backtest → IC-first deliverable + DSR
  weekly_ingest.py    # scheduled incremental job
  staleness_check.py  # scheduled silent-crash guard
systemd/              # timer + service units (Sat ingest, Sun staleness)
reports/              # generated verification/measurement reports
```

## Notes recorded during Phase 0

- The spec names `publicdata.cftc.gov`; `publicreporting.cftc.gov` serves the
  same Socrata catalog. Both are configured; discovery uses the first one that
  answers and records any fallback in the verification report.
- Dataset ID, column names, and contract market codes are **resolved at
  runtime** against the live API and stored for approval — never hardcoded.
