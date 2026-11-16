import unittest
from datetime import date, datetime, timezone

from store.errors import BadReference
from store.manifest import build_manifests


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


class HiddenTest(unittest.TestCase):        # 5 January 2026 is a Monday
    def test_grouping_still_right(self):
        orders = [("ORD-2026-000002", utc(6, 9)), ("ORD-2026-000001", utc(6, 10)), ("ORD-2026-000003", utc(7, 8))]
        self.assertEqual(build_manifests(orders), {date(2026, 1, 6): ["ORD-2026-000001", "ORD-2026-000002"],
                                                   date(2026, 1, 7): ["ORD-2026-000003"]})

    def test_references_are_put_in_stored_form(self):
        self.assertEqual(build_manifests([(" ord-2026-12 ", utc(6, 9))]), {date(2026, 1, 6): ["ORD-2026-000012"]})

    def test_same_order_in_two_spellings_listed_once(self):
        orders = [("ord-2026-1", utc(6, 9)), ("ORD-2026-000001", utc(6, 9))]
        self.assertEqual(build_manifests(orders), {date(2026, 1, 6): ["ORD-2026-000001"]})

    def test_malformed_reference(self):
        with self.assertRaises(BadReference):
            build_manifests([("ORD-26-1", utc(6, 9))])

    def test_orders_after_the_cutoff_leave_next_day(self):
        orders = [("ORD-2026-000001", utc(6, 12, 59)), ("ORD-2026-000002", utc(6, 13)), ("ORD-2026-000003", utc(6, 14, 30))]
        self.assertEqual(build_manifests(orders), {date(2026, 1, 6): ["ORD-2026-000001"],
                                                   date(2026, 1, 7): ["ORD-2026-000002", "ORD-2026-000003"]})

    def test_saturday_is_a_working_day(self):
        self.assertEqual(build_manifests([("ORD-2026-000001", utc(10, 10))]), {date(2026, 1, 10): ["ORD-2026-000001"]})

    def test_sunday_and_late_saturday_go_out_monday(self):
        orders = [("ORD-2026-000001", utc(11, 9)), ("ORD-2026-000002", utc(10, 13, 30))]
        self.assertEqual(build_manifests(orders), {date(2026, 1, 12): ["ORD-2026-000001", "ORD-2026-000002"]})

    def test_late_utc_is_next_day_in_lagos(self):
        self.assertEqual(build_manifests([("ORD-2026-000001", utc(6, 23, 30))]), {date(2026, 1, 7): ["ORD-2026-000001"]})
