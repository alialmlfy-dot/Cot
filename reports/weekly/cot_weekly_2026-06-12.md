# COT Weekly Opportunity Report — release 2026-06-12

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- **PL**: LEAN_SHORT → **NEUTRAL** (composite -0.170)

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL | -0.166 | -1.00 | +0.92 | -0.00 | +0.04 | — | — | USO (options) |
| GC | NEUTRAL | -0.149 | -0.87 | +0.87 | -0.00 | -0.11 | — | — | GLD (options) |
| HG | NEUTRAL | -0.084 | +0.68 | -0.74 | -0.73 | -0.18 | YES | — | CPER / FCX as proxy |
| PL | NEUTRAL *(new)* | -0.170 | -1.00 | +1.00 | -0.00 | -0.13 | — | — | PPLT |
| SI | LEAN_SHORT | -0.230 | -1.00 | +0.68 | -0.00 | -0.00 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Machine-readable block

```json
{
  "release_date": "2026-06-12",
  "engine": "cot-cm v1.1 time-series composite",
  "note": "Context, not entries. No sizing, no order routing.",
  "transitions": [
    "PL"
  ],
  "contracts": [
    {
      "root": "CL",
      "label": "WTI Crude Oil",
      "sector": "Energy",
      "cftc_code": "067651",
      "etf_mapping": "USO (options)",
      "caveat": null,
      "composite": -0.165603,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.9162,
        "h_mm": -0.0,
        "k_flow": 0.0356,
        "inputs": {
          "hp_index": -0.13686784658655535,
          "cot_idx_comm_3y": 98.32428025312629,
          "cot_idx_mm_3y": 39.103450711271456,
          "z_delta_mm": 0.14248368520108662,
          "oi_flag": "mixed",
          "conc_pctile": 40.42145593869732
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
      "composite": -0.148817,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.8741,
        "g_comm": 0.8684,
        "h_mm": -0.0,
        "k_flow": -0.1085,
        "inputs": {
          "hp_index": 0.08949654807898808,
          "cot_idx_comm_3y": 97.36715612547098,
          "cot_idx_mm_3y": 53.95938095005614,
          "z_delta_mm": -0.43411646868329545,
          "oi_flag": "mixed",
          "conc_pctile": 89.17624521072797
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
      "composite": -0.083813,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.6847,
        "g_comm": -0.7393,
        "h_mm": -0.7266,
        "k_flow": -0.1837,
        "inputs": {
          "hp_index": 0.3119226378786736,
          "cot_idx_comm_3y": 5.214531209579068,
          "cot_idx_mm_3y": 94.53269270942135,
          "z_delta_mm": -0.7346275515779536,
          "oi_flag": "mixed",
          "conc_pctile": 81.70498084291188
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
      "composite": -0.170177,
      "state": "NEUTRAL",
      "prev_state": "LEAN_SHORT",
      "transition": true,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": -0.1345,
        "inputs": {
          "hp_index": 0.20580007125942187,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 57.81341284070992,
          "z_delta_mm": -0.5380434796610226,
          "oi_flag": "long_liquidation",
          "conc_pctile": 27.298850574712645
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
      "composite": -0.230122,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.6801,
        "h_mm": -0.0,
        "k_flow": -0.001,
        "inputs": {
          "hp_index": 0.15929381731352288,
          "cot_idx_comm_3y": 93.60203415455452,
          "cot_idx_mm_3y": 33.154897299516,
          "z_delta_mm": -0.00392231088317826,
          "oi_flag": "mixed",
          "conc_pctile": 27.10727969348659
        }
      }
    }
  ]
}
```
