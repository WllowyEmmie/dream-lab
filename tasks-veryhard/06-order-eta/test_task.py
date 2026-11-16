import unittest
from datetime import date, datetime, timezone

from store.eta import eta


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


class TaskTest(unittest.TestCase):          # 5 January 2026 is a Monday
    def test_midweek(self):
        self.assertEqual(eta(utc(6, 9), 2), date(2026, 1, 8))
        self.assertEqual(eta(utc(5, 10), 1), date(2026, 1, 6))

    def test_no_transit(self):
        self.assertEqual(eta(utc(6, 9), 0), date(2026, 1, 6))
