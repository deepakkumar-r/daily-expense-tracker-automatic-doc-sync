# Test report

## New-repository publication verification - 2026-11-10
The human approved publishing the current workspace, including website/UI changes,
to a new public repository with a feature-branch PR and no merge.

Command: `python -m unittest discover -s tests -v`, exit 0:
```text
Ran 81 tests in 16.915s

OK (skipped=1)
```
80 passed, one existing Windows symlink-privilege skip; no failures/errors.
Command: `python src/docsync.py check`, exit 0:
```text
Documentation is current
```
This rerun validates the current website, CLI and automation before publication.
Historical sections below retain their original delivery claims and limitations.
The first staged-index check caught CRLF/LF fingerprint drift in the new source.
Normalize the new Python/frontend files to the repository LF convention and
regenerate both references with the sync engine. Final command
`python src/git_gate.py`, exit 0: `Staged documentation is current`.

Publication is blocked: repeated `gh repo create` requests failed with
`error connecting to api.github.com`; DNS diagnostics also reported resolution
failures. No new repository/PR creation or remote push is claimed. Original
remote configuration and all main branches remain unchanged.

## Website and multi-source documentation extension - 2026-11-10
The same US-001 now includes a plain HTML/CSS/JavaScript website and local HTTP
adapter. No production deployment, database migration, package installation,
commit, push or remote PR update was performed for this extension.

Command: `python -m unittest discover -s tests -v`, exit 0.
Verbatim final summary:
```text
Ran 81 tests in 16.606s

OK (skipped=1)
```
80 passed, 1 skipped, 0 failures/errors. The existing real OS symlink test skips
with WinError 1314; controlled source/asset/output symlink rejection checks pass.
The suite includes ten loopback HTTP integration tests, nine frontend sync tests
and a Python runner executing ten JavaScript controller checks. All original
CLI/SQLite, AST, automation, customization and real Git/pre-commit tests pass.

Command: `node --test tests\frontend.test.js`, exit 0.
Verbatim summary:
```text
tests 10
suites 0
pass 10
fail 0
cancelled 0
skipped 0
todo 0
duration_ms 126.5633
```
These are actual JavaScript controller tests with a small DOM test double, not
claims of a browser layout/accessibility audit. Browser-tool discovery was denied
by the approval hook; real browser visual/responsive validation was not executed.
Node is optional test tooling; the application needs only Python and a browser.

Commands: `python src\docsync.py sync` and `python src\docsync.py check`, exit 0:
```text
Documentation unchanged
Documentation is current
```
The unchanged second synchronization validates no-op output. Both generated
references are written only by the sync engine. `node --check src\static\app.js`
and `git diff --check` also returned exit 0 (Git reported existing Markdown
working-tree CRLF normalization warnings, not whitespace failures).

| Criteria | Executed evidence |
|---|---|
| AC14 | JS controller CRUD/add/edit/delete-confirmation, filters/reset, exact summary/chart rendering, empty/error/retry states, safe text rendering, stale-response rejection, BigInt precision above Number's safe range |
| AC15 | Real loopback HTTP CRUD and shared CLI persistence, Unicode filters, monthly/category/daily summary agreement, empty results, decimal string serialization, invalid/missing fields, missing IDs, denied cross-origin/Host requests, oversized/malformed bodies, storage failures, static allowlist and response headers |
| AC16 | HTML/CSS/JS add/edit/rename/delete and final removal, independent Python/UI fingerprints, unchanged mtimes, missing descriptions, escaped metadata, no field-value publication, UTF-8/ownership/symlink failures preserving good output, live watcher deadlines, PostToolUse sync and real partially staged frontend drift rejection |

The initial focused run failed (20 tests, 7.536s, one failure/two errors): the new
test expected an unprefixed CLI total and called assert_called on its patch rather
than the started mock; both test assumptions were corrected without changing the
CLI. It also exposed Windows resetting oversized-body connections before the
error arrived. The HTTP adapter now drains the bounded declared oversized body
in chunks before returning its explicit error. The passing full run above
includes those repairs.

