import unittest

from store import tax


class TaskTest(unittest.TestCase):
    def test_vat_rounds_up(self):
        self.assertEqual(tax.vat(20000), 1500)
        self.assertEqual(tax.vat(60), 5)      # 4.5
        self.assertEqual(tax.vat(110), 9)     # 8.25
        self.assertEqual(tax.vat(1), 1)       # 0.075
        self.assertEqual(tax.vat(0), 0)

    def test_service_charge_rounds_half_up(self):
        self.assertEqual(tax.service_charge(250, 10), 25)
        self.assertEqual(tax.service_charge(5, 10), 1)     # 0.5
        self.assertEqual(tax.service_charge(25, 10), 3)    # 2.5
        self.assertEqual(tax.service_charge(104, 10), 10)  # 10.4
        self.assertEqual(tax.service_charge(1000, 2.5), 25)
