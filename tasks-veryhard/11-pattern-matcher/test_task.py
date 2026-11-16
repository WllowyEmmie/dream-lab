import unittest

from pattern import matches


class TaskTest(unittest.TestCase):
    def test_whole_text_must_match(self):
        self.assertTrue(matches("ab*c", "abbbc"))
        self.assertTrue(matches("ab*c", "ac"))
        self.assertFalse(matches("ab*c", "abbbcd"))

    def test_groups_and_classes(self):
        self.assertTrue(matches("(cat|dog)s?", "dogs"))
        self.assertTrue(matches("[a-c]+\\d", "abca7"))
        self.assertFalse(matches("[^a-c]+", "xbz"))

    def test_malformed(self):
        with self.assertRaises(ValueError):
            matches("(ab", "ab")

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
