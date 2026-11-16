import unittest

from store.errors import OutOfStock
from store.inventory import Inventory


class HiddenTest(unittest.TestCase):
    def make(self):
        stock = Inventory()
        stock.receive(10, 100)
        stock.receive(10, 120)
        stock.receive(5, 90)
        return stock

    def test_ship_across_layers(self):
        stock = self.make()
        self.assertEqual(stock.ship(15), 1600)
        self.assertEqual(stock.layers(), [(5, 120), (5, 90)])
        self.assertEqual((stock.units(), stock.value()), (10, 1050))

    def test_ship_exactly_one_layer(self):
        stock = self.make()
        self.assertEqual(stock.ship(10), 1000)
        self.assertEqual(stock.layers(), [(10, 120), (5, 90)])

    def test_ship_everything(self):
        stock = self.make()
        self.assertEqual(stock.ship(25), 1000 + 1200 + 450)
        self.assertEqual((stock.units(), stock.value(), stock.layers(), stock.average_cost()), (0, 0, [], 0))

    def test_too_many_changes_nothing(self):
        stock = self.make()
        with self.assertRaises(OutOfStock):
            stock.ship(26)
        self.assertEqual(stock.layers(), [(10, 100), (10, 120), (5, 90)])

    def test_bad_arguments(self):
        stock = self.make()
        for call in (lambda: stock.ship(0), lambda: stock.ship(-1),
                     lambda: stock.receive(0, 100), lambda: stock.receive(5, -1)):
            with self.assertRaises(ValueError):
                call()
        self.assertEqual(stock.units(), 25)

    def test_free_units_are_allowed(self):
        stock = Inventory()
        stock.receive(3, 0)
        self.assertEqual((stock.value(), stock.ship(2)), (0, 0))

    def test_same_cost_stays_a_separate_layer(self):
        stock = Inventory()
        stock.receive(2, 100)
        stock.receive(3, 100)
        self.assertEqual(stock.layers(), [(2, 100), (3, 100)])

    def test_average_cost_rounds_half_up(self):
        stock = Inventory()
        stock.receive(1, 100)
        stock.receive(1, 101)
        self.assertEqual(stock.average_cost(), 101)      # 100.5
        stock.receive(1, 100)
        self.assertEqual(stock.average_cost(), 100)      # 100.33

    def test_layers_is_a_copy(self):
        stock = self.make()
        stock.layers().clear()
        self.assertEqual(stock.units(), 25)
