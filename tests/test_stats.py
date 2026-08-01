"""Tests for cotcm.stats — the pure-python statistics helpers."""

import unittest

from cotcm import stats


class TestMean(unittest.TestCase):
    def test_basic(self):
        self.assertAlmostEqual(stats.mean([1.0, 2.0, 3.0]), 2.0)

    def test_empty(self):
        self.assertIsNone(stats.mean([]))


class TestPstdev(unittest.TestCase):
    def test_population(self):
        # population sd of [2, 4, 4, 4, 5, 5, 7, 9] is 2.0
        self.assertAlmostEqual(stats.pstdev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_too_short(self):
        self.assertIsNone(stats.pstdev([1.0]))
        self.assertIsNone(stats.pstdev([]))


class TestMedian(unittest.TestCase):
    def test_odd(self):
        self.assertEqual(stats.median([3, 1, 2]), 2)

    def test_even(self):
        self.assertEqual(stats.median([4, 1, 3, 2]), 2.5)

    def test_empty(self):
        self.assertIsNone(stats.median([]))


class TestPercentile(unittest.TestCase):
    def test_linear_interpolation(self):
        xs = list(range(11))  # 0..10
        self.assertAlmostEqual(stats.percentile(xs, 0), 0)
        self.assertAlmostEqual(stats.percentile(xs, 50), 5)
        self.assertAlmostEqual(stats.percentile(xs, 100), 10)
        self.assertAlmostEqual(stats.percentile(xs, 25), 2.5)

    def test_single_and_empty(self):
        self.assertEqual(stats.percentile([7.0], 90), 7.0)
        self.assertIsNone(stats.percentile([], 50))


class TestPctRankLeq(unittest.TestCase):
    def test_monotonic_causal(self):
        xs = [10, 20, 30, 40]
        self.assertAlmostEqual(stats.pct_rank_leq(10, xs), 25.0)
        self.assertAlmostEqual(stats.pct_rank_leq(40, xs), 100.0)
        self.assertAlmostEqual(stats.pct_rank_leq(35, xs), 75.0)

    def test_empty(self):
        self.assertIsNone(stats.pct_rank_leq(5, []))


if __name__ == "__main__":
    unittest.main()
