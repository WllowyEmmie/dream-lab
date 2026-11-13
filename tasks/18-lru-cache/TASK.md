# LRU cache evicts an item that was just used

With capacity 2: put a, put b, get a, put c. The cache drops a, but b was the least recently used.

## Done when

- `python -m unittest` passes in this folder.
- You didn't edit `test_task.py`.
