# COT Weekly Opportunity Report — release 2026-05-15

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- None this week.

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL | -0.147 | -1.00 | +1.00 | -0.00 | +0.02 | — | — | USO (options) |
| GC | NEUTRAL | -0.127 | -0.84 | +0.80 | -0.00 | +0.06 | — | — | GLD (options) |
| HG | NEUTRAL | -0.137 | +0.56 | -1.00 | -0.95 | +0.54 | YES | YES | CPER / FCX as proxy |
| PL | LEAN_SHORT | -0.249 | -1.00 | +0.43 | -0.00 | +0.29 | — | — | PPLT |
| SI | LEAN_SHORT | -0.293 | -0.99 | +0.17 | -0.00 | +0.39 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Crowding warnings (context only, never directional)

- **HG**: net-4-trader concentration ≥ 90th percentile of own history (92).

## Machine-readable block

```json
{
  "release_date": "2026-05-15",
  "engine": "cot-cm v1.1 time-series composite",
  "note": "Context, not entries. No sizing, no order routing.",
  "transitions": [],
  "contracts": [
    {
      "root": "CL",
      "label": "WTI Crude Oil",
      "sector": "Energy",
      "cftc_code": "067651",
      "etf_mapping": "USO (options)",
      "caveat": null,
      "composite": -0.146663,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": 0.0222,
        "inputs": {
          "hp_index": -0.13298313653602972,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 32.65168592229867,
          "z_delta_mm": 0.0889942632141691,
          "oi_flag": "mixed",
          "conc_pctile": 40.48076923076923
        }
      }
    },
    {
      "root": "GC",
      "label": "Gold",
      "sector": "Metals",
      "cftc_code": "088691",
      "etf_mapping": "GLD (options)",
      "caveat": null,
      "composite": -0.126918,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.84,
        "g_comm": 0.7984,
        "h_mm": -0.0,
        "k_flow": 0.063,
        "inputs": {
          "hp_index": 0.0934192297360665,
          "cot_idx_comm_3y": 95.96855472686958,
          "cot_idx_mm_3y": 50.766489283796325,
          "z_delta_mm": 0.25214361929137374,
          "oi_flag": "mixed",
          "conc_pctile": 77.40384615384616
        }
      }
    },
    {
      "root": "HG",
      "label": "Copper",
      "sector": "Metals",
      "cftc_code": "085692",
      "etf_mapping": "CPER / FCX as proxy",
      "caveat": null,
      "composite": -0.137153,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 1,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.5557,
        "g_comm": -1.0,
        "h_mm": -0.9527,
        "k_flow": 0.5407,
        "inputs": {
          "hp_index": 0.29274853296019476,
          "cot_idx_comm_3y": 0.0,
          "cot_idx_mm_3y": 99.05392858039097,
          "z_delta_mm": 1.0813216049288163,
          "oi_flag": "new_longs",
          "conc_pctile": 91.82692307692308
        }
      }
    },
    {
      "root": "PL",
      "label": "Platinum",
      "sector": "Metals",
      "cftc_code": "076651",
      "etf_mapping": "PPLT",
      "caveat": null,
      "composite": -0.248626,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.4332,
        "h_mm": -0.0,
        "k_flow": 0.2872,
        "inputs": {
          "hp_index": 0.20754210357962424,
          "cot_idx_comm_3y": 88.66301798279906,
          "cot_idx_mm_3y": 73.60140212333044,
          "z_delta_mm": 0.5744778373585026,
          "oi_flag": "new_longs",
          "conc_pctile": 32.01923076923077
        }
      }
    },
    {
      "root": "SI",
      "label": "Silver",
      "sector": "Metals",
      "cftc_code": "084691",
      "etf_mapping": "SLV (options)",
      "caveat": null,
      "composite": -0.29345,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.9873,
        "g_comm": 0.1693,
        "h_mm": -0.0,
        "k_flow": 0.3941,
        "inputs": {
          "hp_index": 0.1616908117983377,
          "cot_idx_comm_3y": 83.386592447514,
          "cot_idx_mm_3y": 42.31841425664004,
          "z_delta_mm": 0.7882986009673282,
          "oi_flag": "new_longs",
          "conc_pctile": 27.98076923076923
        }
      }
    }
  ]
}
```
