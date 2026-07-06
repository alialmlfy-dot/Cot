# Phase 2 Measurement Report — Features & Proposed Cuts

MEASURE FIRST, THRESHOLD SECOND. This report computes the §4 features over full history and distributions per feature per contract. The cut points in section 7 are **proposals** for operator approval — no score is computed and no threshold is frozen until the Phase 2 gate is passed.

Window/burn-in: hp_index 52wk SMA · COT index 156wk (3y) and inception-to-date (full), both from obs 156 · z-delta vs trailing 156 WoW deltas · oi_flag 26wk median · conc_pctile causal expanding, 52wk burn-in. No partial-window values.

## 1. Feature distributions (per contract)

### hp_index

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 995 | -0.1392 | -0.1142 | -0.0465 | -0.00544 | 0.037 | 0.09894 | 0.1456 | 0.1619 | 0.1741 | 0.04247 | 0.07685 |
| GC | 995 | 0.03736 | 0.0679 | 0.07502 | 0.1151 | 0.19 | 0.2987 | 0.3557 | 0.3731 | 0.398 | 0.205 | 0.1021 |
| HG | 995 | 0.05816 | 0.09832 | 0.1203 | 0.165 | 0.2101 | 0.2626 | 0.3588 | 0.4011 | 0.4169 | 0.2245 | 0.08446 |
| PL | 995 | 0.1646 | 0.2086 | 0.2365 | 0.303 | 0.365 | 0.4264 | 0.4544 | 0.4618 | 0.4877 | 0.3579 | 0.07912 |
| SI | 995 | 0.1348 | 0.1509 | 0.1605 | 0.2133 | 0.2572 | 0.3211 | 0.3922 | 0.4396 | 0.4601 | 0.2686 | 0.0821 |

### cot_idx_comm_3y

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 891 | 0 | 1.153 | 5.204 | 33.52 | 73.13 | 95 | 100 | 100 | 100 | 62.22 | 34.73 |
| GC | 891 | 0 | 4.319 | 11.25 | 28.07 | 58.42 | 81.16 | 94.9 | 98.54 | 100 | 54.48 | 30.32 |
| HG | 891 | 0 | 1.648 | 7.433 | 21.55 | 47.91 | 71.22 | 86 | 92.29 | 100 | 47.08 | 28.8 |
| PL | 891 | 0 | 0.4937 | 9.618 | 27.72 | 49.93 | 71.25 | 87.23 | 94.07 | 100 | 49.51 | 27.92 |
| SI | 891 | 0 | 7.757 | 19.22 | 33.47 | 54.24 | 76.56 | 92.24 | 98.05 | 100 | 54.93 | 26.86 |

### cot_idx_comm_full

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 891 | 0 | 4.422 | 13.22 | 40.86 | 74.46 | 92.83 | 98.76 | 100 | 100 | 65.41 | 31.35 |
| GC | 891 | 0 | 12.9 | 19 | 34.72 | 63.49 | 76.09 | 84.13 | 89.15 | 100 | 56.01 | 25.17 |
| HG | 891 | 0 | 3.207 | 8.29 | 22.57 | 45.48 | 64.02 | 78.63 | 84.67 | 100 | 44.56 | 25.51 |
| PL | 891 | 0 | 1.276 | 9.945 | 25.5 | 40.32 | 52.21 | 62.99 | 71.42 | 90.15 | 38.51 | 19.91 |
| SI | 891 | 0 | 13.18 | 22.52 | 38.02 | 58.26 | 71.44 | 84.66 | 89.48 | 100 | 54.87 | 23.28 |

### cot_idx_mm_3y

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 891 | 0 | 8.21 | 14.32 | 30.27 | 52.61 | 70.7 | 88.01 | 95.97 | 100 | 51.13 | 26.41 |
| GC | 891 | 0 | 1.647 | 8.049 | 28.65 | 53.93 | 75.97 | 91.07 | 96.33 | 100 | 51.82 | 29.32 |
| HG | 891 | 0 | 6.773 | 13.07 | 30.11 | 52.26 | 72.09 | 89.67 | 97.67 | 100 | 51.48 | 27.35 |
| PL | 891 | 0 | 3.884 | 11.69 | 29.27 | 50.05 | 70.82 | 91.25 | 98.99 | 100 | 49.99 | 27.66 |
| SI | 891 | 0 | 4.146 | 11.68 | 31.04 | 52.48 | 71.12 | 83.39 | 92.82 | 100 | 50.51 | 26.46 |

