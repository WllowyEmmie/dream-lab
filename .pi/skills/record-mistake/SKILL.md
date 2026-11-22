---
name: record-mistake
description: Use before finishing a task to save what it taught about this repo, after fixing a bug or failing test, or when a memory note contradicts the code.
---
Append lines to memory/inbox.md, one per item, in these forms:

- RULE: <a general rule for this repo, true beyond this task> (learned in <task>)
- MISTAKE: <what went wrong> | FIX: <what fixed it> | FILE: <path>
- CONTRADICTION: <the note> | CODE SAYS: <what the code actually does> | FILE: <path>
- NOTE: <anything else reusable, in one line>

Write a RULE whenever a task states or reveals how the repo works: a business
rule, a format, a rounding or time rule, a command. State it so a later task can
apply it without knowing this one, for example
"RULE: VAT always rounds up to the next kobo (learned in 01-vat-rounding)",
not "In task 01 the spec said VAT rounds up".

Append only. Don't edit or remove other lines, and don't touch any other memory file.
