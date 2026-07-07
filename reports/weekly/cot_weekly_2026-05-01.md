# COT Weekly Opportunity Report — release 2026-05-01

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- None this week.

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL | -0.177 | -1.00 | +1.00 | -0.00 | -0.18 | — | — | USO (options) |
| GC | NEUTRAL | -0.138 | -0.83 | +0.80 | -0.00 | -0.05 | — | — | GLD (options) |
| HG | NEUTRAL | -0.129 | +0.49 | -1.00 | -0.39 | +0.02 | YES | YES | CPER / FCX as proxy |
| PL | LEAN_SHORT | -0.254 | -1.00 | +0.63 | -0.00 | -0.07 | — | — | PPLT |
| SI | LEAN_SHORT | -0.271 | -0.97 | +0.43 | -0.00 | +0.07 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Crowding warnings (context only, never directional)

- **HG**: net-4-trader concentration ≥ 90th percentile of own history (94).

## Machine-readable block

```json
{
  "release_date": "2026-05-01",
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
      "composite": -0.176829,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": -0.1789,
        "inputs": {
          "hp_index": -0.1314470963854196,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 34.867604042211326,
          "z_delta_mm": -0.715441531050091,
          "oi_flag": "mixed",
          "conc_pctile": 50.481695568400774
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
      "composite": -0.137883,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.8251,
        "g_comm": 0.7992,
        "h_mm": -0.0,
        "k_flow": -0.0509,
        "inputs": {
          "hp_index": 0.09512513248399315,
          "cot_idx_comm_3y": 95.9840602856124,
          "cot_idx_mm_3y": 47.404758417549516,
          "z_delta_mm": -0.20368474549468835,
          "oi_flag": "mixed",
          "conc_pctile": 72.83236994219654
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
      "composite": -0.129153,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 1,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.4867,
        "g_comm": -1.0,
        "h_mm": -0.3859,
        "k_flow": 0.0223,
        "inputs": {
          "hp_index": 0.2824899904143622,
          "cot_idx_comm_3y": 0.0,
          "cot_idx_mm_3y": 87.71863785791363,
          "z_delta_mm": 0.08933890555683291,
          "oi_flag": "short_covering",
          "conc_pctile": 94.21965317919076
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
      "composite": -0.253893,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.626,
        "h_mm": -0.0,
        "k_flow": -0.0693,
        "inputs": {
          "hp_index": 0.2080483447047911,
          "cot_idx_comm_3y": 92.52019807140995,
          "cot_idx_mm_3y": 69.49978847277343,
          "z_delta_mm": -0.27720487730500226,
          "oi_flag": "mixed",
          "conc_pctile": 41.23314065510597
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
      "composite": -0.270825,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.9737,
        "g_comm": 0.4308,
        "h_mm": -0.0,
        "k_flow": 0.073,
        "inputs": {
          "hp_index": 0.1630032201926517,
          "cot_idx_comm_3y": 88.6162938528674,
          "cot_idx_mm_3y": 33.50207795317337,
          "z_delta_mm": 0.29192517268508,
          "oi_flag": "short_covering",
          "conc_pctile": 31.984585741811177
        }
      }
    }
  ]
}
```