### cot_idx_mm_full

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 891 | 0.87 | 22.72 | 27.09 | 40 | 58.88 | 74.85 | 89.72 | 96.46 | 100 | 58.06 | 22.7 |
| GC | 891 | 0 | 8.851 | 16.86 | 34.75 | 53.07 | 69.93 | 84.91 | 91.46 | 100 | 51.87 | 24.79 |
| HG | 891 | 0 | 9.872 | 17.38 | 31.97 | 48.48 | 67.35 | 82.6 | 94.55 | 100 | 49.95 | 24.21 |
| PL | 891 | 0 | 14.16 | 20.44 | 34.69 | 50.7 | 66.14 | 91.57 | 97.95 | 100 | 51.52 | 24.5 |
| SI | 891 | 0 | 7.856 | 15.01 | 32.12 | 48.55 | 60.84 | 74.69 | 88.49 | 100 | 46.96 | 22.53 |

### z_delta_mm

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 890 | -3.962 | -1.874 | -1.355 | -0.6492 | 0.009144 | 0.652 | 1.322 | 1.784 | 4.32 | -0.003308 | 1.077 |
| GC | 890 | -3.228 | -1.664 | -1.237 | -0.6367 | -0.0132 | 0.5674 | 1.295 | 1.691 | 3.374 | -0.004988 | 1.009 |
| HG | 890 | -5.098 | -1.952 | -1.357 | -0.603 | 0.01211 | 0.6632 | 1.349 | 1.851 | 3.865 | 0.00825 | 1.138 |
| PL | 890 | -6.041 | -1.95 | -1.51 | -0.6611 | 0.03853 | 0.7084 | 1.446 | 1.898 | 5.01 | 0.0042 | 1.197 |
| SI | 890 | -5.024 | -1.784 | -1.216 | -0.5684 | -0.02303 | 0.5606 | 1.258 | 1.788 | 5.456 | -0.0007617 | 1.069 |

### z_delta_comm

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 890 | -3.604 | -1.662 | -1.227 | -0.6197 | 0.01922 | 0.6592 | 1.218 | 1.683 | 4.909 | 0.01692 | 1.038 |
| GC | 890 | -4.235 | -1.476 | -1.081 | -0.5003 | -0.01399 | 0.5348 | 1.088 | 1.469 | 5.092 | 0.007515 | 0.932 |
| HG | 890 | -4.748 | -1.822 | -1.331 | -0.6057 | -0.0003951 | 0.6323 | 1.378 | 1.733 | 4.408 | -0.003187 | 1.103 |
| PL | 890 | -3.665 | -1.673 | -1.249 | -0.6527 | -0.04634 | 0.5654 | 1.347 | 1.859 | 6.511 | -0.0003808 | 1.095 |
| SI | 890 | -4.279 | -1.511 | -1.175 | -0.5976 | -0.001975 | 0.5546 | 1.214 | 1.695 | 4.816 | 0.008217 | 0.9996 |

### conc_pctile

| Root | n | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CL | 995 | 0.9444 | 6.859 | 12.12 | 31.88 | 57.16 | 81.92 | 95.14 | 98.11 | 100 | 55.98 | 29.27 |
| GC | 995 | 0.1479 | 3.97 | 8.938 | 27.07 | 45.99 | 67.86 | 85.34 | 92.91 | 100 | 47.47 | 26.67 |
| HG | 995 | 0.1002 | 1.282 | 3.121 | 10.44 | 30.31 | 53.29 | 71.5 | 80.09 | 100 | 34.08 | 25.9 |
| PL | 995 | 0.156 | 1.493 | 3.8 | 15.51 | 37.4 | 69.93 | 85.08 | 90.8 | 100 | 42.21 | 29.91 |
| SI | 995 | 0.2268 | 2.374 | 5.099 | 14.77 | 36.82 | 60.61 | 77.1 | 91.3 | 100 | 39.08 | 27.32 |

