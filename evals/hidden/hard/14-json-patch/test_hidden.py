import unittest

from jsonpatch import PatchError, apply_patch


class HiddenTest(unittest.TestCase):
    def ok(self, doc, patch, expected):
        self.assertEqual(apply_patch(doc, patch), expected)

    def bad(self, doc, patch):
        with self.assertRaises(PatchError):
            apply_patch(doc, patch)

    def test_add_to_object(self):
        self.ok({"a": 1}, [{"op": "add", "path": "/b", "value": [1, 2]}], {"a": 1, "b": [1, 2]})
        self.ok({"a": 1}, [{"op": "add", "path": "/a", "value": 2}], {"a": 2})
        self.ok({"a": {"b": {}}}, [{"op": "add", "path": "/a/b/c", "value": None}], {"a": {"b": {"c": None}}})

    def test_add_to_array(self):
        self.ok({"x": [1, 3]}, [{"op": "add", "path": "/x/1", "value": 2}], {"x": [1, 2, 3]})
        self.ok({"x": [1, 2]}, [{"op": "add", "path": "/x/-", "value": 3}], {"x": [1, 2, 3]})
        self.ok({"x": [1, 2]}, [{"op": "add", "path": "/x/2", "value": 3}], {"x": [1, 2, 3]})
        self.ok([], [{"op": "add", "path": "/0", "value": "a"}], ["a"])
        self.bad({"x": [1, 2]}, [{"op": "add", "path": "/x/3", "value": 9}])
        self.bad({"x": [1, 2]}, [{"op": "add", "path": "/x/01", "value": 9}])
        self.bad({"x": [1, 2]}, [{"op": "add", "path": "/x/one", "value": 9}])

    def test_add_needs_an_existing_parent(self):
        self.bad({"a": 1}, [{"op": "add", "path": "/b/c", "value": 1}])
        self.bad({"a": 1}, [{"op": "add", "path": "/a/c", "value": 1}])

    def test_whole_document(self):
        self.ok({"a": 1}, [{"op": "add", "path": "", "value": [1]}], [1])
        self.ok({"a": 1}, [{"op": "replace", "path": "", "value": "x"}], "x")
        self.ok({"a": 1}, [{"op": "test", "path": "", "value": {"a": 1}}], {"a": 1})

    def test_remove(self):
        self.ok({"a": 1, "b": 2}, [{"op": "remove", "path": "/a"}], {"b": 2})
        self.ok({"x": [1, 2, 3]}, [{"op": "remove", "path": "/x/1"}], {"x": [1, 3]})
        self.bad({"x": [1, 2, 3]}, [{"op": "remove", "path": "/x/3"}])
        self.bad({"x": [1, 2, 3]}, [{"op": "remove", "path": "/x/-"}])
        self.bad({"a": 1}, [{"op": "remove", "path": "/a/b"}])

    def test_replace(self):
        self.ok({"x": [1, 2, 3]}, [{"op": "replace", "path": "/x/1", "value": "b"}], {"x": [1, "b", 3]})
        self.bad({"a": 1}, [{"op": "replace", "path": "/b", "value": 2}])
        self.bad({"x": [1]}, [{"op": "replace", "path": "/x/1", "value": 2}])
        self.bad({"x": [1]}, [{"op": "replace", "path": "/x/-", "value": 2}])

    def test_move(self):
        self.ok({"a": {"b": 1}, "c": {}}, [{"op": "move", "from": "/a/b", "path": "/c/d"}], {"a": {}, "c": {"d": 1}})
        self.ok({"x": [1, 2, 3]}, [{"op": "move", "from": "/x/0", "path": "/x/2"}], {"x": [2, 3, 1]})
        self.ok({"x": [1, 2, 3]}, [{"op": "move", "from": "/x/0", "path": "/x/-"}], {"x": [2, 3, 1]})
        self.bad({"a": {"b": 1}}, [{"op": "move", "from": "/a", "path": "/a/b"}])
        self.bad({"a": 1}, [{"op": "move", "from": "/nope", "path": "/b"}])

    def test_copy(self):
        result = apply_patch({"a": {"b": [1]}}, [{"op": "copy", "from": "/a", "path": "/c"},
                                                 {"op": "add", "path": "/c/b/-", "value": 2}])
        self.assertEqual(result, {"a": {"b": [1]}, "c": {"b": [1, 2]}})
        self.bad({"a": 1}, [{"op": "copy", "from": "/nope", "path": "/b"}])

    def test_test(self):
        doc = {"n": 1, "t": True, "o": {"a": 1, "b": [1, 2]}, "s": "x", "z": None}
        self.ok(doc, [{"op": "test", "path": "/n", "value": 1.0}], doc)
        self.ok(doc, [{"op": "test", "path": "/o", "value": {"b": [1, 2], "a": 1}}], doc)
        self.ok(doc, [{"op": "test", "path": "/z", "value": None}], doc)
        self.bad(doc, [{"op": "test", "path": "/t", "value": 1}])
        self.bad(doc, [{"op": "test", "path": "/n", "value": True}])
        self.bad(doc, [{"op": "test", "path": "/o/b", "value": [2, 1]}])
        self.bad(doc, [{"op": "test", "path": "/s", "value": "y"}])
        self.bad(doc, [{"op": "test", "path": "/o/b", "value": [1, True]}])
        self.bad(doc, [{"op": "test", "path": "/missing", "value": None}])

    def test_pointer_escapes(self):
        doc = {"a/b": 1, "m~n": 2, "": 3, " ": 4}
        self.ok(doc, [{"op": "replace", "path": "/a~1b", "value": 10}], {"a/b": 10, "m~n": 2, "": 3, " ": 4})
        self.ok(doc, [{"op": "replace", "path": "/m~0n", "value": 20}], {"a/b": 1, "m~n": 20, "": 3, " ": 4})
        self.ok(doc, [{"op": "replace", "path": "/", "value": 30}], {"a/b": 1, "m~n": 2, "": 30, " ": 4})
        self.ok({"~1": "x"}, [{"op": "test", "path": "/~01", "value": "x"}], {"~1": "x"})

    def test_operations_apply_in_order(self):
        patch = [{"op": "add", "path": "/list", "value": []},
                 {"op": "add", "path": "/list/-", "value": 1},
                 {"op": "copy", "from": "/list/0", "path": "/first"},
                 {"op": "test", "path": "/first", "value": 1},
                 {"op": "remove", "path": "/list"}]
        self.ok({}, patch, {"first": 1})

    def test_failure_leaves_the_input_alone(self):
        doc = {"a": [1, 2]}
        patch = [{"op": "add", "path": "/a/-", "value": 3}, {"op": "test", "path": "/a/0", "value": 99}]
        self.bad(doc, patch)
        self.assertEqual(doc, {"a": [1, 2]})

    def test_inputs_are_not_modified_or_shared(self):
        doc = {"a": [1]}
        value = {"k": [1]}
        patch = [{"op": "add", "path": "/b", "value": value}]
        result = apply_patch(doc, patch)
        result["b"]["k"].append(2)
        result["a"].append(2)
        self.assertEqual((doc, value), ({"a": [1]}, {"k": [1]}))

    def test_malformed_operations(self):
        self.bad({}, [{"op": "frobnicate", "path": "/a"}])
        self.bad({}, [{"path": "/a", "value": 1}])
        self.bad({}, [{"op": "add", "value": 1}])
        self.bad({}, [{"op": "add", "path": "/a"}])
        self.bad({"a": 1}, [{"op": "move", "path": "/b"}])
        self.bad({"a": 1}, [{"op": "replace", "path": "a", "value": 2}])