## Daily Expense Tracker migration - 2026-11-10
Historical CLI migration evidence; the website extension above is current.
Environment verified: Windows, Python 3.15.2, Git 2.56.0.windows.4,
GitHub CLI 2.103.3. Target remains Python 3.11+ standard library only; no
additional interpreter, dependency installation or CI execution is claimed.

Command: `python -m unittest discover -s tests -v`, exit 0.
Verbatim final summary:
```text
Ran 61 tests in 7.287s

OK (skipped=1)
```
60 passed, 1 skipped, 0 failures/errors. All 17 new expense tests passed.
The existing OS symlink test skips because Windows reports WinError 1314
(symlink creation privilege unavailable); controlled symlink rejection tests pass.

Command: `python src/docsync.py check`, exit 0:
```text
Documentation is current
```
Command: `python src/docsync.py sync`, exit 0:
```text
Documentation unchanged
```
The unchanged second sync confirms the generated expense reference is current.

After final agent discovery descriptions were updated, command
`python -m unittest discover -s tests -p test_customizations.py -v`, exit 0:
```text
Ran 9 tests in 0.055s

OK
```
The following `python src/docsync.py check` also returned exit 0 and
`Documentation is current`. All source/test files additionally parsed with
`ast.parse(..., feature_version=(3, 11))`; this is syntax validation, not a
claim of execution on a Python 3.11 interpreter.

The first real-index gate found CRLF in the new Python files, while Git attributes
stage LF. Normalize those files to the existing LF convention, regenerate the
reference using the engine and stage matching source/output. Final command
`python src/git_gate.py`, exit 0:
```text
Staged documentation is current
```
The following drift check returned `Documentation is current`, exit 0.
The installed pre-commit gate remains enabled at `.github/hooks`; no hooks are
bypassed. Original engine/adapters, hook configuration and Git attributes are unchanged.

| Criteria | Executed evidence |
|---|---|
| AC1 | Add/default date, stable IDs, SQLite persistence across service instances and real CLI processes |
| AC2 | Date/ID ordering, individual/all-field updates, preserved unspecified values, deletion and missing IDs |
| AC3 | `0.10 + 0.20 = 0.30`, combined/filtered/empty totals, Unicode casefold and exact category matching |
| AC4-5 | Boundaries, invalid decimal/date/text/ID input, no-field updates, CLI help/errors, damaged/missing database paths, no mutation on invalid updates |
| AC6-10 | Existing AST/sync/no-op/watcher/hook/failure tests, real staged-index partial-staging/pre-commit tests |
| AC11 | Exactly ten names, tool boundaries, allowlist/handoffs, eight stages, instructions/skills/prompts |
| AC12 | Generated descriptions/fingerprint, all Markdown links, application scope and preserved infrastructure |
| AC13 | Required PR sections and complete file manifest; remote delivery verified separately |

Two earlier failures were repaired, not counted as successes: the focused
expense run exposed a test-owned unclosed SQLite connection during Windows
cleanup; the first full run exposed an architecture title missing the application
name. Explicit connection closure and the corrected title precede the passing
run above. Existing application connections already closed correctly.

Direct review is recorded in [code review](code-review.md). Tests establish
local contracts, not actual VS Code host discovery/delegation of all agents.
No new PR or merge is permitted. The human approved committing/pushing this
migration to the existing `capstone/us-001` branch and PR #1.

## Historical infrastructure evidence

## Environment
Windows; Python 3.15.2. Runtime target is Python 3.11+; only the installed interpreter
is validated in this session. No third-party runtime/test packages.

## Final execution evidence
Date: 2026-11-08. Command: `python -m unittest discover -s tests -v`, exit 0.
Verbatim final summary:
```text
Ran 43 tests in 3.901s

OK (skipped=1)
```

42 passed, 1 skipped, 0 failures/errors. The skip is listed below.
Real Git partial-staging rejection and the installed pre-commit gate both passed.
Git 2.56.0.windows.4 and GitHub CLI 2.103.3 are now available.

