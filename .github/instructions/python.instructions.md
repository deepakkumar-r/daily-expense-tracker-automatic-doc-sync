---
description: "Use when implementing or testing the Daily Expense Tracker, AST documentation-sync engine and hooks."
applyTo: "src/**/*.py,tests/**/*.py"
---
- Standard library, Python 3.11+, typed interfaces and pathlib.
- The documentation engine parses source using ast; never import or execute source being documented.
- Render sorted, deterministic output; omit default expressions and variable values.
- Reject unsafe paths and malformed input; preserve last valid output on failure.
- Write only owned generated output, atomically, with a cooperating-writer lock.
- Test behavior in temporary workspaces; never mutate the real source for tests.
- Expense amounts use validated decimal strings and integer cents, never floats.
- Bind SQL values; validate dates/categories and surface missing IDs/database errors.
- Keep expense databases isolated in tests; preserve the existing sync automation.
