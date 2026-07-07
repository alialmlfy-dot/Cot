# Phase 4 Deliverable — Backtest Harness Results

Walk-forward throughout: hp anchors re-derived causally per test year (expanding window, burn-in 2006–2014, 1-year steps); no fitting inside test windows. Costs 5 bps/side. Configurations tried: 2 (0.50 provisional cut, 0.35 approved) — used as the DSR trial count.

## 1. Per-feature IC report (delivered before any composite result)

Spearman rank IC of each RAW feature vs forward returns. Expected signs: hp_index + (risk premium), cot_idx_comm + (contrarian commercial), cot_idx_mm − at extremes (crowding), z_delta_mm + (flow momentum), conc_pctile ~0 (context only, never directional).

### Horizon 1w (rho, |t|>2 flagged)

| Feature | CL | GC | HG | PL | SI | avg |
|---|---|---|---|---|---|---|
| hp_index | +0.052 | -0.004 | -0.030 | -0.020 | +0.033 | 0.006 |
| cot_idx_comm_3y | -0.032 | -0.042 | +0.014 | **+0.115** | +0.004 | 0.012 |
| cot_idx_comm_full | -0.041 | +0.008 | +0.011 | **+0.121** | +0.014 | 0.023 |
| cot_idx_mm_3y | +0.001 | +0.032 | -0.010 | **-0.098** | -0.025 | -0.020 |
| cot_idx_mm_full | -0.015 | +0.030 | -0.018 | **-0.108** | -0.032 | -0.028 |
| z_delta_mm | -0.008 | **-0.070** | -0.056 | **-0.087** | -0.063 | -0.057 |
| z_delta_comm | -0.049 | +0.009 | +0.048 | **+0.084** | +0.034 | 0.025 |
| conc_pctile | +0.037 | +0.017 | **+0.075** | **-0.082** | -0.023 | 0.005 |

### Horizon 2w (rho, |t|>2 flagged)

| Feature | CL | GC | HG | PL | SI | avg |
|---|---|---|---|---|---|---|
| hp_index | **+0.069** | -0.011 | -0.038 | -0.027 | +0.042 | 0.007 |
| cot_idx_comm_3y | -0.028 | -0.067 | -0.005 | **+0.145** | +0.001 | 0.009 |
| cot_idx_comm_full | -0.045 | -0.000 | -0.003 | **+0.160** | +0.014 | 0.025 |
| cot_idx_mm_3y | -0.005 | +0.055 | +0.010 | **-0.118** | -0.025 | -0.017 |
| cot_idx_mm_full | -0.020 | +0.048 | -0.004 | **-0.134** | -0.037 | -0.029 |
| z_delta_mm | +0.000 | -0.046 | -0.043 | **-0.078** | -0.063 | -0.046 |
| z_delta_comm | -0.039 | +0.018 | +0.017 | **+0.088** | +0.042 | 0.025 |
| conc_pctile | **+0.065** | +0.028 | **+0.116** | **-0.092** | -0.031 | 0.017 |

### Horizon 4w (rho, |t|>2 flagged)

| Feature | CL | GC | HG | PL | SI | avg |
|---|---|---|---|---|---|---|
| hp_index | **+0.107** | -0.022 | -0.050 | -0.058 | +0.034 | 0.002 |
| cot_idx_comm_3y | -0.037 | **-0.103** | -0.016 | **+0.183** | +0.001 | 0.006 |
| cot_idx_comm_full | -0.062 | -0.001 | -0.013 | **+0.204** | +0.032 | 0.032 |
| cot_idx_mm_3y | +0.001 | **+0.099** | +0.024 | **-0.157** | -0.015 | -0.010 |
| cot_idx_mm_full | -0.006 | **+0.080** | +0.008 | **-0.178** | -0.039 | -0.027 |
| z_delta_mm | +0.016 | -0.053 | -0.002 | **-0.092** | **-0.069** | -0.040 |
| z_delta_comm | -0.049 | +0.037 | -0.008 | **+0.109** | **+0.070** | 0.032 |
| conc_pctile | **+0.071** | +0.038 | **+0.146** | **-0.120** | -0.026 | 0.022 |

## 2. Primary — state-conditioned forward returns (walk-forward)

Walk-forward sample: 3000 contract-weeks, 2015-01-02 → 2026-06-26.

### 1w forward returns by state (pooled)

| State | n | mean | median | hit% | t (overlap-adj) |
|---|---|---|---|---|---|
| STRONG_LONG | 60 | -0.575% | -0.478% | 40.0 | -1.26 |
| LEAN_LONG | 150 | 0.446% | 0.224% | 54.0 | 1.40 |
| NEUTRAL | 1443 | 0.169% | 0.254% | 53.4 | 1.58 |
| LEAN_SHORT | 802 | 0.227% | 0.267% | 53.2 | 1.41 |
| STRONG_SHORT | 545 | 0.362% | 0.099% | 52.3 | 2.21 |
| **signed (dir. states)** | 1557 | -0.223% | -0.160% | 47.5 | -2.08 |

### 2w forward returns by state (pooled)

| State | n | mean | median | hit% | t (overlap-adj) |
|---|---|---|---|---|---|
| STRONG_LONG | 60 | -0.493% | -0.792% | 41.7 | -0.50 |
| LEAN_LONG | 150 | 0.435% | 0.442% | 53.3 | 0.75 |
| NEUTRAL | 1443 | 0.389% | 0.360% | 53.2 | 1.84 |
| LEAN_SHORT | 802 | 0.462% | 0.316% | 52.6 | 1.40 |
| STRONG_SHORT | 545 | 0.646% | 0.500% | 54.3 | 1.90 |
| **signed (dir. states)** | 1557 | -0.441% | -0.365% | 47.1 | -2.02 |

