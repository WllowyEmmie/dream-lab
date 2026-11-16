import unittest

from jsonpatch import PatchError, apply_patch


class TaskTest(unittest.TestCase):
    def test_add_replace_remove(self):
        doc = {"name": "Ade", "tags": ["a", "b"]}
        patch = [
            {"op": "add", "path": "/age", "value": 30},
            {"op": "replace", "path": "/name", "value": "Bola"},
            {"op": "remove", "path": "/tags/0"},
        ]
        self.assertEqual(apply_patch(doc, patch), {"name": "Bola", "tags": ["b"], "age": 30})
        self.assertEqual(doc, {"name": "Ade", "tags": ["a", "b"]})

    def test_missing_path(self):
        with self.assertRaises(PatchError):
            apply_patch({"a": 1}, [{"op": "remove", "path": "/b"}])
