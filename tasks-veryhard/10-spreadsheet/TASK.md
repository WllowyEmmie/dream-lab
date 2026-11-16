# Evaluate a small spreadsheet

Implement `evaluate(cells)` in `sheet.py`. `cells` maps cell names like `"A1"`
to values, and the result maps the same names to what each cell shows.

A cell name is one upper-case letter and a row from 1 to 99. A value is:

- a number: shown as a `float`
- a string starting with `=`: a formula, shown as its result (a `float`) or an
  error code
- any other string: text, shown unchanged

**Formulas** may use numbers (`3`, `3.25`), cell references (`B2`), `+ - * /`,
unary minus and plus, parentheses, and the functions `SUM`, `MIN`, `MAX` and
`COUNT`. Usual precedence; spaces are ignored. Function and cell names are
upper-case only.

- A reference to a cell that isn't in `cells` is `0`.
- Function arguments are separated by commas. Each is an expression or a range
  like `A1:B3`, which covers the whole rectangle (`B3:A1` is the same range). A
  range skips cells that are missing or hold text. A function needs at least one
  argument. `SUM`, `MIN` and `MAX` of no values is `0`. `COUNT` counts how many
  numeric values its arguments give.
- A range is only allowed as a function argument.

**Errors** are shown as strings:

- `#DIV/0!`: division by zero.
- `#VALUE!`: a text cell used as a number. That includes a bare reference
  (`=A2` where A2 holds text) and a single reference passed to a function
  (`=SUM(A2)`); only ranges skip text.
- `#CYCLE!`: the cell depends on itself, directly or through other cells.
- `#ERROR!`: the formula is malformed.
- A formula that uses a cell showing an error shows that same error. This
  includes cells that depend on a cycle without being part of it, and ranges
  that contain an error cell.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
