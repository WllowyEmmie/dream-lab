import unittest
from datetime import date, datetime, timezone

from store.dispatch import dispatch_date


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


class TaskTest(unittest.TestCase):          # 5 January 2026 is a Monday
    def test_before_cutoff(self):
        self.assertEqual(dispatch_date(utc(6, 9)), date(2026, 1, 6))
        self.assertEqual(dispatch_date(utc(6, 14, 59)), date(2026, 1, 6))    # 15:59 in Lagos

    def test_at_or_after_cutoff(self):
        self.assertEqual(dispatch_date(utc(6, 15)), date(2026, 1, 7))        # 16:00 in Lagos
        self.assertEqual(dispatch_date(utc(9, 16)), date(2026, 1, 10))       # Friday evening -> Saturday

    def test_saturday_is_a_working_day(self):
        self.assertEqual(dispatch_date(utc(10, 10)), date(2026, 1, 10))
        self.assertEqual(dispatch_date(utc(10, 15, 30)), date(2026, 1, 12))  # late Saturday -> Monday

    def test_sunday(self):
        self.assertEqual(dispatch_date(utc(11, 8)), date(2026, 1, 12))

    def test_late_utc_is_next_day_in_lagos(self):
        self.assertEqual(dispatch_date(utc(6, 23, 30)), date(2026, 1, 7))    # 00:30 Wednesday in Lagos
