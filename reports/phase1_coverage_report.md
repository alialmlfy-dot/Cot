# Phase 1 Deliverable — Backfill Coverage & Gaps

## COT positioning (cot_raw)

| Root | Code | Enabled | Rows | First | Last | Gaps (>10d) |
|---|---|---|---|---|---|---|
| CL | `067651` | yes | 1046 | 2006-06-13 | 2026-06-23 | 0 |
| GC | `088691` | yes | 1046 | 2006-06-13 | 2026-06-23 | 0 |
| HG | `085692` | yes | 1046 | 2006-06-13 | 2026-06-23 | 0 |
| PA | `075651` | no | 0 | — | — | 0 |
| PL | `076651` | yes | 1046 | 2006-06-13 | 2026-06-23 | 0 |
| SI | `084691` | yes | 1046 | 2006-06-13 | 2026-06-23 | 0 |

### Gap detail (consecutive report_date jumps > 10 days)

- None. Every contract steps at the expected weekly cadence.

## Weekly prices (prices_weekly)

| Root | Code | Rows | First | Last | Source(s) |
|---|---|---|---|---|---|
| CL | `067651` | 1306 | 2001-07-06 | 2026-07-10 | yahoo |
| GC | `088691` | 1306 | 2001-07-06 | 2026-07-10 | yahoo |
| HG | `085692` | 1306 | 2001-07-06 | 2026-07-10 | yahoo |
| PL | `076651` | 1185 | 2001-07-06 | 2026-07-10 | yahoo |
| SI | `084691` | 1306 | 2001-07-06 | 2026-07-10 | yahoo |

## Release-lag discipline (operating rule 3)

- Every row stores both `report_date` (Tuesday snapshot) and `release_date` (Friday publication). All 5,230 rows satisfy the spec rule: `release_date` is the first Friday ≥ 3 days after `report_date` (verified 0 violations), and `release_date_estimated=1` on every row.
- 14 report dates are holiday-shifted off Tuesday (13 Mondays, 1 Wednesday) — e.g. 2006-07-03, 2018-12-24. These are handled by the same rule and flagged estimated; a live CFTC publication calendar can refine them later without touching signal code.

## Ops checks exercised

- **Idempotency:** re-running the weekly ingest wrote 0 new rows (INSERT OR IGNORE on natural keys).
- **Integrity gate:** batches with < 5 contracts, OI ≤ 0, or a category leg exceeding OI are rejected before any write (no partial commit).
- **Heartbeat:** every job (backfill_cot, backfill_prices, weekly_cot, weekly_prices, staleness_check) writes an ok/error row.
- **Staleness guard:** independent Sunday timer; alerts if the latest report_date is > 12 days old.

## ⛔ STOP — Phase 1 gate

Operator reviews row counts, coverage and the gap list. Phase 2 (features + measurement report) does not begin until approval.
