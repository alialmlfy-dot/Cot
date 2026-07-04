# Phase 0 Verification Report — COT Crude + Metals v1.1

Generated: 2026-07-04T03:26:25Z

## 1. Socrata source

- **Domain used:** `publicreporting.cftc.gov`
- Domain fallback note: `publicdata.cftc.gov -> GET https://publicdata.cftc.gov/api/views/metadata/v1 failed after 4 attempts: HTTPSConnectionPool(host='publicdata.cftc.gov', port=443): Max retries exceeded with url: /api/views/metadata/v1?limit=1 (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 502 Bad Gateway')))`
- **Dataset resolved by live name-match (not hardcoded):** `72hh-3qpy` — "Disaggregated - Futures Only" (data updated 2026-06-26T19:30:54+0000)
- Rejected same-name candidate: `ubmb-6exi` (row access: False, data updated 2022-07-28T19:12:21+0000)
- Live column count: 194; all 26 required field concepts resolved.

## 2. Resolved field map (concept → live API field)

| Concept | Live field |
|---|---|
| report_date | `report_date_as_yyyy_mm_dd` |
| cftc_code | `cftc_contract_market_code` |
| market_name | `market_and_exchange_names` |
| open_interest | `open_interest_all` |
| prod_merc_long | `prod_merc_positions_long` |
| prod_merc_short | `prod_merc_positions_short` |
| swap_long | `swap_positions_long_all` |
| swap_short | `swap__positions_short_all` |
| swap_spread | `swap__positions_spread_all` |
| mm_long | `m_money_positions_long_all` |
| mm_short | `m_money_positions_short_all` |
| mm_spread | `m_money_positions_spread` |
| other_rept_long | `other_rept_positions_long` |
| other_rept_short | `other_rept_positions_short` |
| other_rept_spread | `other_rept_positions_spread` |
| nonrept_long | `nonrept_positions_long_all` |
| nonrept_short | `nonrept_positions_short_all` |
| conc_gross_4_long | `conc_gross_le_4_tdr_long` |
| conc_gross_4_short | `conc_gross_le_4_tdr_short` |
| conc_gross_8_long | `conc_gross_le_8_tdr_long` |
| conc_gross_8_short | `conc_gross_le_8_tdr_short` |
| conc_net_4_long | `conc_net_le_4_tdr_long_all` |
| conc_net_4_short | `conc_net_le_4_tdr_short_all` |
| conc_net_8_long | `conc_net_le_8_tdr_long_all` |
| conc_net_8_short | `conc_net_le_8_tdr_short_all` |
| traders_total | `traders_tot_all` |

## 3. Contract map (stored with `approved=0` — awaiting operator approval)

| Root | Label | Enabled | Selected code | Market name (live) | History | Weeks | Other candidates |
|---|---|---|---|---|---|---|---|
| CL | WTI Crude Oil | yes | `067651` | WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE | 2006-06-13 → 2026-06-23 | 1046 | `067411` (CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE), `067655` (E-MINI CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE) |
| GC | Gold | yes | `088691` | GOLD - COMMODITY EXCHANGE INC. | 2006-06-13 → 2026-06-23 | 1046 | `088695` (MICRO GOLD - COMMODITY EXCHANGE INC.) |
| SI | Silver | yes | `084691` | SILVER - COMMODITY EXCHANGE INC. | 2006-06-13 → 2026-06-23 | 1046 | `084694` (MICRO SILVER - COMMODITY EXCHANGE INC.) |
| HG | Copper | yes | `085692` | COPPER- #1 - COMMODITY EXCHANGE INC. | 2006-06-13 → 2026-06-23 | 1046 | `085699` (MICRO COPPER - COMMODITY EXCHANGE INC.) |
| PL | Platinum | yes | `076651` | PLATINUM - NEW YORK MERCANTILE EXCHANGE | 2006-06-13 → 2026-06-23 | 1046 | — |
| PA | Palladium (optional, disabled by default) | no | `075651` | PALLADIUM - NEW YORK MERCANTILE EXCHANGE | 2006-06-13 → 2026-06-23 | 1046 | — |

Selection rule: candidates merged by contract code across historical renames, ranked by most-recent report date then history length. The operator approves or overrides each code before Phase 1.

## 4. Price source test (weekly closes, all configured sources)

| Source | Root | Symbol | OK | Rows | First | Last | Last close | Error |
|---|---|---|---|---|---|---|---|---|
| stooq | CL | `cl.f` | NO | 0 | — | — | — | HTTP 200 / body starts: '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="robo… |
| stooq | GC | `gc.f` | NO | 0 | — | — | — | HTTP 200 / body starts: '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="robo… |
| stooq | SI | `si.f` | NO | 0 | — | — | — | HTTP 200 / body starts: '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="robo… |
| stooq | HG | `hg.f` | NO | 0 | — | — | — | HTTP 200 / body starts: '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="robo… |
| stooq | PL | `pl.f` | NO | 0 | — | — | — | HTTP 200 / body starts: '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="robo… |
| stooq | PA | `pa.f` | NO | 0 | — | — | — | HTTP 200 / body starts: '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="robo… |
| yahoo | CL | `CL=F` | yes | 1306 | 2001-07-02 | 2026-07-03 | 68.78 | — |
| yahoo | GC | `GC=F` | yes | 1306 | 2001-07-02 | 2026-07-03 | 4187.2998 | — |
| yahoo | SI | `SI=F` | yes | 1306 | 2001-07-02 | 2026-07-03 | 62.815 | — |
| yahoo | HG | `HG=F` | yes | 1306 | 2001-07-02 | 2026-07-03 | 6.224 | — |
| yahoo | PL | `PL=F` | yes | 1185 | 2001-07-02 | 2026-07-03 | 1651.9 | — |
| yahoo | PA | `PA=F` | yes | 1233 | 2001-07-02 | 2026-07-03 | 1272.5 | — |

Note: Yahoo weekly bars are labeled by week-start (Monday); the bar close is the week's final trade (Friday close for full weeks). Friday-date mapping is implemented in Phase 1 for whichever source is approved.

## 5. Plumbing checks

- SQLite schema initialized (contract_map, cot_raw, prices_weekly, features, scores, heartbeat) — idempotent, WAL mode.
- This run itself executed under the heartbeat wrapper; see the `heartbeat` table for the row.

## 6. ⛔ STOP — Phase 0 gate

Operator must approve: (a) the contract map above (then set `approved=1`), (b) the price source choice. Phase 1 (backfill + weekly ingest) does not begin until approval.
