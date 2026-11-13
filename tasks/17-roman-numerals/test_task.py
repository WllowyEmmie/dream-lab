import unittest

from roman import to_int


class TaskTest(unittest.TestCase):
    def test_numerals(self):
        cases = {"III": 3, "IV": 4, "IX": 9, "XIV": 14, "XL": 40, "MCMXCIV": 1994, "MMXXVI": 2026}
        for numeral, expected in cases.items():
            with self.subTest(numeral=numeral):
                self.assertEqual(to_int(numeral), expected)
