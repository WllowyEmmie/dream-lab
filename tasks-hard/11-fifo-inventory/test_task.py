import unittest

from store.inventory import Inventory


class TaskTest(unittest.TestCase):
    def test_ship_uses_oldest_first(self):
        stock = Inventory()
        stock.receive(10, 100)
        stock.receive(10, 120)
        self.assertEqual(stock.ship(15), 10 * 100 + 5 * 120)
        self.assertEqual(stock.units(), 5)
        self.assertEqual(stock.value(), 600)
