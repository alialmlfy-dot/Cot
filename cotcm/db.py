"""SQLite schema (cot_cm.db). Idempotent init; idempotent writes everywhere
(upserts on natural keys).

Release-lag discipline is structural: cot_raw carries BOTH report_date
(Tuesday snapshot) and release_date (Friday publication). Signal logic and
backtests key off release_date only.
"""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS contract_map (
  cftc_code TEXT PRIMARY KEY,
  root TEXT NOT NULL,
  label TEXT NOT NULL,
  sector TEXT NOT NULL,
  market_name_api TEXT NOT NULL,        -- exact market_and_exchange_names from live API
  etf_mapping TEXT,
  stooq_symbol TEXT,
  enabled INTEGER NOT NULL DEFAULT 1,
  approved INTEGER NOT NULL DEFAULT 0,  -- operator flips to 1 at Phase 0 gate
  first_report_date TEXT,
  last_report_date TEXT,
  n_weeks INTEGER,
  matched_at TEXT NOT NULL,
  caveat TEXT
);

CREATE TABLE IF NOT EXISTS cot_raw (
  cftc_code TEXT NOT NULL,
  report_date TEXT NOT NULL,             -- Tuesday snapshot date
  release_date TEXT NOT NULL,            -- Friday publication date (signal timing key)
  release_date_estimated INTEGER NOT NULL DEFAULT 1,
  open_interest REAL,
  prod_merc_long REAL,
  prod_merc_short REAL,
  swap_long REAL,
  swap_short REAL,
  swap_spread REAL,
  mm_long REAL,
  mm_short REAL,
  mm_spread REAL,
  other_rept_long REAL,
  other_rept_short REAL,
  other_rept_spread REAL,
  nonrept_long REAL,
  nonrept_short REAL,
  conc_gross_4_long REAL,
  conc_gross_4_short REAL,
  conc_gross_8_long REAL,
  conc_gross_8_short REAL,
  conc_net_4_long REAL,
  conc_net_4_short REAL,
  conc_net_8_long REAL,
  conc_net_8_short REAL,
  traders_total REAL,
  ingested_at TEXT NOT NULL,
  PRIMARY KEY (cftc_code, report_date)
);

CREATE TABLE IF NOT EXISTS prices_weekly (
  cftc_code TEXT NOT NULL,
  week_end_date TEXT NOT NULL,           -- Friday close date
  close REAL NOT NULL,
  source TEXT NOT NULL,
  ingested_at TEXT NOT NULL,
  PRIMARY KEY (cftc_code, week_end_date)
);

CREATE TABLE IF NOT EXISTS features (
  cftc_code TEXT NOT NULL,
  release_date TEXT NOT NULL,
  hp_index REAL,
  cot_idx_comm_3y REAL,
  cot_idx_comm_full REAL,
  cot_idx_mm_3y REAL,
  cot_idx_mm_full REAL,
  z_delta_mm REAL,
  z_delta_comm REAL,
  oi_flag TEXT,                          -- new_longs|new_shorts|long_liquidation|short_covering|mixed
  conc_pctile REAL,
  computed_at TEXT NOT NULL,
  PRIMARY KEY (cftc_code, release_date)
);

-- v1.1 time-series engine (spec section 3)
CREATE TABLE IF NOT EXISTS scores (
  cftc_code TEXT NOT NULL,
  release_date TEXT NOT NULL,
  composite REAL,                -- signed: + bullish, - bearish, vs OWN history
  state TEXT,                    -- STRONG_LONG | LEAN_LONG | NEUTRAL | LEAN_SHORT | STRONG_SHORT
  crowding_flag INTEGER,         -- conc_pctile > measured extreme
  divergence_aligned INTEGER,    -- MM extreme + Commercial extreme agree contrarian
  components_json TEXT,
  computed_at TEXT,              -- when this score row was (re)computed
  PRIMARY KEY (cftc_code, release_date)
);

CREATE TABLE IF NOT EXISTS heartbeat (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_ts TEXT NOT NULL,
  job TEXT NOT NULL,
  status TEXT NOT NULL,                  -- ok | error
  latest_report_date TEXT,
  rows_written INTEGER,
  duration_s REAL,
  message TEXT
);
"""


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    # Wait up to 10s on a locked database instead of failing instantly —
    # the Saturday ingest and the Sunday staleness guard may overlap.
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def _migrate(conn):
    """Additive migrations for existing databases (init stays idempotent)."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(scores)")}
    if cols and "computed_at" not in cols:
        conn.execute("ALTER TABLE scores ADD COLUMN computed_at TEXT")
        conn.commit()


def init_db(conn):
    conn.executescript(SCHEMA)
    conn.commit()
    _migrate(conn)