## 2. Commercial COT-index extremes (dated, full-history lookback)

Episodes where `cot_idx_comm_full` > 95 (commercials at a record net-long extreme → contrarian-bullish) or < 5 (record net-short → contrarian-bearish). Consecutive weeks grouped.

- **CL** — high (>95): May-2012..Jul-2012 (10w, peak 100), Aug-2012..Aug-2012 (3w, peak 100), Sep-2012..Nov-2012 (12w, peak 100), Dec-2012..Mar-2013 (15w, peak 100), Apr-2013..Jun-2013 (9w, peak 100), Jun-2013..Sep-2013 (15w, peak 100), Aug-2019..Aug-2019 (1w, peak 96), Oct-2019..Oct-2019 (2w, peak 95), Oct-2019..Oct-2019 (1w, peak 95), Mar-2020..Mar-2020 (2w, peak 97), Sep-2021..Sep-2021 (3w, peak 98), Dec-2021..Apr-2022 (20w, peak 100), Aug-2022..Sep-2022 (7w, peak 100), Nov-2023..Feb-2024 (14w, peak 100), Aug-2024..Aug-2024 (1w, peak 96), Sep-2024..Dec-2024 (16w, peak 100), Jan-2025..Apr-2025 (13w, peak 100), May-2025..May-2025 (1w, peak 96), Jul-2025..Nov-2025 (18w, peak 100), Apr-2026..Jun-2026 (13w, peak 100)
  - low (<5): Jun-2009..Jun-2009 (2w, trough 0), Nov-2009..Jan-2010 (12w, trough 0), Jan-2016..Jun-2016 (20w, trough 0), Aug-2016..Sep-2016 (3w, trough 0), Oct-2016..Oct-2016 (3w, trough 0), Jan-2017..Mar-2017 (9w, trough 0)

- **GC** — high (>95): May-2013..May-2013 (2w, peak 100), Jun-2013..Aug-2013 (12w, peak 100), Sep-2013..Oct-2013 (3w, peak 98), Oct-2013..Oct-2013 (1w, peak 97), Nov-2013..Jan-2014 (10w, peak 100)
  - low (<5): Jun-2009..Jun-2009 (2w, trough 0), Sep-2009..Sep-2009 (3w, trough 0), Oct-2009..Oct-2009 (3w, trough 0), Nov-2009..Nov-2009 (4w, trough 0), Dec-2009..Dec-2009 (1w, trough 4), Jan-2010..Jan-2010 (1w, trough 4), May-2010..May-2010 (2w, trough 0), Jun-2010..Jun-2010 (4w, trough 0), Oct-2012..Oct-2012 (2w, trough 3)

- **HG** — high (>95): Jan-2015..Jan-2015 (1w, peak 100), Jan-2016..Jan-2016 (2w, peak 100), Jun-2016..Jun-2016 (1w, peak 97), Aug-2019..Aug-2019 (2w, peak 100), Aug-2019..Sep-2019 (2w, peak 100)
  - low (<5): Jul-2009..Aug-2009 (4w, trough 0), Sep-2009..Sep-2009 (3w, trough 0), Oct-2009..Jan-2010 (15w, trough 0), Nov-2010..Nov-2010 (1w, trough 4), Dec-2010..Jan-2011 (6w, trough 2), Nov-2016..Dec-2016 (6w, trough 0), Jan-2017..Feb-2017 (3w, trough 0), Sep-2017..Sep-2017 (2w, trough 4), Jan-2018..Jan-2018 (3w, trough 0), Jun-2018..Jun-2018 (1w, trough 0), Sep-2020..Sep-2020 (1w, trough 1), Oct-2020..Oct-2020 (1w, trough 4), Nov-2020..Jan-2021 (8w, trough 0), Feb-2021..Feb-2021 (2w, trough 0), May-2026..Jun-2026 (5w, trough 0)

