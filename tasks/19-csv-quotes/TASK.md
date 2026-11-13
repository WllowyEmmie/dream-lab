# Quoted CSV fields lose their quote marks

split_line('a,"b ""c"" d",e') should give ['a', 'b "c" d', 'e']. In CSV, "" inside quotes means one " character, but it gets dropped.

## Done when

- `python -m unittest` passes in this folder.
- You didn't edit `test_task.py`.