### 4w forward returns by state (pooled)

| State | n | mean | median | hit% | t (overlap-adj) |
|---|---|---|---|---|---|
| STRONG_LONG | 60 | -1.356% | -1.645% | 36.7 | -0.89 |
| LEAN_LONG | 150 | 0.680% | 1.411% | 60.0 | 0.61 |
| NEUTRAL | 1433 | 0.856% | 0.712% | 54.6 | 2.04 |
| LEAN_SHORT | 802 | 0.990% | 0.535% | 52.7 | 1.58 |
| STRONG_SHORT | 545 | 1.011% | 0.440% | 54.1 | 1.35 |
| **signed (dir. states)** | 1557 | -0.850% | -0.343% | 47.4 | -1.96 |

### Per-contract signed 4w mean (directional states only)

| Root | STRONG_LONG mean/n | STRONG_SHORT mean/n | LEAN_LONG mean/n | LEAN_SHORT mean/n |
|---|---|---|---|---|
| CL | -9.955% / 4 | 1.828% / 111 | 2.635% / 29 | 1.250% / 192 |
| GC | -0.469% / 7 | 1.344% / 155 | -0.728% / 13 | 1.412% / 212 |
| HG | 0.027% / 17 | 1.299% / 99 | -0.576% / 69 | 0.861% / 91 |
| PL | -1.209% / 32 | -0.499% / 71 | 2.423% / 30 | 0.076% / 148 |
| SI | —% / 0 | 0.425% / 109 | 0.236% / 9 | 1.035% / 159 |

## 3. Secondary — state-transition event study

Forward returns after a transition INTO a directional state, vs the unconditional baseline (transitions are the actionable events).

**1w** — baseline: n=2995, mean 0.219%, hit 52.9%

| → State | n | mean | median | hit% | t |
|---|---|---|---|---|---|
| STRONG_LONG | 22 | -0.890% | -0.651% | 31.8 | -1.59 |
| LEAN_LONG | 54 | 1.383% | 1.194% | 61.1 | 2.54 |
| LEAN_SHORT | 262 | 0.382% | 0.378% | 58.4 | 1.51 |
| STRONG_SHORT | 119 | 0.594% | 0.214% | 55.5 | 1.53 |

**2w** — baseline: n=2995, mean 0.436%, hit 53.0%

| → State | n | mean | median | hit% | t |
|---|---|---|---|---|---|
| STRONG_LONG | 22 | -0.016% | 0.041% | 50.0 | -0.01 |
| LEAN_LONG | 54 | 0.849% | -0.052% | 48.1 | 0.91 |
| LEAN_SHORT | 262 | 0.362% | 0.253% | 51.5 | 0.60 |
| STRONG_SHORT | 119 | 0.999% | 0.873% | 58.8 | 1.35 |

**4w** — baseline: n=2985, mean 0.868%, hit 53.9%

| → State | n | mean | median | hit% | t |
|---|---|---|---|---|---|
| STRONG_LONG | 22 | -1.046% | -1.771% | 45.5 | -0.37 |
| LEAN_LONG | 54 | 1.733% | 1.486% | 63.0 | 1.03 |
| LEAN_SHORT | 262 | 1.107% | 0.366% | 51.9 | 0.94 |
| STRONG_SHORT | 119 | 1.974% | 1.232% | 58.8 | 1.08 |

## 4. Strategy Sharpes (state-following convention) + DSR

| Config | ann. Sharpe gross | ann. Sharpe net (5bps/side) |
|---|---|---|
| approved cuts 0.35/0.20 | -0.49 | -0.51 |
| provisional cuts 0.50/0.20 (trial) | -0.49 | -0.51 |

Deflated Sharpe (net, approved config): **DSR = 0.039** (SR* benchmark 0.00 ann., 2 trials, skew -0.49, kurt 9.97, T=600 weeks). DSR is the probability the true Sharpe exceeds the expected-max-of-trials benchmark.

## 5. Tertiary — 5-name cross-sectional spread (LOW CONFIDENCE)

Top-1 vs bottom-1 by composite, 1w hold, 600 weeks: gross SR -0.21, net SR -0.27, DSR 0.174. Flagged low-confidence: 5 names is insufficient breadth for cross-sectional inference (v1.1 design note) — context only, not a signal.

## 6. Honesty notes (residual lookahead & conventions)

- hp anchors: fully walk-forward in this backtest (the live engine's frozen full-sample anchors are NOT used here).
- The 20/80 band and 0.35/0.20 cuts are held fixed across all windows; 0.35 was chosen from the full-sample composite distribution — a mild selection effect, mitigated by the 0.50 trial being counted in the DSR and both configs reported.
- Weights 0.40/0.25/0.20/0.15 are the spec's priors — never fitted, per-contract or otherwise.
- Multi-week t-stats use a conservative sqrt(h) SE inflation for overlapping observations.
- ETF-execution proxy costs only (5 bps/side); futures/options microstructure not modeled — consistent with 'context, not entries'.

## ⛔ STOP — Phase 4 gate

Operator decides: (a) go/no-go on live operation; (b) the single permitted weight-revision round — the §1 IC table identifies any component with no standalone IC whose weight should be considered for zeroing. After that, weights freeze.
