# COT Weekly Opportunity Report — release 2026-05-08

*Time-series composite vs each contract's own history. Context for the analysis layer — never sizes or places trades.*

## State transitions (the actionable events)

- None this week.

## Per-contract state

| Root | State | Composite | f(hp) | g(comm) | h(mm) | k(flow) | Diverg.✓ | Crowding⚠ | ETF |
|---|---|---|---|---|---|---|---|---|---|
| CL | NEUTRAL | -0.175 | -1.00 | +1.00 | -0.00 | -0.17 | — | — | USO (options) |
| GC | NEUTRAL | -0.101 | -0.83 | +0.88 | -0.00 | +0.08 | — | — | GLD (options) |
| HG | NEUTRAL | -0.110 | +0.52 | -0.91 | -0.49 | +0.05 | YES | YES | CPER / FCX as proxy |
| PL | LEAN_SHORT | -0.255 | -1.00 | +0.62 | -0.00 | -0.06 | — | — | PPLT |
| SI | LEAN_SHORT | -0.261 | -0.98 | +0.52 | -0.00 | +0.01 | — | — | SLV (options) |

## Divergence-aligned setups (highest-quality class)

- **HG**: commercial and managed-money COT indices both at contrarian extremes, aligned bearish.

## Crowding warnings (context only, never directional)

- **HG**: net-4-trader concentration ≥ 90th percentile of own history (94).

## Machine-readable block

```json
{
  "release_date": "2026-05-08",
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
      "composite": -0.175276,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 1.0,
        "h_mm": -0.0,
        "k_flow": -0.1685,
        "inputs": {
          "hp_index": -0.1321816591368805,
          "cot_idx_comm_3y": 100.0,
          "cot_idx_mm_3y": 32.06018586638572,
          "z_delta_mm": -0.3370170720231035,
          "oi_flag": "new_shorts",
          "conc_pctile": 41.57844080846968
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
      "composite": -0.101068,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.8332,
        "g_comm": 0.8829,
        "h_mm": -0.0,
        "k_flow": 0.0764,
        "inputs": {
          "hp_index": 0.09419913265937357,
          "cot_idx_comm_3y": 97.6586606298358,
          "cot_idx_mm_3y": 49.23635860632395,
          "z_delta_mm": 0.30575670777431785,
          "oi_flag": "mixed",
          "conc_pctile": 74.87969201154957
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
      "composite": -0.110083,
      "state": "NEUTRAL",
      "prev_state": "NEUTRAL",
      "transition": false,
      "crowding_flag": 1,
      "divergence_aligned": 1,
      "components": {
        "f_hp": 0.5209,
        "g_comm": -0.9119,
        "h_mm": -0.492,
        "k_flow": 0.0527,
        "inputs": {
          "hp_index": 0.287579327193571,
          "cot_idx_comm_3y": 1.762644381311822,
          "cot_idx_mm_3y": 89.83997925502103,
          "z_delta_mm": 0.21084615084829902,
          "oi_flag": "mixed",
          "conc_pctile": 94.22521655437922
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
      "composite": -0.255217,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -1.0,
        "g_comm": 0.6169,
        "h_mm": -0.0,
        "k_flow": -0.0629,
        "inputs": {
          "hp_index": 0.20783784207047912,
          "cot_idx_comm_3y": 92.3377638780297,
          "cot_idx_mm_3y": 66.06901831221418,
          "z_delta_mm": -0.25170578520845355,
          "oi_flag": "mixed",
          "conc_pctile": 41.289701636188646
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
      "composite": -0.261411,
      "state": "LEAN_SHORT",
      "prev_state": "LEAN_SHORT",
      "transition": false,
      "crowding_flag": 0,
      "divergence_aligned": 0,
      "components": {
        "f_hp": -0.9811,
        "g_comm": 0.5162,
        "h_mm": -0.0,
        "k_flow": 0.0131,
        "inputs": {
          "hp_index": 0.16228849261541814,
          "cot_idx_comm_3y": 90.32402157853141,
          "cot_idx_mm_3y": 33.907407090694534,
          "z_delta_mm": 0.05255992747530243,
          "oi_flag": "short_covering",
          "conc_pctile": 40.51973051010587
        }
      }
    }
  ]
}
```
