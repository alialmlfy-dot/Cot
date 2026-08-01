"""Tests for cotcm.scoring — the frozen v1.1 composite. These tests pin the
APPROVED maths; if any of them fails, either the code regressed or someone
changed the signal without going through the gate."""

import unittest

from cotcm import scoring

SIG = {
    "weights": {"hp": 0.4, "comm": 0.25, "mm": 0.2, "flow": 0.15},
    "hp_anchors": {"XX": {"p10": 0.10, "p50": 0.20, "p90": 0.40}},
    "cot_band": {"low": 20.0, "high": 80.0},
    "flow": {
        "z_saturation": 2.0,
        "oi_gate": {"new_longs": 1.0, "new_shorts": 1.0,
                    "long_liquidation": 0.5, "short_covering": 0.5,
                    "mixed": 0.5},
    },
    "state_cuts": {"strong": 0.35, "lean": 0.2},
    "crowding_pctile": 90.0,
}


def feat(**kw):
    base = {"cftc_code": "001", "release_date": "2026-07-10",
            "hp_index": 0.20, "cot_idx_comm_3y": 50.0, "cot_idx_mm_3y": 50.0,
            "z_delta_mm": 0.0, "oi_flag": "mixed", "conc_pctile": 50.0}
    base.update(kw)
    return base


class TestFHp(unittest.TestCase):
    def test_anchors(self):
        a = SIG["hp_anchors"]["XX"]
        self.assertEqual(scoring.f_hp(0.20, a), 0.0)
        self.assertEqual(scoring.f_hp(0.10, a), -1.0)
        self.assertEqual(scoring.f_hp(0.40, a), 1.0)

    def test_piecewise_midpoints(self):
        a = SIG["hp_anchors"]["XX"]
        self.assertAlmostEqual(scoring.f_hp(0.15, a), -0.5)
        self.assertAlmostEqual(scoring.f_hp(0.30, a), 0.5)

    def test_clipped_beyond_anchors(self):
        a = SIG["hp_anchors"]["XX"]
        self.assertEqual(scoring.f_hp(-5.0, a), -1.0)
        self.assertEqual(scoring.f_hp(5.0, a), 1.0)

    def test_degenerate_anchor(self):
        self.assertEqual(scoring.f_hp(0.2, {"p10": 0.2, "p50": 0.2, "p90": 0.4}), 0.0)
        self.assertEqual(scoring.f_hp(0.3, {"p10": 0.1, "p50": 0.2, "p90": 0.2}), 0.0)


class TestBands(unittest.TestCase):
    def test_inside_band_is_zero(self):
        self.assertEqual(scoring.g_comm(50.0, SIG["cot_band"]), 0.0)
        self.assertEqual(scoring.g_comm(20.0, SIG["cot_band"]), 0.0)
        self.assertEqual(scoring.g_comm(80.0, SIG["cot_band"]), 0.0)

    def test_extremes(self):
        self.assertEqual(scoring.g_comm(100.0, SIG["cot_band"]), 1.0)
        self.assertEqual(scoring.g_comm(0.0, SIG["cot_band"]), -1.0)

    def test_mm_is_opposite_sign(self):
        self.assertAlmostEqual(scoring.h_mm(95.0, SIG["cot_band"]),
                               -scoring.g_comm(95.0, SIG["cot_band"]))


class TestKFlow(unittest.TestCase):
    def test_none_z_degrades_to_zero(self):
        self.assertEqual(scoring.k_flow(None, "new_longs", SIG["flow"]), 0.0)

    def test_saturation_clip(self):
        self.assertEqual(scoring.k_flow(4.0, "new_longs", SIG["flow"]), 1.0)

    def test_oi_gate(self):
        self.assertAlmostEqual(scoring.k_flow(2.0, "mixed", SIG["flow"]), 0.5)
        self.assertAlmostEqual(scoring.k_flow(2.0, None, SIG["flow"]), 0.5)


class TestClassify(unittest.TestCase):
    def test_states(self):
        c = SIG["state_cuts"]
        self.assertEqual(scoring.classify(0.50, c), "STRONG_LONG")
        self.assertEqual(scoring.classify(0.35, c), "STRONG_LONG")
        self.assertEqual(scoring.classify(0.20, c), "LEAN_LONG")
        self.assertEqual(scoring.classify(-0.20, c), "LEAN_SHORT")
        self.assertEqual(scoring.classify(-0.35, c), "STRONG_SHORT")
        self.assertEqual(scoring.classify(0.199, c), "NEUTRAL")


class TestScoreRow(unittest.TestCase):
    def test_neutral_inputs_zero_composite(self):
        s = scoring.score_row(feat(), "XX", SIG)
        self.assertIsNotNone(s)
        self.assertEqual(s["composite"], 0.0)
        self.assertEqual(s["state"], "NEUTRAL")
        self.assertEqual(s["crowding_flag"], 0)
        self.assertEqual(s["divergence_aligned"], 0)

    def test_null_core_suppresses_score(self):
        for key in ("hp_index", "cot_idx_comm_3y", "cot_idx_mm_3y"):
            self.assertIsNone(scoring.score_row(feat(**{key: None}), "XX", SIG))

    def test_null_flow_still_scores(self):
        s = scoring.score_row(feat(z_delta_mm=None, oi_flag=None), "XX", SIG)
        self.assertIsNotNone(s)

    def test_divergence_aligned(self):
        s = scoring.score_row(
            feat(cot_idx_comm_3y=95.0, cot_idx_mm_3y=5.0), "XX", SIG)
        # g>0 (commercials crowded long -> bullish) and h>0 (MM crowded short
        # -> bullish): aligned contrarian
        self.assertEqual(s["divergence_aligned"], 1)

    def test_crowding_flag(self):
        s = scoring.score_row(feat(conc_pctile=95.0), "XX", SIG)
        self.assertEqual(s["crowding_flag"], 1)


if __name__ == "__main__":
    unittest.main()
