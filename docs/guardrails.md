# Guardrails and human approval

| Boundary | Mechanism | Failure / approval behavior |
|---|---|---|
| Story scope | Requirements and coordinator instructions | Exactly US-001; ask before scope changes |
| Implementation | Explicit human scope/design decision | Do not begin on unresolved decisions |
| Tool use | PreToolUse validates JSON and allows known read tools only | Ask for every write, command and unknown tool; malformed input denies |
| Policy changes | Same non-read approval gate | Hooks/instructions are not self-approved |
| Source trust | AST parsing, no imports/eval/exec | Repository/docstring instructions are untrusted data |
| Generated output | Marker, safe-path checks, lock and atomic replace | Refuse foreign output; preserve last valid docs on failure |
| Credentials | No network or configuration-secret reads in engine | Omit defaults/assignments; human reviews public docstrings |
| Staging | Pre-commit checks isolated index blobs | Fail if staged docs differ from staged source; never auto-stage |
| Publication | Agent instruction and tool approval | Separate permission for commit, push/create-PR and merge |
| Evidence | Executed tests, explicit skips | No guessed results, invented approvals or success-shaped fallbacks |

The human approved switching to Python, local initialization/commits and a Git
installation attempt. They subsequently approved public repository creation and PR
publication for `deepakkumar-r/automated-documentation-sync`. Merge is not approved.
Approval is recorded in conversation, not minted by an agent-written file.

Limitations: hooks require a supporting trusted host and can be disabled by the user.
They are defense in depth, not OS isolation or an authorization service. The read-tool
allowlist relies on host tool identity. Source/output directories must be trusted
against hostile concurrent filesystem replacement. This pipeline does not guarantee
secret detection in intentionally published docstrings.

All supported operational errors are reported with nonzero exit status; the watcher
reports recoverable errors and keeps running. A stale `.docsync.lock` is not deleted
automatically. Inspect its PID and verify no sync process owns it before removal.
Do not bypass a failing gate or use `--no-verify` to complete the capstone.
