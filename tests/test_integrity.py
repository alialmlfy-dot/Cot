"""Tests for cotcm.integrity — the pre-write batch gate."""

import unittest

from cotcm import integrity


def row(code="001", oi=1000.0, **legs):
    r = {"cftc_code": code, "report_date": "2026-07-07", "open_interest": oi}
    for leg in integrity._CATEGORY_LEGS:
        r[leg] = legs.get(leg, 100.0)
    return r


class TestCheckBatch(unittest.TestCase):
    def test_ok_batch(self):
        rows = [row(code=str(i)) for i in range(6)]
        ok, violations = integrity.check_batch(rows, min_contracts=5)
        self.assertTrue(ok, violations)

    def test_empty_batch(self):
        ok, violations = integrity.check_batch([])
        self.assertFalse(ok)
        self.assertIn("empty batch", violations)

    def test_too_few_contracts(self):
        rows = [row(code="001"), row(code="002")]
        ok, violations = integrity.check_batch(rows, min_contracts=5)
        self.assertFalse(ok)
        self.assertTrue(any("distinct contracts" in v for v in violations))

    def test_zero_oi_rejected(self):
        rows = [row(code=str(i)) for i in range(6)]
        rows[0]["open_interest"] = 0
        ok, violations = integrity.check_batch(rows, min_contracts=5)
        self.assertFalse(ok)
        self.assertTrue(any("open_interest" in v for v in violations))

    def test_leg_exceeding_oi_rejected(self):
        rows = [row(code=str(i)) for i in range(6)]
        rows[1]["mm_long"] = 2000.0  # > OI * tolerance
        ok, violations = integrity.check_batch(rows, min_contracts=5)
        self.assertFalse(ok)
        self.assertTrue(any("mm_long" in v for v in violations))

    def test_leg_within_tolerance_ok(self):
        rows = [row(code=str(i)) for i in range(6)]
        rows[1]["mm_long"] = 1049.0  # < 1000 * 1.05
        ok, _ = integrity.check_batch(rows, min_contracts=5)
        self.assertTrue(ok)

    def test_none_leg_skipped(self):
        rows = [row(code=str(i)) for i in range(6)]
        rows[0]["swap_long"] = None
        ok, _ = integrity.check_batch(rows, min_contracts=5)
        self.assertTrue(ok)

    def test_assert_ok_raises(self):
        with self.assertRaises(integrity.IntegrityError):
            integrity.assert_ok([])


if __name__ == "__main__":
    unittest.main()
