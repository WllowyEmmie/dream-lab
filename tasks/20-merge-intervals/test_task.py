import unittest

from intervals import merge


class TaskTest(unittest.TestCase):
    def test_merge(self):
        self.assertEqual(merge([(1, 2), (2, 3)]), [(1, 3)])
        self.assertEqual(merge([(5, 8), (1, 3), (2, 4)]), [(1, 4), (5, 8)])
        self.assertEqual(merge([(1, 10), (2, 3)]), [(1, 10)])
        self.assertEqual(merge([]), [])
