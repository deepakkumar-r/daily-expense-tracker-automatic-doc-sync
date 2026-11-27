# Code review

## Daily Expense Tracker migration - 2026-11-10
Direct engineering review, not an independently executed custom agent or
vulnerability scan. Original review evidence below remains historical.

| Area | Assessment |
|---|---|
| Correctness | Stable autoincrement IDs, date/ID sorting, supplied-field-only updates, normalized category queries and Python integer-cent totals |
| Security | All expense SQL values are bound; update columns are fixed; runtime data excluded from Git; no network or new packages |
| Error handling | Validation precedes mutation; missing IDs raise; transactions roll back; CLI surfaces SQLite/filesystem errors with exit 2 |
| Test coverage | Isolated API and real subprocess CLI tests cover persistence, CRUD, exact/empty totals, Unicode categories, invalid dates/text/amounts/IDs and database failures |
| Code clarity | One small application module with typed record, service and CLI; existing infrastructure unchanged |
| DRY | CLI calls the same validated service; totals reuse filtered views; one connection/transaction helper |
| Dependency safety | Python 3.11+ standard library only; no installation or dependency changes |

During focused verification a test-owned SQLite connection was not closed by
SQLite's transaction context manager. Explicit `contextlib.closing` fixes Windows
temporary-file cleanup. Application connections already used explicit closure.
Full verification and skips are recorded in [test report](test-report.md).
Human review/merge and actual Copilot-host discovery remain separate gates.

## Original infrastructure review

Direct engineering review of the implementation and tests against the brief.
This is not a claim of an independently executed custom-agent review.

| Area | Assessment / evidence |
|---|---|
| Correctness | AST declaration selection, defaults, sorting, fingerprint, add/rename/delete and no-op behavior covered by tests |
| Security | No source execution or third-party runtime packages; escaped docstrings, omitted literal defaults, safe output ownership |
| Error handling | Missing/empty source, bad encoding/syntax, lock conflict, traversal errors and replace failure surface errors and preserve output |
| Test coverage | Unit and integration tests for engine, real watcher and hook adapter; staged blobs tested with real Git test conditional on availability |
| Code clarity | Small CLI modules with explicit names/types, no hidden network/service dependency |
| DRY | CLI, watcher, Copilot hook and staged gate reuse the same snapshot/renderer/check contracts |
| Dependency safety | Standard-library runtime only; no third-party version audit required; no claim of a vulnerability scan |

Issues resolved during review:
1. `os.walk` errors must propagate rather than silently omit unreadable source.
2. Path-based write allowlists are brittle; ask approval for every non-read tool.
3. Git hook failures may use stdout; preserve that diagnostic if stderr is empty.
4. Reject non-regular staged entries even when their names lack a Python suffix.
5. Normalize the POSIX hook and initial Python source to LF so shell execution and
   staged fingerprints remain consistent with Git attributes.
6. Wait for watcher completion notifications before reading an output being
   replaced on Windows; verify the integration test with 20 repeated executions.

Real Git/hook integration now passes, including partial staging and blocked commits.
Moved prompts were restored without deleting user-added skills; broken links and
the change manifest were corrected and contract tests pass.
Remaining constraints: host-side Copilot agent loading/delegation and Windows
symlink integration require a supported environment. See test-report.md for evidence.
Merge approval is not represented by this review.
