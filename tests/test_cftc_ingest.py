"""Tests for cotcm.cftc_ingest — record parsing and the upsert write path
(late arrivals + CFTC revisions must propagate)."""

import unittest

from cotcm import cftc_ingest, db

FIELDS = {
    "cftc_code": "cftc_contract_market_code",
    "report_date": "report_date_as_yyyy_mm_dd",
}
for concept in cftc_ingest._VALUE_CONCEPTS:
    FIELDS[concept] = concept  # test doubles use the concept names directly


def _rec(code="001", rd="2026-07-07", oi=1000.0, mm_long=100.0):
    rec = {FIELDS["cftc_code"]: code,
           FIELDS["report_date"]: rd + "T00:00:00.000"}
    for concept in cftc_ingest._VALUE_CONCEPTS:
        rec[FIELDS[concept]] = None
    rec[FIELDS["open_interest"]] = oi
    rec[FIELDS["mm_long"]] = mm_long
    return rec


class TestParseRecord(unittest.TestCase):
    def test_release_date_computed(self):
        row = cftc_ingest._parse_record(_rec(), FIELDS)
        self.assertEqual(row["report_date"], "2026-07-07")
        self.assertEqual(row["release_date"], "2026-07-10")  # same-week Friday
        self.assertEqual(row["open_interest"], 1000.0)
        self.assertIsNone(row["mm_short"])

    def test_non_numeric_becomes_none(self):
        rec = _rec()
        rec[FIELDS["mm_long"]] = "N/A"
        row = cftc_ingest._parse_record(rec, FIELDS)
        self.assertIsNone(row["mm_long"])


class TestWriteUpsert(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        db.init_db(self.conn)

    def test_insert_then_revision_updates(self):
        rows = [cftc_ingest._parse_record(_rec(mm_long=100.0), FIELDS)]
        inserted, updated = cftc_ingest._write(self.conn, rows)
        self.assertEqual((inserted, updated), (1, 0))

        # CFTC revises the same (code, report_date): value must be overwritten
        rows2 = [cftc_ingest._parse_record(_rec(mm_long=250.0), FIELDS)]
        inserted, updated = cftc_ingest._write(self.conn, rows2)
        self.assertEqual((inserted, updated), (0, 1))
        got = self.conn.execute(
            "SELECT mm_long FROM cot_raw WHERE cftc_code='001'").fetchone()
        self.assertEqual(got["mm_long"], 250.0)
        n = self.conn.execute("SELECT count(*) c FROM cot_raw").fetchone()["c"]
        self.assertEqual(n, 1)  # still one row — no duplicate

    def test_late_arrival_older_date_inserts(self):
        new = cftc_ingest._parse_record(_rec(rd="2026-07-14"), FIELDS)
        cftc_ingest._write(self.conn, [new])
        # delayed older report arrives after the newer one was ingested
        late = cftc_ingest._parse_record(_rec(rd="2026-07-07"), FIELDS)
        inserted, updated = cftc_ingest._write(self.conn, [late])
        self.assertEqual((inserted, updated), (1, 0))
        n = self.conn.execute("SELECT count(*) c FROM cot_raw").fetchone()["c"]
        self.assertEqual(n, 2)


class TestIncrementalWindow(unittest.TestCase):
    def test_window_floor(self):
        # 35-day trailing window behind 2026-07-28 -> floor 2026-06-23
        from cotcm.release_date import parse_date
        from datetime import timedelta
        floor = (parse_date("2026-07-28") - timedelta(days=35)).isoformat()
        self.assertEqual(floor, "2026-06-23")


if __name__ == "__main__":
    unittest.main()
