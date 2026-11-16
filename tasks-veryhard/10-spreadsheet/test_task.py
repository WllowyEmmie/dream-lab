import unittest

from sheet import evaluate


class TaskTest(unittest.TestCase):
    def test_values_and_formulas(self):
        cells = {"A1": 2, "A2": 3, "A3": "=A1+A2*2", "B1": "total", "B2": "=SUM(A1:A3)"}
        self.assertEqual(evaluate(cells), {"A1": 2.0, "A2": 3.0, "A3": 8.0, "B1": "total", "B2": 13.0})

    def test_division_by_zero(self):
        self.assertEqual(evaluate({"A1": "=1/0"}), {"A1": "#DIV/0!"})
