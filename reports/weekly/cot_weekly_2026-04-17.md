# COT Weekly Opportunity Report — release 2026-04-17

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- **CL**: LEAN_SHORT → **NEUTRAL** (composite -0.154)
- **PL**: NEUTRAL → **LEAN_SHORT** (composite -0.273)
- **SI**: NEUTRAL → **LEAN_SHORT** (composite -0.211)

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL *(new)* | -0.154 | -1.00 | +0.76 | -0.00 | +0.37 | — | — | USO (options) |
| GC | NEUTRAL | -0.079 | -0.81 | +0.93 | -0.00 | +0.09 | — | — | GLD (options) |
| HG | NEUTRAL | +0.050 | +0.42 | -0.87 | -0.03 | +0.70 | YES | — | CPER / FCX as proxy |
| PL | LEAN_SHORT *(new)* | -0.273 | -1.00 | +0.44 | -0.00 | +0.11 | — | — | PPLT |
| SI | LEAN_SHORT *(new)* | -0.211 | -0.96 | +0.66 | -0.00 | +0.04 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Machine-readable block

```json
{
  "release_date": "2026-04-17",
  "engine": "cot-cm v1.1 time-series composite",
  "note": "Context, not entries. No sizing, no order routing.",
  "transitions": [
    "CL",
    "PL",
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
      "composite": -0.154273,
      "state": "NEUTRAL",
      "prev_state": "LEAN_SHORT",
      "transition": true,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.7583,
        "h_mm": -0.0,
        "k_flow": 0.3743,
        "inputs": {
          "hp_index": -0.13093644838090876,
          "cot_idx_comm_3y": 95.16640746500778,
          "cot_idx_mm_3y": 40.17550777778432,
          "z_delta_mm": 0.748626700819062,
          "oi_flag": "new_longs",
          "conc_pctile": 47.972972972972975
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
      "composite": -0.079421,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.8106,
        "g_comm": 0.9281,
        "h_mm": -0.0,
        "k_flow": 0.0854,
        "inputs": {
          "hp_index": 0.09679175500435414,
          "cot_idx_comm_3y": 98.5610841486673,
          "cot_idx_mm_3y": 49.597226968705755,
          "z_delta_mm": 0.34166409425036404,
          "oi_flag": "mixed",
          "conc_pctile": 77.60617760617761
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
      "composite": 0.050372,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.4191,
        "g_comm": -0.8652,
        "h_mm": -0.0261,
        "k_flow": 0.6951,
        "inputs": {
          "hp_index": 0.27243622952079183,
          "cot_idx_comm_3y": 2.6951518309515627,
          "cot_idx_mm_3y": 80.52146854375266,
          "z_delta_mm": 1.390235087748971,
          "oi_flag": "new_longs",
          "conc_pctile": 74.22779922779922
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
      "composite": -0.272547,
      "state": "LEAN_SHORT",
      "prev_state": "NEUTRAL",
      "transition": true,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.4414,
        "h_mm": -0.0,
        "k_flow": 0.114,
        "inputs": {
          "hp_index": 0.20853338302386928,
          "cot_idx_comm_3y": 88.82807749109547,
          "cot_idx_mm_3y": 74.63486371602973,
          "z_delta_mm": 0.4560433063775357,
          "oi_flag": "mixed",
          "conc_pctile": 27.895752895752896
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
      "composite": -0.210729,
      "state": "LEAN_SHORT",
      "prev_state": "NEUTRAL",
      "transition": true,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.9553,
        "g_comm": 0.6634,
        "h_mm": -0.0,
        "k_flow": 0.0368,
        "inputs": {
          "hp_index": 0.1647828313236942,
          "cot_idx_comm_3y": 93.26873518194002,
          "cot_idx_mm_3y": 34.63768363804279,
          "z_delta_mm": 0.14734819425491086,
          "oi_flag": "mixed",
          "conc_pctile": 11.96911196911197
        }
      }
    }
  ]
}
```