Command: `python src/docsync.py check`, exit 0:
```text
Documentation is current
```

Command: `python src/docsync.py sync`, exit 0:
```text
Documentation unchanged
```

The live watcher recovery test was additionally executed 20 times in one
`unittest.TestSuite`, exit 0:
```text
Ran 20 tests in 1.967s

OK
```
Each run uses real temporary source edits, a 0.02-second poll interval and a
3-second deadline for initial synchronization, error reporting and recovery.
The test waits for completion notifications before reading output, avoiding a
Windows file-sharing race while atomic replacement is still completing.

## Coverage against the story
| Criteria | Executed checks |
|---|---|
| AC1 | Public/async APIs, parameter kinds, missing descriptions, escaping and no source execution |
| AC2 | Determinism, fingerprint changes, nested add/rename/delete, no-op mtime and tampered-output repair |
| AC3 | Real watcher edit/recovery integration and post-hook synchronization |
| AC4 | Invalid syntax/encoding, missing/empty source, foreign docs, lock/replace failures and symlink guard paths |
| AC5 | CLI exit codes, isolated staged-blob matching/drift and real Git pre-commit/partial-staging integration |
| AC6 | Exactly ten agent names, coordinator allowlist, handoffs, scopes, skills/prompts, hook commands and eight stages |
| AC7 | Generated content quality, descriptions, fingerprint and all Markdown link targets |
| AC8 | Required PR sections and complete change manifest; no claim of publication |

## Corrections during verification
- The initial hook contract check caught CRLF in the POSIX pre-commit entry.
  Normalize it and Python source to LF; Git attributes preserve source fingerprints.
- A watcher test initially read output before the writer's completion notification.
  Synchronize on that notification; the subsequent 20-repeat run passed.
- Earlier failed runs are superseded by the final passing run above, not concealed
  as successes.
- The November 8 run found user-moved prompts, broken skill links and an outdated
  PR manifest. Preserve those skills, correct their links, restore agent-targeted
  prompts and update the manifest. All contract checks pass after repair.

## Limitations
- Windows lacks symlink-creation privilege: real symlink integration skipped;
  rejection paths are still unit-tested with controlled filesystem probes.
- VS Code host agent discovery/handoffs/hooks have not been exercised in this
  build session. Hook adapter JSON and actual post-edit sync are tested locally.
- No remote repository, PR, merge or approval has been invented.
- Earlier Git installation errors are resolved: the real Git test creates and
  commits temporary repositories and verifies rejection of stale staged docs.
- Frontmatter tests validate this project's constrained field/array layout and
  target references; they are not a full YAML parser or host compatibility test.

