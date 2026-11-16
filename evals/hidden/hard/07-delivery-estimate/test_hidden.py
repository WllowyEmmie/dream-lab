import unittest
from datetime import date, datetime, timezone

from store.delivery import estimate


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


class HiddenTest(unittest.TestCase):        # 5 January 2026 is a Monday
    def test_midweek_still_right(self):
        self.assertEqual(estimate(utc(6, 9), 2), date(2026, 1, 8))

    def test_just_before_the_cutoff(self):
        self.assertEqual(estimate(utc(6, 14, 59), 1), date(2026, 1, 7))     # 15:59 in Lagos

    def test_at_the_cutoff(self):
        self.assertEqual(estimate(utc(6, 15), 1), date(2026, 1, 8))         # 16:00 in Lagos

    def test_after_the_cutoff(self):
        self.assertEqual(estimate(utc(6, 15, 30), 1), date(2026, 1, 8))

    def test_saturday_counts_for_transit(self):
        self.assertEqual(estimate(utc(9, 9), 1), date(2026, 1, 10))         # Friday -> Saturday
        self.assertEqual(estimate(utc(9, 9), 2), date(2026, 1, 12))         # Friday -> Monday

    def test_saturday_order_is_dispatched_saturday(self):
        self.assertEqual(estimate(utc(10, 10), 1), date(2026, 1, 12))

    def test_sunday_order(self):
        self.assertEqual(estimate(utc(11, 10), 1), date(2026, 1, 13))       # dispatched Monday

    def test_late_saturday_order(self):
        self.assertEqual(estimate(utc(10, 15), 0), date(2026, 1, 12))

    def test_late_utc_is_next_day_in_lagos(self):
        self.assertEqual(estimate(utc(6, 23, 30), 0), date(2026, 1, 7))
