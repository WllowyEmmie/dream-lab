# Match text against a pattern

Implement `matches(pattern, text)` in `pattern.py`. It returns `True` when the
**whole** of `text` matches the pattern. Write the matcher yourself: don't
import `re`, `regex`, `fnmatch` or anything else that matches patterns.

The pattern language is a subset of regular expressions:

- Any character other than `( ) [ ] | * + ? . \` matches itself.
- `.` matches any one character.
- `*`, `+` and `?` after an item mean zero or more, one or more, and zero or one
  of it. An item is a character, `.`, a class, an escape or a group.
- `( )` groups, and `|` separates alternatives. An alternative can be empty:
  `(|a)b` matches `b` and `ab`.
- `[abc]` matches one character from the class, `[a-z]` uses ranges, and `[^abc]`
  matches one character that is not in the class. A `-` first or last in a class
  is a plain `-`. A `]` closes the class unless it is escaped.
- `\d` is a digit, `\w` is a letter, digit or underscore, `\s` is a space, tab
  or newline; all ASCII. A backslash before any other character makes it match
  itself: `\.`, `\*`, `\\`, `\(`. Escapes work inside classes too.

Raise `ValueError` for a malformed pattern: unbalanced parentheses, an
unterminated or empty class, a class range that runs backwards (`[z-a]`), a
pattern that ends with a backslash, a `*`, `+` or `?` with nothing before it
to repeat, or one directly after another (`a**`).

`{`, `}`, `^` (outside a class) and `$` won't be used.

## Done when

- `python -m unittest test_task` passes in this folder.
- You didn't edit `test_task.py`.
- The code does everything this page asks for, not only what the test checks.
