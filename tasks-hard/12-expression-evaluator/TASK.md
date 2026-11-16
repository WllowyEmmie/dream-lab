# Evaluate arithmetic expressions

Implement `evaluate(text)` in `calc.py`. It works out an arithmetic expression
given as a string and returns a `float`. Don't use `eval`.

- **Numbers** are digits, optionally followed by a point and more digits: `3`,
  `3.25`. `.5` and `5.` are not numbers.
- **Operators**, from lowest to highest precedence:
  1. `+` and `-` (left to right)
  2. `*` and `/` (left to right)
  3. unary `-` and `+`, which may repeat: `--2` is `2`
  4. `^` for powers, right to left: `2^3^2` is `2^(3^2)`
- `^` binds tighter than a unary minus on its left, so `-2^2` is `-4`. The
  exponent may itself start with a unary operator: `2^-1` is `0.5`.
- **Parentheses** group as usual. Spaces between tokens are ignored.
- Anything malformed raises `ValueError`: an empty string, unbalanced
  parentheses, a missing operand, two numbers in a row, an unknown character.
- Dividing by zero raises `ZeroDivisionError`.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
