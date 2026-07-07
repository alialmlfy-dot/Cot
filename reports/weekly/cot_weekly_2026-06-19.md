# COT Weekly Opportunity Report — release 2026-06-19

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- **SI**: LEAN_SHORT → **NEUTRAL** (composite -0.198)

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL | -0.148 | -1.00 | +1.00 | -0.00 | +0.01 | — | — | USO (options) |
| GC | NEUTRAL | -0.085 | -0.89 | +1.00 | -0.00 | +0.13 | — | — | GLD (options) |
| HG | NEUTRAL | +0.034 | +0.71 | -0.42 | -0.72 | -0.01 | YES | — | CPER / FCX as proxy |
| PL | NEUTRAL | -0.152 | -1.00 | +1.00 | -0.00 | -0.01 | — | — | PPLT |
| SI | NEUTRAL *(new)* | -0.198 | -1.00 | +0.69 | -0.00 | +0.20 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Machine-readable block

```json
{
  "release_date": "2026-06-19",
  "engine": "cot-cm v1.1 time-series composite",
  "note": "Context, not entries. No sizing, no order routing.",
  "transitions": [
    "SI"
  ],
  "contracts": [
    {
      "root": "CL",
      "label": "WTI Crude Oil",
      "sector": "Energy",
      "cftc_code": "067651",
      "etf_mapping": "USO (options)",
      "caveat": null,
      "composite": -0.147928,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": 0.0138,
        "inputs": {
          "hp_index": -0.13793826036300996,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 39.54575149934965,
          "z_delta_mm": 0.05526370352843049,
          "oi_flag": "mixed",
          "conc_pctile": 39.13875598086124
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
      "composite": -0.085285,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.8857,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": 0.1268,
        "inputs": {
          "hp_index": 0.08815424506628365,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 57.15634103077348,
          "z_delta_mm": 0.5070112878177082,
          "oi_flag": "mixed",
          "conc_pctile": 87.94258373205741
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
      "composite": 0.034416,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.7103,
        "g_comm": -0.4161,
        "h_mm": -0.7184,
        "k_flow": -0.0133,
        "inputs": {
          "hp_index": 0.31572852287622405,
          "cot_idx_comm_3y": 11.678184707491038,
          "cot_idx_mm_3y": 94.368915813662,
          "z_delta_mm": -0.053153813975679046,
          "oi_flag": "mixed",
          "conc_pctile": 75.11961722488039
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
      "composite": -0.152112,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": -0.0141,
        "inputs": {
          "hp_index": 0.20544521742085695,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 57.02774028485666,
          "z_delta_mm": -0.056324872833016085,
          "oi_flag": "mixed",
          "conc_pctile": 24.210526315789473
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
      "composite": -0.198198,
      "state": "NEUTRAL",
      "prev_state": "LEAN_SHORT",
      "transition": true,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.6882,
        "h_mm": -0.0,
        "k_flow": 0.1984,
        "inputs": {
          "hp_index": 0.15846461697626102,
          "cot_idx_comm_3y": 93.76352953303783,
          "cot_idx_mm_3y": 37.39973662157309,
          "z_delta_mm": 0.39677675010604563,
          "oi_flag": "new_longs",
          "conc_pctile": 30.14354066985646
        }
      }
    }
  ]
}
```
