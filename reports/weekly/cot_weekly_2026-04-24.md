# COT Weekly Opportunity Report — release 2026-04-24

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- None this week.

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL | -0.147 | -1.00 | +1.00 | -0.00 | +0.02 | — | — | USO (options) |
| GC | NEUTRAL | -0.137 | -0.82 | +0.78 | -0.00 | -0.03 | — | — | GLD (options) |
| HG | NEUTRAL | -0.109 | +0.45 | -1.00 | -0.33 | +0.18 | YES | — | CPER / FCX as proxy |
| PL | LEAN_SHORT | -0.308 | -1.00 | +0.38 | -0.00 | -0.02 | — | — | PPLT |
| SI | LEAN_SHORT | -0.221 | -0.97 | +0.72 | -0.00 | -0.09 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Machine-readable block

```json
{
  "release_date": "2026-04-24",
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
      "composite": -0.147233,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": 0.0184,
        "inputs": {
          "hp_index": -0.1310625734940752,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 40.622517024019025,
          "z_delta_mm": 0.07377402578539785,
          "oi_flag": "short_covering",
          "conc_pctile": 58.53423336547734
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
      "composite": -0.136828,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.8176,
        "g_comm": 0.7817,
        "h_mm": -0.0,
        "k_flow": -0.0348,
        "inputs": {
          "hp_index": 0.09599259375339007,
          "cot_idx_comm_3y": 95.6336346580249,
          "cot_idx_mm_3y": 48.71641523865319,
          "z_delta_mm": -0.1392429008534173,
          "oi_flag": "mixed",
          "conc_pctile": 75.79556412729026
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
      "composite": -0.109475,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.4496,
        "g_comm": -1.0,
        "h_mm": -0.3294,
        "k_flow": 0.1771,
        "inputs": {
          "hp_index": 0.27697199217333207,
          "cot_idx_comm_3y": 0.0,
          "cot_idx_mm_3y": 86.58770190803618,
          "z_delta_mm": 0.7084649480782259,
          "oi_flag": "mixed",
          "conc_pctile": 79.07425265188043
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
      "composite": -0.307849,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.3834,
        "h_mm": -0.0,
        "k_flow": -0.0247,
        "inputs": {
          "hp_index": 0.20865311889135435,
          "cot_idx_comm_3y": 87.66831726174964,
          "cot_idx_mm_3y": 73.23072584056891,
          "z_delta_mm": -0.09873881420963404,
          "oi_flag": "mixed",
          "conc_pctile": 33.751205400192866
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
      "composite": -0.220884,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.9689,
        "g_comm": 0.7217,
        "h_mm": -0.0,
        "k_flow": -0.0917,
        "inputs": {
          "hp_index": 0.16346912539586234,
          "cot_idx_comm_3y": 94.43356355014947,
          "cot_idx_mm_3y": 30.529664278018164,
          "z_delta_mm": -0.3668019286340198,
          "oi_flag": "mixed",
          "conc_pctile": 15.429122468659594
        }
      }
    }
  ]
}
```
