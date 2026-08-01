"""Tests for cotcm.features — burn-in discipline, window maths, NULL tolerance.
Runs against an in-memory SQLite database with synthetic weekly rows; no
network, no fixtures on disk."""

import unittest
from datetime import date, timedelta

from cotcm import db, features
from cotcm.release_date import release_date_for


def _conn():
    conn = db.connect(":memory:")
    db.init_db(conn)
    return conn


def _insert_weeks(conn, code, n, oi_null_at=None):
    tuesday = date(2024, 1, 2)
    for i in range(n):
        rd = (tuesday + timedelta(weeks=i)).isoformat()
        rel = release_date_for(tuesday + timedelta(weeks=i)).isoformat()
        oi = None if (oi_null_at is not None and i == oi_null_at) else 100000.0 + i * 100
        conn.execute(
            "INSERT INTO cot_raw (cftc_code, report_date, release_date, "
            "open_interest, prod_merc_long, prod_merc_short, mm_long, mm_short, "
            "conc_net_4_long, conc_net_4_short, ingested_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '2026-01-01T00:00:00Z')",
            (code, rd, rel, oi,
             30000.0 + i * 10, 45000.0 - i * 10,   # commercial legs
             25000.0 + i * 20, 20000.0 - i * 5,    # MM legs
             30.0, 25.0))
    conn.commit()


class TestBurnIn(unittest.TestCase):
    def setUp(self):
        self.conn = _conn()
        _insert_weeks(self.conn, "001", 60)
        self.rows = features.compute_contract(self.conn, "001")

    def test_row_count(self):
        self.assertEqual(len(self.rows), 60)

    def test_hp_burn_in(self):
        # 52-week window: NULL through index 50, first value at index 51
        self.assertTrue(all(r["hp_index"] is None for r in self.rows[:51]))
        self.assertIsNotNone(self.rows[51]["hp_index"])

    def test_cot_index_burn_in(self):
        # 156-week window: nothing yet at 60 obs
        self.assertTrue(all(r["cot_idx_comm_3y"] is None for r in self.rows))

    def test_oi_flag_burn_in(self):
        # 26-week median of |dOI|: first value at index 26
        self.assertTrue(all(r["oi_flag"] is None for r in self.rows[:26]))
        self.assertIsNotNone(self.rows[26]["oi_flag"])

    def test_conc_pctile_burn_in(self):
        self.assertTrue(all(r["conc_pctile"] is None for r in self.rows[:51]))
        self.assertIsNotNone(self.rows[51]["conc_pctile"])

    def test_oi_flag_values(self):
        flags = {r["oi_flag"] for r in self.rows if r["oi_flag"] is not None}
        self.assertTrue(flags <= {"new_longs", "new_shorts", "long_liquidation",
                                  "short_covering", "mixed"})

    def test_empty_contract(self):
        self.assertEqual(features.compute_contract(self.conn, "999"), [])


class TestNullOiTolerance(unittest.TestCase):
    def test_null_oi_row_does_not_crash(self):
        conn = _conn()
        _insert_weeks(conn, "001", 60, oi_null_at=40)
        rows = features.compute_contract(conn, "001")
        # one row per week regardless; the NULL week must not emit an OI flag
        self.assertEqual(len(rows), 60)
        self.assertIsNone(rows[40]["oi_flag"])
        # hp_index windows covering the NULL week stay NULL (no partial windows)
        self.assertIsNone(rows[51]["hp_index"])


if __name__ == "__main__":
    unittest.main()
