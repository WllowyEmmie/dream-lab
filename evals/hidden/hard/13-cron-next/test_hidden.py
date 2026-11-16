import unittest
from datetime import datetime

from cron import next_run


class HiddenTest(unittest.TestCase):        # 5 January 2026 is a Monday
    def check(self, expr, after, expected):
        with self.subTest(expr=expr, after=after):
            self.assertEqual(next_run(expr, datetime(*after)), datetime(*expected))

    def test_steps(self):
        self.check("*/15 * * * *", (2026, 1, 5, 10, 7), (2026, 1, 5, 10, 15))
        self.check("*/15 * * * *", (2026, 1, 5, 10, 45), (2026, 1, 5, 11, 0))
        self.check("0 8-18/5 * * *", (2026, 1, 5, 10, 0), (2026, 1, 5, 13, 0))
        self.check("0 8-18/5 * * *", (2026, 1, 5, 18, 0), (2026, 1, 6, 8, 0))
        self.check("10-30/5 * * * *", (2026, 1, 5, 10, 12), (2026, 1, 5, 10, 15))

    def test_strictly_after(self):
        self.check("*/15 * * * *", (2026, 1, 5, 10, 15), (2026, 1, 5, 10, 30))
        self.check("30 8 * * *", (2026, 1, 5, 8, 30), (2026, 1, 6, 8, 30))

    def test_seconds_are_ignored(self):
        self.check("* * * * *", (2026, 1, 5, 10, 0, 30), (2026, 1, 5, 10, 1))
        self.check("0 10 * * *", (2026, 1, 5, 10, 0, 30), (2026, 1, 6, 10, 0))

    def test_lists_and_ranges(self):
        self.check("5,10-12 * * * *", (2026, 1, 5, 10, 5), (2026, 1, 5, 10, 10))
        self.check("5,10-12 * * * *", (2026, 1, 5, 10, 12), (2026, 1, 5, 11, 5))
        self.check("30 8 1,15 * *", (2026, 1, 15, 8, 30), (2026, 2, 1, 8, 30))

    def test_weekdays(self):
        self.check("0 9 * * 1-5", (2026, 1, 9, 9, 0), (2026, 1, 12, 9, 0))       # Friday -> Monday
        self.check("0 0 * * 0", (2026, 1, 5, 0, 0), (2026, 1, 11, 0, 0))         # Sunday
        self.check("0 0 * * 7", (2026, 1, 5, 0, 0), (2026, 1, 11, 0, 0))         # also Sunday
        self.check("0 0 * * 6,7", (2026, 1, 5, 0, 0), (2026, 1, 10, 0, 0))

    def test_day_of_month_or_day_of_week(self):
        self.check("0 12 13 * 5", (2026, 1, 5, 0, 0), (2026, 1, 9, 12, 0))       # Friday
        self.check("0 12 13 * 5", (2026, 1, 9, 12, 0), (2026, 1, 13, 12, 0))     # the 13th, a Tuesday
        self.check("0 12 13 * 5", (2026, 1, 13, 12, 0), (2026, 1, 16, 12, 0))

    def test_step_on_days_counts_as_restricted(self):
        self.check("0 0 */10 * *", (2026, 1, 21, 0, 0), (2026, 1, 31, 0, 0))
        self.check("0 0 */10 * *", (2026, 1, 31, 0, 0), (2026, 2, 1, 0, 0))
        self.check("0 0 */10 * 1", (2026, 1, 1, 0, 0), (2026, 1, 5, 0, 0))       # a Monday, or the 1st/11th/21st/31st

    def test_month_and_year_rollover(self):
        self.check("59 23 31 12 *", (2026, 12, 31, 23, 59), (2027, 12, 31, 23, 59))
        self.check("0 0 1 1 *", (2026, 6, 1, 0, 0), (2027, 1, 1, 0, 0))
        self.check("0 0 31 * *", (2026, 1, 31, 0, 0), (2026, 3, 31, 0, 0))

    def test_leap_day(self):
        self.check("0 0 29 2 *", (2026, 3, 1, 0, 0), (2028, 2, 29, 0, 0))

    def test_extra_spaces(self):
        self.check("0   9  *  * *", (2026, 1, 5, 9, 0), (2026, 1, 6, 9, 0))

    def test_invalid(self):
        bad = ["60 * * * *", "* 24 * * *", "* * 0 * *", "* * 32 * *", "* * * 13 *", "* * * 0 *", "* * * * 8",
               "* * * *", "* * * * * *", "", "a * * * *", "*/0 * * * *", "5-1 * * * *", "5/2 * * * *",
               "1,,2 * * * *", "1- * * * *", "*/x * * * *", "-1 * * * *"]
        for expr in bad:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError):
                    next_run(expr, datetime(2026, 1, 5))

    def test_never_runs(self):
        for expr in ["0 0 30 2 *", "0 0 31 4 *"]:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError):
                    next_run(expr, datetime(2026, 1, 5))
