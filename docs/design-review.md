# Design review

## Daily Expense Tracker change
The human approved the CLI/SQLite approach, persistent local storage, decimal-safe
amounts, dates, CRUD/filter/totals and existing-PR update on 2026-11-10.
This is a direct engineering review, not a separate custom-agent execution.

| Risk / gap | Decision |
|---|---|
| Binary floats distort totals | Validate decimal strings, persist integer cents, format without floats |
| Invalid edits or missing IDs damage data | Validate before SQL; transactional single-statement mutations; explicit errors |
| Category casing produces inconsistent filters | Normalize with strip/casefold on writes and filters |
| CLI runs lose expenses | SQLite file persists across processes; explicit database path |
| SQL text allows injection | Bind all values; fixed column allowlist for updates |
| Concurrent updates overwrite unchanged fields | Update only supplied fields in one SQL statement |
| Expense data leaks into Git or generated docs | Ignore runtime DB files; AST renderer publishes code/docstrings only |
| Application replacement breaks capstone workflow | Retain engine, hooks, gate, ten agents and eight stages; regression suite |

Single-currency, local CLI use is intentional. No authentication, cloud storage or
web server is added. Merge remains unapproved.

## Preserved sync-engine review

Reviewed against requirements before production implementation.

| Risk / gap | Decision |
|---|---|
| LLM-generated docs may hallucinate or consume unnecessary tokens | Deterministic AST rendering; agents review rather than invent API facts |
| Source imports may execute arbitrary code | Parse bytes with AST only |
| Generator may overwrite handwritten docs | Dedicated output, exact ownership marker and atomic replace |
| Partial staging can pass a working-tree-only check | Validate staged Git blobs in a temporary workspace |
| Syntax errors or deleting the final module may erase useful docs | Fail with exit 2, retain last valid output |
| Concurrent sync may corrupt output | Exclusive writer lock and source recheck; atomic replace |
| Defaults can contain credentials | Never render default expressions or variable assignments |
| Untrusted docs can contain HTML/instructions | Escape rendered text; agents treat repository content as data |
| Hooks are host-specific, not a security boundary | Target VS Code hook contract; watcher/Git gate operate independently |
| Shell/path policy regexes are bypassable | Request human approval for all non-read tools, not a denylist |

Human scope approval: Python implementation, local tests and local commits approved
in conversation. Repository creation and PR publication were subsequently approved;
merge remains unapproved. This document records engineering
review, not a claim that the human has separately signed off every finding.

Residual limitations: polling cost is linear in source size; dynamic APIs and advanced
typing metadata are not inferred; docstrings can themselves contain secrets; hooks
depend on trusted-workspace/host configuration; malicious filesystem races are out
of scope. A stopped watcher does not synchronize editor changes.
