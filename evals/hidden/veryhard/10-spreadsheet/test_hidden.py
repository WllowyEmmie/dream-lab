import unittest

from sheet import evaluate


class HiddenTest(unittest.TestCase):
    def one(self, formula, expected, **cells):
        cells = {"Z1": formula, **cells}
        with self.subTest(formula=formula):
            result = evaluate(cells)["Z1"]
            if isinstance(expected, str):
                self.assertEqual(result, expected)
            else:
                self.assertIsInstance(result, float)
                self.assertAlmostEqual(result, expected, places=9)

    def test_numbers_and_text_pass_through(self):
        self.assertEqual(evaluate({"A1": 5, "A2": 2.5, "A3": "hello", "A4": ""}), {"A1": 5.0, "A2": 2.5, "A3": "hello", "A4": ""})
        self.assertIsInstance(evaluate({"A1": 5})["A1"], float)

    def test_arithmetic(self):
        self.one("=1+2*3", 7)
        self.one("=(1+2)*3", 9)
        self.one("=10/4", 2.5)
        self.one("=8/2/2", 2)
        self.one("=1-2-3", -4)
        self.one("=-3+5", 2)
        self.one("=--3", 3)
        self.one("=2*-3", -6)
        self.one("=+4", 4)
        self.one("= 2 * ( 3 + 4 ) ", 14)
        self.one("=3.5*2", 7)

    def test_references(self):
        self.one("=A1*3+B1", 11, A1=2, B1="=A1+3")
        self.one("=Y9+1", 1)                               # a missing cell is 0
        self.one("=-A1", -2, A1=2)
        self.one("=A1+A10+A99", 111, A1=1, A10=10, A99=100)

    def test_formulas_can_come_before_what_they_use(self):
        self.assertEqual(evaluate({"C1": "=B1+1", "B1": "=A1+1", "A1": 1}), {"C1": 3.0, "B1": 2.0, "A1": 1.0})

    def test_functions(self):
        cells = dict(A1=1, A2=2, A3="=A1+A2", B1=10, B2="text", B3=30)
        self.one("=SUM(A1:A3)", 6, **cells)
        self.one("=SUM(A1:B3)", 46, **cells)
        self.one("=SUM(B3:A1)", 46, **cells)
        self.one("=SUM(A1:A2, 10, B1)", 23, **cells)
        self.one("=MIN(A1:B3)", 1, **cells)
        self.one("=MAX(A1:B3, 100)", 100, **cells)
        self.one("=COUNT(A1:B3)", 5, **cells)
        self.one("=COUNT(A1:A2, 7, C5)", 4, **cells)
        self.one("=SUM(A1:A2)*2+MAX(1,5)", 11, **cells)
        self.one("=SUM( A1 : A2 )", 3, **cells)
        self.one("=MAX(-5, -2)", -2)

    def test_functions_with_nothing_to_work_on(self):
        self.one("=SUM(C1:D4)", 0)
        self.one("=MAX(C1:D4)", 0)
        self.one("=MIN(C1:D4)", 0)
        self.one("=COUNT(C1:D4)", 0)
        self.one("=SUM(B2:B2)", 0, B2="text")

    def test_division_by_zero(self):
        self.one("=1/0", "#DIV/0!")
        self.one("=A1/B1", "#DIV/0!", A1=5)
        self.one("=1/(2-2)", "#DIV/0!")

    def test_text_used_as_a_number(self):
        self.one("=A2+1", "#VALUE!", A2="text")
        self.one("=A2", "#VALUE!", A2="text")
        self.one("=SUM(A2)", "#VALUE!", A2="text")
        self.one("=SUM(A2, 1)", "#VALUE!", A2="text")

    def test_errors_spread_to_cells_that_use_them(self):
        result = evaluate({"A1": "=1/0", "A2": "=A1+1", "A3": "=SUM(A1:A2)", "A4": 5, "B1": "=A4*2"})
        self.assertEqual(result, {"A1": "#DIV/0!", "A2": "#DIV/0!", "A3": "#DIV/0!", "A4": 5.0, "B1": 10.0})
        result = evaluate({"A1": "oops", "A2": "=A1*2", "A3": "=A2+1"})
        self.assertEqual(result, {"A1": "oops", "A2": "#VALUE!", "A3": "#VALUE!"})

    def test_cycles(self):
        self.assertEqual(evaluate({"A1": "=A1"}), {"A1": "#CYCLE!"})
        self.assertEqual(evaluate({"A1": "=B1+1", "B1": "=A1+1"}), {"A1": "#CYCLE!", "B1": "#CYCLE!"})
        result = evaluate({"A1": "=B1", "B1": "=C1", "C1": "=B1", "D1": "=A1+1", "E1": 3, "F1": "=E1+1"})
        self.assertEqual(result, {"A1": "#CYCLE!", "B1": "#CYCLE!", "C1": "#CYCLE!", "D1": "#CYCLE!", "E1": 3.0, "F1": 4.0})
        result = evaluate({"C1": "=B1", "B1": "=C1", "A1": "=SUM(B1:C1)"})
        self.assertEqual(result, {"C1": "#CYCLE!", "B1": "#CYCLE!", "A1": "#CYCLE!"})

    def test_malformed_formulas(self):
        for formula in ["=", "=1+", "=(1", "=1)", "=1 2", "=SUM(", "=SUM()", "=SUM(1,)", "=A1:B2", "=abc", "=A100",
                        "=1 $ 2", "=sum(A1)", "=a1+1", "=AVG(A1)", "=SUM(A1:)", "=1..2", "=*2"]:
            self.one(formula, "#ERROR!", A1=1, B2=2)
