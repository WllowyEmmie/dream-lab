import re
import unittest

from pattern import matches

PATTERNS = ["abc", "a.c", "a*", "a+b?", "(ab)*", "(a|b)*c", "a|b|cd", "[abc]+", "[a-z0-9]+", "[^abc]*",
            "\\d+\\.\\d+", "\\w+\\s\\w+", "(a|ab)(c|bcd)", "(a*)*b", "x(yz|y)*z?", "[a\\-z]+", "[-a]+", "[a-]+",
            "a\\*b", "(|a)b", "((a|b)c)+", ".*foo.*", "(a+)+", "[\\d.]+", "a?a?a?aaa", "\\(x\\)", "[^\\d]+", "a|",
            "()", "(a|)+", "..", ".?", "[\\]x]+", "\\\\+", "(ab|a)(bc|c)?", "[A-Za-z_]\\w*", "\\s*a\\s*", "(.)(.)\\w"]
TEXTS = ["", "a", "b", "ab", "abc", "aab", "abab", "c", "bc", "abcd", "cd", "foo", "xfoo", "foobar", "1.5", "12.345",
         "1.", "hello world", "a*b", "ab ", "xyzz", "xyz", "xyyz", "aaa", "aaaa", "aaaaa", "a-z", "-a", "a-", "(x)", "x",
         "acbc", "abbcd", "..", "5", "a1", "A", "_x9", " a ", "]x", "\\\\", "ac", "abbc"]


class HiddenTest(unittest.TestCase):
    def test_agrees_with_real_regular_expressions(self):
        for pattern in PATTERNS:
            for text in TEXTS:
                with self.subTest(pattern=pattern, text=text):
                    self.assertEqual(matches(pattern, text), re.fullmatch(pattern, text, re.ASCII) is not None)

    def test_returns_a_bool(self):
        self.assertIs(matches("a", "a"), True)
        self.assertIs(matches("a", "b"), False)

    def test_longer_text(self):
        self.assertTrue(matches("(ab|cd)*e", "abcdab" * 3 + "e"))
        self.assertFalse(matches("(ab|cd)*e", "abcdab" * 3 + "f"))
        self.assertTrue(matches("[a-z]+@[a-z]+\\.(com|ng)", "emmie@example.ng"))

    def test_malformed_patterns(self):
        for pattern in ["(a", "a)", "((a)", "*a", "a**", "a+*", "a?+", "[abc", "[]", "[^]", "a\\", "(*a)", "[z-a]",
                        "+", "a|*", "(|+)"]:
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValueError):
                    matches(pattern, "a")

    def test_does_not_use_a_regex_library(self):
        import ast
        tree = ast.parse(open("pattern.py", encoding="utf-8").read())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add((node.module or "").split(".")[0])
        self.assertFalse(names & {"re", "regex", "fnmatch", "sre_compile", "sre_parse"})
