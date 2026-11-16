import unittest

from calc import evaluate


class HiddenTest(unittest.TestCase):
    def check(self, cases):
        for text, expected in cases.items():
            with self.subTest(text=text):
                result = evaluate(text)
                self.assertIsInstance(result, float)
                self.assertAlmostEqual(result, expected, places=9)

    def test_basics(self):
        self.check({"1 + 2 * 3": 7, "(1 + 2) * 3": 9, "10 / 4": 2.5, "3.5 * 2": 7, "42": 42, "(((4)))": 4})

    def test_left_to_right(self):
        self.check({"1 - 2 - 3": -4, "8 / 2 / 2": 2, "2 - 3 + 4": 3, "8 / 4 * 2": 4})

    def test_power_is_right_to_left(self):
        self.check({"2 ^ 3 ^ 2": 512, "2^3*2": 16, "2 * 3 ^ 2": 18, "2 ^ 0.5": 2 ** 0.5})

    def test_unary(self):
        self.check({"-3": -3, "+5": 5, "--2": 2, "- - 2": 2, "-+-2": 2, "2 * -3": -6, "2 - -3": 5, "-(2 + 3)": -5})

    def test_power_and_unary_minus(self):
        self.check({"-2 ^ 2": -4, "2 ^ -1": 0.5, "-(2 + 3) ^ 2": -25, "(-2) ^ 2": 4, "2 ^ -2 ^ 2": 2 ** -4})

    def test_spacing(self):
        self.check({"  1+2  ": 3, "1+2": 3, "( 1 + 2 )*3": 9})

    def test_malformed(self):
        for text in ["", "   ", "1 +", "(1 + 2", "1 + 2)", "2 3", "2 $ 3", "1..2", ".5", "5.", "* 2", "()", "2 ^", "1 + * 2", "abc"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    evaluate(text)

    def test_division_by_zero(self):
        for text in ["1 / 0", "1 / (2 - 2)", "5 / 0.0"]:
            with self.subTest(text=text):
                with self.assertRaises(ZeroDivisionError):
                    evaluate(text)