- **PL** — high (>95): none
  - low (<5): Jun-2009..Jul-2009 (3w, trough 0), Jul-2009..Dec-2009 (20w, trough 0), Feb-2011..Feb-2011 (1w, trough 0), Jun-2011..Jun-2011 (1w, trough 0), Aug-2011..Sep-2011 (4w, trough 0), Feb-2012..Mar-2012 (4w, trough 0), Aug-2012..Nov-2012 (10w, trough 0), Dec-2012..Dec-2012 (3w, trough 0), Feb-2013..Feb-2013 (4w, trough 0), Mar-2014..Mar-2014 (2w, trough 0), Dec-2019..Jan-2020 (6w, trough 0)

- **SI** — high (>95): Sep-2014..Nov-2014 (10w, peak 100), Mar-2015..Mar-2015 (1w, peak 100), Jun-2015..Jun-2015 (1w, peak 96), Jul-2015..Aug-2015 (6w, peak 100), Sep-2018..Sep-2018 (3w, peak 100)
  - low (<5): Sep-2009..Sep-2009 (1w, trough 5), Oct-2009..Oct-2009 (4w, trough 0), Nov-2009..Dec-2009 (4w, trough 1), Sep-2010..Sep-2010 (2w, trough 3), Sep-2016..Sep-2016 (1w, trough 2), Feb-2017..Mar-2017 (3w, trough 0), Mar-2017..Apr-2017 (4w, trough 0)

## 3. Managed-Money COT-index extremes (dated)

Episodes where `cot_idx_mm_full` > 95 (MM crowded long) or < 5 (MM crowded short).

- **CL** — high (>95): Oct-2009..Nov-2009 (2w, peak 100), Nov-2009..Nov-2009 (1w, peak 95), Jan-2010..Jan-2010 (3w, peak 100), Mar-2010..Mar-2010 (1w, peak 97), Apr-2010..Apr-2010 (3w, peak 100), Nov-2010..Nov-2010 (2w, peak 100), Dec-2010..Dec-2010 (4w, peak 100), Jan-2011..Jan-2011 (2w, peak 97), Feb-2011..Mar-2011 (3w, peak 100), Apr-2011..Apr-2011 (2w, peak 98), Apr-2011..May-2011 (3w, peak 96), Jul-2013..Aug-2013 (3w, peak 100), Feb-2014..Mar-2014 (5w, peak 100), Apr-2014..May-2014 (3w, peak 98), May-2014..Jun-2014 (5w, peak 99), Jan-2017..Feb-2017 (3w, peak 100), Feb-2017..Feb-2017 (2w, peak 100), Dec-2017..Dec-2017 (3w, peak 98), Dec-2017..Feb-2018 (7w, peak 100), Mar-2018..Mar-2018 (1w, peak 96), Mar-2018..Mar-2018 (1w, peak 96)
  - low (<5): Oct-2025..Oct-2025 (3w, trough 1), Nov-2025..Dec-2025 (2w, trough 1)

- **GC** — high (>95): Sep-2009..Oct-2009 (7w, peak 100), Nov-2009..Nov-2009 (1w, peak 96), Nov-2009..Dec-2009 (2w, peak 98), May-2010..May-2010 (2w, peak 97), Jun-2010..Jun-2010 (1w, peak 96), Sep-2010..Sep-2010 (1w, peak 96), Oct-2010..Oct-2010 (3w, peak 99), Aug-2011..Aug-2011 (1w, peak 100), May-2016..May-2016 (1w, peak 96), Jun-2016..Jul-2016 (5w, peak 100), Sep-2016..Sep-2016 (1w, peak 99)
  - low (<5): Nov-2013..Jan-2014 (6w, trough 0), Mar-2015..Mar-2015 (2w, trough 1), Jul-2015..Aug-2015 (7w, trough 0), Nov-2015..Jan-2016 (8w, trough 0), Jul-2018..Oct-2018 (13w, trough 0)

