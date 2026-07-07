# Phase 3 Deliverable — Composite Engine + 12 Dry-Run Weekly Reports

§5 implemented with the operator-approved cuts: per-contract hp anchors; global contrarian band [20, 80] for g/h and divergence_aligned; k = clip(z/2) gated by oi_flag; weights 0.40/0.25/0.20/0.15 (global constants).

## 1. Composite distribution vs provisional state cuts

Approval condition from the Phase 2 gate: confirm the provisional cuts (LEAN 0.2, STRONG 0.35) against the measured composite distribution; if the outer deciles land materially away from ±0.35, decile-based cuts win and return to the operator.

| Scope | n | p10 | p25 | p75 | p90 | min | max |
|---|---|---|---|---|---|---|---|
| pooled | 4455 | -0.354 | -0.181 | +0.215 | +0.374 | — | — |
| CL | 891 | -0.283 | -0.151 | +0.221 | +0.355 | -0.462 | +0.568 |
| GC | 891 | -0.389 | -0.244 | +0.210 | +0.419 | -0.785 | +0.846 |
| HG | 891 | -0.355 | -0.181 | +0.190 | +0.367 | -0.807 | +0.564 |
| PL | 891 | -0.357 | -0.153 | +0.247 | +0.366 | -0.803 | +0.560 |
| SI | 891 | -0.363 | -0.206 | +0.191 | +0.381 | -0.794 | +0.691 |

State frequencies under the provisional cuts: {"LEAN_LONG": 14.4, "LEAN_SHORT": 12.7, "NEUTRAL": 50.4, "STRONG_LONG": 12.2, "STRONG_SHORT": 10.2}

**Verdict:** pooled outer deciles (-0.354 / +0.374) are consistent with the provisional STRONG cut ±0.35.

## 2. Dry-run weekly reports (last 12 historical release dates)

- `reports/weekly/cot_weekly_2026-04-10.md`
- `reports/weekly/cot_weekly_2026-04-17.md`
- `reports/weekly/cot_weekly_2026-04-24.md`
- `reports/weekly/cot_weekly_2026-05-01.md`
- `reports/weekly/cot_weekly_2026-05-08.md`
- `reports/weekly/cot_weekly_2026-05-15.md`
- `reports/weekly/cot_weekly_2026-05-22.md`
- `reports/weekly/cot_weekly_2026-05-29.md`
- `reports/weekly/cot_weekly_2026-06-05.md`
- `reports/weekly/cot_weekly_2026-06-12.md`
- `reports/weekly/cot_weekly_2026-06-19.md`
- `reports/weekly/cot_weekly_2026-06-26.md`

Across the 12 dry-run weeks there were 7 state transitions — transitions are the actionable events; steady states are context.

## ⛔ STOP — Phase 3 gate

Operator reviews the 12 sample reports and the state-cut check. Phase 4 (backtest harness) does not begin until approval.
