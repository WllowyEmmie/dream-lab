import unittest
from datetime import date, datetime, timezone

from store.dispatch import dispatch_date


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


class TaskTest(unittest.TestCase):          # 5 January 2026 is a Monday
    def test_before_the_new_cutoff(self):
        self.assertEqual(dispatch_date(utc(6, 9)), date(2026, 1, 6))
        self.assertEqual(dispatch_date(utc(6, 12, 59)), date(2026, 1, 6))    # 13:59 in Lagos

    def test_at_or_after_the_new_cutoff(self):
        self.assertEqual(dispatch_date(utc(6, 13)), date(2026, 1, 7))        # 14:00 in Lagos
        self.assertEqual(dispatch_date(utc(6, 14, 30)), date(2026, 1, 7))    # 15:30 in Lagos: same day under the old rule

    def test_working_days_unchanged(self):
        self.assertEqual(dispatch_date(utc(10, 10)), date(2026, 1, 10))      # Saturday morning
        self.assertEqual(dispatch_date(utc(10, 13, 30)), date(2026, 1, 12))  # Saturday afternoon -> Monday
        self.assertEqual(dispatch_date(utc(11, 8)), date(2026, 1, 12))       # Sunday -> Monday