- **HG** — high (>95): Oct-2009..Oct-2009 (1w, peak 96), Dec-2009..Dec-2009 (1w, peak 98), Jan-2010..Jan-2010 (5w, peak 100), Apr-2010..Apr-2010 (3w, peak 100), Oct-2010..Nov-2010 (7w, peak 100), Dec-2010..Jan-2011 (7w, peak 100), Feb-2011..Feb-2011 (1w, peak 96), Jan-2014..Jan-2014 (1w, peak 96), Jul-2014..Jul-2014 (2w, peak 100), Nov-2016..Dec-2016 (6w, peak 100), Jan-2017..Feb-2017 (2w, peak 100), Aug-2017..Sep-2017 (7w, peak 100)
  - low (<5): Mar-2013..Apr-2013 (3w, trough 0), Dec-2015..Dec-2015 (3w, trough 2), Jun-2016..Jun-2016 (2w, trough 0), Jan-2019..Feb-2019 (3w, trough 1), May-2019..Jun-2019 (4w, trough 0), Jul-2019..Jul-2019 (2w, trough 0), Aug-2019..Aug-2019 (2w, trough 0), Aug-2019..Sep-2019 (2w, trough 2)

- **PL** — high (>95): Aug-2009..Aug-2009 (4w, peak 100), Sep-2009..Sep-2009 (3w, peak 100), Oct-2009..Oct-2009 (3w, peak 100), Nov-2009..Dec-2009 (4w, peak 100), Mar-2010..Apr-2010 (8w, peak 100), Sep-2010..Nov-2010 (8w, peak 100), Jan-2011..Jan-2011 (1w, peak 95), Jan-2011..Feb-2011 (4w, peak 100), Sep-2012..Oct-2012 (5w, peak 100), Jan-2013..Feb-2013 (5w, peak 100), Jul-2014..Aug-2014 (5w, peak 100), Aug-2016..Aug-2016 (1w, peak 100), Dec-2019..Jan-2020 (6w, peak 100)
  - low (<5): May-2017..May-2017 (3w, trough 0), Jun-2017..Jul-2017 (3w, trough 0), May-2018..Sep-2018 (19w, trough 0)

- **SI** — high (>95): Sep-2010..Oct-2010 (5w, peak 100), Jul-2014..Jul-2014 (1w, peak 95), Oct-2015..Oct-2015 (2w, peak 100), Feb-2016..Feb-2016 (1w, peak 97), Mar-2016..Mar-2016 (2w, peak 100), Apr-2016..May-2016 (5w, peak 100), Jun-2016..Jul-2016 (6w, peak 100), Apr-2017..Apr-2017 (3w, peak 100)
  - low (<5): Mar-2013..Apr-2013 (3w, trough 0), Jun-2013..Jun-2013 (2w, trough 4), Dec-2013..Dec-2013 (1w, trough 0), May-2014..Jun-2014 (2w, trough 0), Oct-2014..Oct-2014 (2w, trough 4), Jun-2015..Jul-2015 (3w, trough 0), Jul-2015..Jul-2015 (2w, trough 0), Dec-2017..Dec-2017 (1w, trough 0), Feb-2018..Apr-2018 (8w, trough 0), Aug-2018..Sep-2018 (5w, trough 0)

## 4. WoW z-delta tail frequency (% of weeks beyond |z|)

| Root | z_delta_mm n | >1σ | >2σ | >3σ | z_delta_comm n | >1σ | >2σ | >3σ |
|---|---|---|---|---|---|---|---|---|
| CL | 890 | 32.0 | 7.1 | 1.1 | 890 | 30.4 | 6.5 | 1.0 |
| GC | 890 | 29.2 | 5.5 | 0.6 | 890 | 23.4 | 4.6 | 0.8 |
| HG | 890 | 31.8 | 8.8 | 2.0 | 890 | 32.4 | 6.7 | 1.3 |
| PL | 890 | 34.4 | 9.0 | 2.1 | 890 | 30.4 | 7.0 | 1.6 |
| SI | 890 | 28.9 | 6.7 | 1.2 | 890 | 28.3 | 5.3 | 1.1 |

## 5. OI-confirmation flag frequency

