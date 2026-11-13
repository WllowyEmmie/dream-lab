import unittest

from csvline import split_line


class TaskTest(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(split_line("a,b,c"), ["a", "b", "c"])

    def test_quoted_comma(self):
        self.assertEqual(split_line('a,"b, c",d'), ["a", "b, c", "d"])

    def test_escaped_quotes(self):
        self.assertEqual(split_line('a,"b ""c"" d",e'), ["a", 'b "c" d', "e"])
        self.assertEqual(split_line('""""'), ['"'])
