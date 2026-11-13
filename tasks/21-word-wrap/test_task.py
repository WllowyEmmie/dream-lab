import unittest

from wrap import wrap


class TaskTest(unittest.TestCase):
    def test_width_respected(self):
        self.assertEqual(wrap("the quick brown fox", 8), ["the", "quick", "brown", "fox"])
        self.assertEqual(wrap("the quick brown fox", 9), ["the quick", "brown fox"])

    def test_long_word_alone(self):
        self.assertEqual(wrap("a extraordinarily b", 5), ["a", "extraordinarily", "b"])
