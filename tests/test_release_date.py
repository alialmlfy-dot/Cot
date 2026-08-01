"""Tests for cotcm.release_date — the structural report_date -> release_date
mapping (operating rule 3)."""

import unittest
from datetime import date

from cotcm.release_date import friday_of_week, parse_date, release_date_for


class TestParseDate(unittest.TestCase):
    def test_socrata_datetime(self):
        self.assertEqual(parse_date("2026-07-07T00:00:00.000"), date(2026, 7, 7))

    def test_plain_date(self):
        self.assertEqual(parse_date("2026-07-07"), date(2026, 7, 7))


class TestReleaseDateFor(unittest.TestCase):
    def test_tuesday_to_same_week_friday(self):
        # Tuesday 2026-07-07 -> Friday 2026-07-10
        self.assertEqual(release_date_for(date(2026, 7, 7)), date(2026, 7, 10))

    def test_accepts_string(self):
        self.assertEqual(release_date_for("2026-07-07"), date(2026, 7, 10))

    def test_friday_floor_is_inclusive(self):
        # report_date exactly 3 days before a Friday -> that same Friday
        self.assertEqual(release_date_for(date(2026, 7, 7)).weekday(), 4)

    def test_non_tuesday_robustness(self):
        # A Wednesday report: floor is Saturday -> next Friday
        self.assertEqual(release_date_for(date(2026, 7, 8)), date(2026, 7, 17))
        # A Monday report: floor is Thursday -> that week's Friday
        self.assertEqual(release_date_for(date(2026, 7, 6)), date(2026, 7, 10))


class TestFridayOfWeek(unittest.TestCase):
    def test_midweek(self):
        self.assertEqual(friday_of_week(date(2026, 7, 29)), date(2026, 7, 31))

    def test_already_friday(self):
        self.assertEqual(friday_of_week(date(2026, 7, 31)), date(2026, 7, 31))

    def test_saturday_maps_to_same_calendar_week_friday(self):
        # Saturday belongs to the Mon-Sun week whose Friday was the day before
        self.assertEqual(friday_of_week(date(2026, 8, 1)), date(2026, 7, 31))

    def test_string_input(self):
        self.assertEqual(friday_of_week("2026-07-29"), date(2026, 7, 31))


if __name__ == "__main__":
    unittest.main()
