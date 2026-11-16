import unittest
from datetime import date, datetime, timezone

from store.manifest import build_manifests


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


class TaskTest(unittest.TestCase):          # 5 January 2026 is a Monday
    def test_orders_grouped_by_day(self):
        orders = [("ORD-2026-000002", utc(6, 9)), ("ORD-2026-000001", utc(6, 10)), ("ORD-2026-000003", utc(7, 8))]
        self.assertEqual(build_manifests(orders), {date(2026, 1, 6): ["ORD-2026-000001", "ORD-2026-000002"],
                                                   date(2026, 1, 7): ["ORD-2026-000003"]})

    def test_repeated_order_listed_once(self):
        orders = [("ORD-2026-000001", utc(6, 9)), ("ORD-2026-000001", utc(6, 9))]
        self.assertEqual(build_manifests(orders), {date(2026, 1, 6): ["ORD-2026-000001"]})
