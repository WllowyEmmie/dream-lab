import unittest
from datetime import datetime

from cron import next_run


class TaskTest(unittest.TestCase):          # 5 January 2026 is a Monday
    def test_every_quarter_hour(self):
        self.assertEqual(next_run("*/15 * * * *", datetime(2026, 1, 5, 10, 7)), datetime(2026, 1, 5, 10, 15))

    def test_daily(self):
        self.assertEqual(next_run("30 8 * * *", datetime(2026, 1, 5, 9, 0)), datetime(2026, 1, 6, 8, 30))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            next_run("60 * * * *", datetime(2026, 1, 5))
