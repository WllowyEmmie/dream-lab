import unittest

from lru import LRUCache


class TaskTest(unittest.TestCase):
    def test_get_counts_as_use(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        self.assertEqual(cache.get("a"), 1)
        cache.put("c", 3)
        self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(len(cache), 2)