| Root | new_longs | new_shorts | long_liquidation | short_covering | mixed |
|---|---|---|---|---|---|
| CL | 15.4% | 11.2% | 13.7% | 10.3% | 49.4% |
| GC | 20.4% | 6.2% | 15.8% | 6.9% | 50.7% |
| HG | 16.4% | 12.1% | 13.3% | 10.4% | 47.8% |
| PL | 16.4% | 10.3% | 12.3% | 9.8% | 51.2% |
| SI | 17.5% | 10.1% | 13.8% | 8.6% | 50.0% |

## 6. Concentration percentile — crowding context (never directional)

conc_pctile is the causal percentile of the more-crowded net-4-trader leg vs the contract's own history. Weeks at the 100th percentile (a fresh concentration record) per contract:
- **CL**: 14 record-concentration weeks; most recent 2020-06-26
- **GC**: 8 record-concentration weeks; most recent 2008-06-06
- **HG**: 1 record-concentration weeks; most recent 2009-12-11
- **PL**: 4 record-concentration weeks; most recent 2007-08-17
- **SI**: 8 record-concentration weeks; most recent 2009-03-06

## 7. ⬅ PROPOSED cut points (for operator approval)

### 7.1 Component rescaling to [−1, +1]

**f(hp_index)** — time-series, centered on each contract's own median ("extreme *for this market*"). Proposed anchors: p10 → −1, p50 → 0, p90 → +1, clipped. Sign preserves structural meaning (more net-short-than-usual producers → bullish).

| Root | p10 (→−1) | p50 (→0) | p90 (→+1) |
|---|---|---|---|
| CL | -0.0465 | 0.037 | 0.1456 |
| GC | 0.07502 | 0.19 | 0.3557 |
| HG | 0.1203 | 0.2101 | 0.3588 |
| PL | 0.2365 | 0.365 | 0.4544 |
| SI | 0.1605 | 0.2572 | 0.3922 |

**g(cot_idx_comm_3y)** — commercial contrarian. Proposed: 0 inside the [10, 90] band, ramping to +1 as the index → 100 (commercials record net-long → bullish) and to −1 as it → 0. Extreme band endpoints proposed at the measured p10/p90 per contract (see §1); a round-number fallback of 20/80 is offered for a single global rule.

**h(cot_idx_mm_3y)** — MM crowding, contrarian *at extremes only*. Proposed: 0 inside [10, 90]; as MM index → 100 (crowded long) h → −1; as → 0 (crowded short) h → +1. Note the sign is opposite to g.

**k(z_delta_mm, oi_flag)** — flow confirmation/divergence. Proposed: base = clip(z_delta_mm / 2, −1, +1) (±2σ saturates), gated by oi_flag quality — new_longs/new_shorts → full weight (conviction), mixed → ×0.5, long_liquidation/short_covering → ×0.5 (position unwind, not fresh conviction). §4 tail freqs and §5 flag mix support the 2σ and gating choices.

### 7.2 State classification

With weights (0.40/0.25/0.20/0.15) summing to 1 and each component in [−1,+1], the composite is bounded in [−1,+1]. **Proposed rule:** STRONG at |composite| ≥ 0.50, LEAN at 0.20 ≤ |composite| < 0.50, NEUTRAL at |composite| < 0.20 (sign gives LONG/SHORT). These provisional cuts are to be **confirmed against the measured composite distribution in the Phase 3 dry-run** (outer deciles → STRONG), per spec §5 — no composite is computed in Phase 2.

### 7.3 Setup-quality flag thresholds

- `divergence_aligned`: commercial COT index and MM COT index BOTH in their contrarian-extreme bands (comm and MM both >90 or both <10) pointing the same way — proposed band = [10,90] as above.
- `crowding_flag`: conc_pctile ≥ 90 (contract in the top decile of its own concentration history) — proposed extreme = p90.

## ⛔ STOP — Phase 2 gate

Operator approves the rescaling anchors (§7.1), state cuts (§7.2) and flag thresholds (§7.3). Phase 3 implements §5 with the approved cuts — not before.
