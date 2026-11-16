# Apply a JSON Patch

Implement `apply_patch(doc, patch)` in `jsonpatch.py`. It applies a JSON Patch
(RFC 6902) to a document made of dicts, lists, strings, numbers, booleans and
`None`, and returns the new document. `doc` and `patch` are never modified, and
if any operation fails the function raises `PatchError` (defined in the module).

`patch` is a list of operations, applied in order. Each is a dict with `op`,
`path`, and depending on the op, `value` or `from`:

- `add`: set an object member (replacing one that exists), or insert into an
  array before the given index. The index may equal the array's length, and `-`
  means the end. With path `""` the value replaces the whole document.
- `remove`: remove the member or element. It must exist.
- `replace`: like `add`, but the target must already exist. On an array it
  replaces the element at that index.
- `move`: remove the value at `from` and add it at `path`. A value can't be moved
  into one of its own children.
- `copy`: add a copy of the value at `from` at `path`.
- `test`: the value at `path` must equal `value`, compared the way JSON would:
  `1` equals `1.0`, but `true` doesn't equal `1`, and member order in objects
  doesn't matter.

Paths are JSON Pointers (RFC 6901): `""` is the whole document, otherwise
`/`-separated tokens. In a token `~1` means `/` and `~0` means `~`. Array
indexes are digits with no leading zeros (`0` is fine, `01` isn't). `-` is only
allowed as the last token of an `add` path (or the `path` of a move or copy).

Raise `PatchError` for: a path that doesn't exist, a bad or out-of-range index,
a failed `test`, an unknown `op`, a missing `op`, `path`, `value` or `from`, and
a path that isn't `""` and doesn't start with `/`.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