## Delivery verification
2026-11-08: `gh repo view` verified the public repository and default branch `main`.
`gh pr view` verified [PR #1](https://github.com/deepakkumar-r/automated-documentation-sync/pull/1)
is OPEN, non-draft and MERGEABLE, with head `capstone/us-001` and base `main`.
Local initialization, requirements checkpoint and implementation commits completed.
`python src/git_gate.py` and the installed pre-commit hook reported
`Staged documentation is current` before the implementation commit.
No merge performed; human review and supported-host agent acceptance remain pending.

## Showcase readiness audit - 2026-11-08

This audit supersedes the earlier run for current local test status, without
discarding historical evidence. Implementation and local automation are suitable
for a technical demonstration. Full agentic SDLC completion is not yet verified.
No agent configuration, implementation, policy or remote state was changed.

### Executed local verification

Interpreter command: `python --version`, output `Python 3.15.2`.
Command: `python -m unittest discover -s tests -v`, exit 0.
Runner runtime: 4.362 seconds; measured command-block elapsed time: 4.742 seconds
(includes the interpreter-version probe). Exact test output:

```text
test_invalid_input_fails_closed (test_automation.HookTests.test_invalid_input_fails_closed) ... ok
test_post_hook_actually_syncs_source_edits (test_automation.HookTests.test_post_hook_actually_syncs_source_edits) ... ok
test_post_hook_blocks_on_invalid_source (test_automation.HookTests.test_post_hook_blocks_on_invalid_source) ... ok
test_post_hook_ignores_untrusted_cwd_and_commands (test_automation.HookTests.test_post_hook_ignores_untrusted_cwd_and_commands) ... ok
test_reads_allowed_and_all_writes_execution_unknown_require_approval (test_automation.HookTests.test_reads_allowed_and_all_writes_execution_unknown_require_approval) ... ok
test_git_command_errors_are_reported (test_automation.IndexTests.test_git_command_errors_are_reported) ... ok
test_git_hook_stdout_failure_is_reported (test_automation.IndexTests.test_git_hook_stdout_failure_is_reported) ... ok
test_no_staged_source_fails_explicitly (test_automation.IndexTests.test_no_staged_source_fails_explicitly) ... ok
test_staged_missing_output_is_drift (test_automation.IndexTests.test_staged_missing_output_is_drift) ... ok
test_staged_snapshot_passes_and_drift_fails_without_git_binary (test_automation.IndexTests.test_staged_snapshot_passes_and_drift_fails_without_git_binary) ... ok
test_unsafe_conflicted_and_symlink_entries_fail (test_automation.IndexTests.test_unsafe_conflicted_and_symlink_entries_fail) ... ok
test_partial_staging_and_installed_precommit_gate (test_automation.RealGitTests.test_partial_staging_and_installed_precommit_gate) ... ok
test_deliverables_one_story_and_diagrams (test_customizations.CustomizationTests.test_deliverables_one_story_and_diagrams) ... ok
test_exactly_ten_agents_and_resolvable_handoffs (test_customizations.CustomizationTests.test_exactly_ten_agents_and_resolvable_handoffs) ... ok
test_generated_reference_content_quality (test_customizations.CustomizationTests.test_generated_reference_content_quality) ... ok
test_hook_contract_and_commands (test_customizations.CustomizationTests.test_hook_contract_and_commands) ... ok
test_markdown_relative_links_resolve (test_customizations.CustomizationTests.test_markdown_relative_links_resolve) ... ok
test_orchestrator_allowlist_and_readonly_review (test_customizations.CustomizationTests.test_orchestrator_allowlist_and_readonly_review) ... ok
test_pr_sections_and_file_manifest (test_customizations.CustomizationTests.test_pr_sections_and_file_manifest) ... ok
test_skills_prompts_and_scoped_instructions (test_customizations.CustomizationTests.test_skills_prompts_and_scoped_instructions) ... ok
test_cli_exit_codes (test_docsync.SyncTests.test_cli_exit_codes) ... ok
test_cli_subprocess_from_another_working_directory (test_docsync.SyncTests.test_cli_subprocess_from_another_working_directory) ... ok
test_declared_encoding_is_supported (test_docsync.SyncTests.test_declared_encoding_is_supported) ... ok
test_directory_scan_errors_are_not_ignored (test_docsync.SyncTests.test_directory_scan_errors_are_not_ignored) ... ok
test_empty_source_preserves_output (test_docsync.SyncTests.test_empty_source_preserves_output) ... ok
test_idempotent_sync_preserves_mtime_and_handwritten_docs (test_docsync.SyncTests.test_idempotent_sync_preserves_mtime_and_handwritten_docs) ... ok
test_invalid_source_preserves_output_and_cleans_lock (test_docsync.SyncTests.test_invalid_source_preserves_output_and_cleans_lock) ... ok
test_invalid_watch_intervals (test_docsync.SyncTests.test_invalid_watch_intervals) ... ok
test_keyword_only_separator (test_docsync.SyncTests.test_keyword_only_separator) ... ok
test_live_watcher_updates_and_recovers_within_deadline (test_docsync.SyncTests.test_live_watcher_updates_and_recovers_within_deadline) ... ok
test_lock_conflict (test_docsync.SyncTests.test_lock_conflict) ... ok
test_missing_and_tampered_generated_output_are_drift (test_docsync.SyncTests.test_missing_and_tampered_generated_output_are_drift) ... ok
test_missing_source (test_docsync.SyncTests.test_missing_source) ... ok
test_nested_add_rename_delete_and_comment_change (test_docsync.SyncTests.test_nested_add_rename_delete_and_comment_change) ... ok
test_output_directory_is_rejected (test_docsync.SyncTests.test_output_directory_is_rejected) ... ok
test_public_api_signatures_and_missing_descriptions (test_docsync.SyncTests.test_public_api_signatures_and_missing_descriptions) ... ok
test_real_symlink_is_rejected_when_supported (test_docsync.SyncTests.test_real_symlink_is_rejected_when_supported) ... skipped "OS symlink creation unavailable: [WinError 1314] A required privilege is not held by the client: 'C:\\Users\\DEEPAK~1\\AppData\\Local\\Temp\\tmp54s2c4an\\src\\example.py' -> 'C:\\Users\\DEEPAK~1\\AppData\\Local\\Temp\\tmp54s2c4an\\src\\linked.py'"
test_render_is_sorted (test_docsync.SyncTests.test_render_is_sorted) ... ok
test_replace_failure_preserves_output_and_cleans_up (test_docsync.SyncTests.test_replace_failure_preserves_output_and_cleans_up) ... ok
test_source_change_during_render_is_rejected (test_docsync.SyncTests.test_source_change_during_render_is_rejected) ... ok
test_source_is_never_executed (test_docsync.SyncTests.test_source_is_never_executed) ... ok
test_symlink_source_and_output_guards (test_docsync.SyncTests.test_symlink_source_and_output_guards) ... ok
test_unowned_output_is_never_overwritten (test_docsync.SyncTests.test_unowned_output_is_never_overwritten) ... ok

----------------------------------------------------------------------
Ran 43 tests in 4.362s

OK (skipped=1)
```

Command: `python src/docsync.py check`, exit 0, elapsed 0.114 seconds:

```text
Documentation is current
```

### Remote verification

These were read-only queries; no publication or merge was performed.
Command: `gh pr view 1 --repo deepakkumar-r/automated-documentation-sync --json number,url,state,isDraft,mergeable,reviewDecision,baseRefName,headRefName,statusCheckRollup,mergedAt`,
exit 0, exact output:

```json
{"baseRefName":"main","headRefName":"capstone/us-001","isDraft":false,"mergeable":"MERGEABLE","mergedAt":null,"number":1,"reviewDecision":"","state":"OPEN","statusCheckRollup":[],"url":"https://github.com/deepakkumar-r/automated-documentation-sync/pull/1"}
```

Command: `gh repo view deepakkumar-r/automated-documentation-sync --json url,isPrivate,defaultBranchRef`,
exit 0, exact output:

```json
{"defaultBranchRef":{"name":"main"},"isPrivate":false,"url":"https://github.com/deepakkumar-r/automated-documentation-sync"}
```

Command: `gh pr view 1 --repo deepakkumar-r/automated-documentation-sync --json body,commits,reviews`,
exit 0. The remote body contains all five required sections; three commits are
listed, including the requirements checkpoint. `reviews` is `[]`.
Remote-query runtimes were not measured. No reported CI checks or submitted reviews
are evidence of neither a CI pass nor human approval.

### Pending items and findings

| Priority | Finding | Required next step |
|---|---|---|
| Showcase acceptance | Ten agent configurations, tool lists, allowlist and handoff targets pass local contract tests; a live execution of all ten is not established | In a supported trusted host, demonstrate bounded delegation, manual handoffs, denied approvals and automatic post-edit synchronization; retain actual evidence |
| Workflow defect | FIXED below: Code Review instructed the Orchestrator to record its report, but neither had an edit tool | Code Review now hands findings to Testing, which has `edit` and records docs/code-review.md; still needs live-host confirmation |
| Delivery-state inconsistency | FIXED below: implementation plan P8 and the changelog said publication was unauthorized/unconfigured despite the verified open PR | docs/impl-plan.md and CHANGELOG.md now state PR #1 is published, open and mergeable, with review/merge pending |
| Inventory inconsistency | FIXED below: the agent catalog said two reusable skills; five skill directories are present | docs/agent-catalog.md now lists all five skills by name |
| Final SDLC gate | PR is open, with no submitted reviews and no reported status checks | Obtain human review and separate merge approval; CI is optional under the current local/offline requirements, not a demonstrated pass |
| Environment limitation | Real symlink integration skipped; only Python 3.15.2 executed | Disclose the skip and untested Python 3.11 minimum; optionally verify in an environment with the required interpreter and symlink support |
| Demo workspace | The current workspace is not a Git repository; real Git integration passed in temporary repositories | Use a checkout of capstone/us-001 with the Git gate installed for any live staged-index/commit demonstration |

No implementation failures were observed. The report-writer ownership defect,
stale delivery-state wording and skill-inventory mismatch are repaired below with
passing tests. Live Copilot-host execution of the corrected handoff, the final
SDLC gate (human review/merge) and the disclosed environment limitations remain
outstanding; "all agents work perfectly" and "fully completed through merge"
would still overstate the evidence until those are independently confirmed.

### Repair pass - 2026-11-08 (report-writer ownership and delivery-state fixes)

Fixed the report-writer ownership defect found in the showcase audit:
`code-review.agent.md` claimed "The Orchestrator records the review report," but
neither Code Review (`tools: [read, search]`) nor Orchestrator (`tools: [read,
search, agent]`) can edit files. Code Review now hands its verbatim findings to
Testing (`tools: [..., edit]`), which records them in docs/code-review.md before
running verification. Also corrected `docs/agent-catalog.md` (stale "two skills"
versus five actual skill directories, and the Code Review/Testing row wording),
`docs/impl-plan.md` P8 and `CHANGELOG.md` (both still said publication was
blocked/unapproved despite the already-verified open PR #1). No source, test,
hook or policy file was changed; only agent instructions and handwritten docs.

Command: `python -m unittest discover -s tests -v`, exit 0; runner runtime 3.836
seconds, command elapsed 4.186 seconds. Final summary:

```text
Ran 43 tests in 3.836s

OK (skipped=1)
```

Command: `python src/docsync.py check`, exit 0, elapsed 0.104 seconds:

```text
Documentation is current
```

Live Copilot-host confirmation of the corrected Code Review -> Testing handoff is
still outstanding; only local contract tests validate the new frontmatter/text.

### Report validation

After updating this report, command
`python -m unittest discover -s tests -p test_customizations.py -k markdown_relative_links -v`
exited 0; runner runtime 0.007 seconds, command elapsed 0.172 seconds:

```text
test_markdown_relative_links_resolve (test_customizations.CustomizationTests.test_markdown_relative_links_resolve) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
```

## Reviewer guide verification - 2026-11-09

Added [the reviewer showcase guide](reviewer-showcase-guide.md), linked it from
the README and updated the local PR description's required complete file manifest.
Existing report history and uncommitted work were preserved. No source, generated
API, agent configuration, hook, remote PR or approval state was changed by this work.
The guide's interactive presentation steps are instructions, not claimed execution.

Command: `python -m unittest discover -s tests -v`, exit 0.
Runner runtime: 4.923 seconds; measured command elapsed: 5.410 seconds.
Exact final runner summary:

```text
Ran 43 tests in 4.923s

OK (skipped=1)
```

42 passed, 1 skipped, 0 failures/errors. The real symlink integration test skipped
with WinError 1314 (required privilege unavailable). Real Git partial-staging and
installed pre-commit integration passed. Markdown links and the expanded PR file
manifest passed.

Command: `python src\docsync.py check`, exit 0; measured elapsed: 0.126 seconds.
Exact output:

```text
Documentation is current
```

These results verify local repository contracts and generated-output consistency.
They do not establish live agent discovery/delegation, hook loading, execution of
the guide's manual demo, current remote state, human review or merge.
