import unittest

from calc import evaluate


class TaskTest(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(evaluate("1 + 2 * 3"), 7.0)
        self.assertEqual(evaluate("(1 + 2) * 3"), 9.0)

    def test_power(self):
        self.assertEqual(evaluate("2 ^ 3"), 8.0)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            evaluate("1 +")
