# Requirements

## US-001 (the only user story)
As a user, I want to add, view, update and delete daily expenses, filter them by
category and calculate totals, so I can understand and manage my spending.

The Daily Expense Tracker replaces the documentation-only sample application.
The existing documentation-sync engine, eight-stage Agentic SDLC, all ten agents,
automation hooks and Git workflows remain supporting infrastructure.

Source: the capstone brief and the human's Daily Expense Tracker change request.
The human approved a Python CLI with persistent SQLite storage, decimal-safe
amounts, free-text categories and dates; integration of existing uncommitted
documentation/agent work; and committing/pushing `capstone/us-001` to update
existing PR #1. No new PR or merge is approved.
The subsequent website request extends this same US-001 to a plain HTML/CSS/JS
dashboard and local Python HTTP adapter, retaining the CLI, SQLite database and
documentation engine. This request also approves Python/HTML/CSS/JS detection
and a separate generated UI reference; no additional publication is requested.

Latest publication approval (2026-11-10): the human subsequently requested a new
public repository, `deepakkumar-r/daily-expense-tracker-Automatic-doc-sync`,
including the current website/UI changes after validation and committing.
Create a PR from `capstone/us-001` into a baseline-only `main` there; do not merge.
This supersedes the earlier existing-PR-only publication restriction for this
delivery. Leave the original repository and its PR unchanged.

## Acceptance criteria
- AC1: Add an expense with a positive amount, category, description and ISO date
  (`YYYY-MM-DD`, default today). Assign a stable, never-reused integer ID and persist
  across CLI invocations in a local SQLite database.
- AC2: View expenses ordered by date then ID; update any supplied fields without
  changing the ID; delete by ID. Missing IDs fail explicitly without changing data.
- AC3: Filter views and totals by trimmed, case-insensitive exact category (Unicode
  casefold). An empty result lists no rows and has total `0.00`; unfiltered totals
  include all expenses. Store integer cents; never use floating-point arithmetic.
- AC4: Reject zero/negative/nonfinite amounts, scientific notation, more than two
  decimal places and amounts over `999999999.99`; reject blank/oversized text,
  invalid dates/IDs and updates without fields. Errors exit 2 with diagnostics and
  preserve existing data. Database errors are explicit, not empty-success results.
- AC5: Provide documented CLI commands `add`, `view`, `update`, `delete`, `total`
  and `--database`; no credentials, network or third-party packages required.
- AC6: Discover nested `src/**/*.py`; AST-parse without importing or executing source.
  Document modules, public functions, classes, methods and signatures; missing
  docstrings are explicitly `Not Found`. Omit private symbols and default values.
- AC7: `sync` produces a deterministic, owned `docs/api.md`; a second unchanged run
  performs no write. Any source-byte change changes its fingerprint. Additions,
  edits, renames and deletions are reflected.
- AC8: `watch` detects changes within the configured polling interval plus processing
  time. A Copilot PostToolUse hook runs the same sync without path guessing.
- AC9: The generator leaves handwritten docs untouched. Syntax/encoding errors, missing/empty source,
  symlinks and unsafe output ownership fail explicitly without replacing good output.
- AC10: `check` returns 0=current, 1=missing/stale generated output, 2=input/operational
  failure. An installed pre-commit gate rejects staged source/documentation drift.
- AC11: All eight SDLC stages, one Orchestrator plus nine specialist configurations,
  handoffs, scoped instructions, reusable skills, prompts and human gates are present.
- AC12: Unit/integration tests exercise expense CRUD, persistence, money accuracy,
  filtering, totals, invalid inputs, CLI/database failures and existing sync/output quality.
  Reports contain real execution evidence, not predicted results.
- AC13: Changelog and PR draft retain required sections. Update existing PR #1
  only after passing verification and approved commit/push; never create a new PR
  or merge as part of the original migration. The latest approved delivery instead
  creates a PR in the new repository specified above; main retains only the original
  brief baseline, and application code stays on the feature branch until review.
- AC14: Provide a responsive, keyboard-accessible local website with add, edit and
  confirmed delete, month/category filters, monthly totals/count/average, daily and
  category charts, explicit loading/empty/error states and no external dependencies.
  Reuse the same service/schema/database and validation as the CLI.
- AC15: Provide loopback-only JSON expense CRUD and filtered dashboard summaries.
  Validate request fields, Host/Origin and mutation headers; return explicit errors.
  Preserve integer precision with string IDs/amounts/cents in JSON.
- AC16: Discover nested HTML/CSS/JavaScript alongside Python. Generate owned
  `docs/ui.md` with frontend page/component/control/style/function inventories and
  explicit functionality descriptions; additions/edits/renames/deletions affect its
  fingerprint, including final frontend removal. Backend-only and frontend-only
  edits update only their respective references. Watcher, hook and staged gate
  cover both references and all four source types.

## Non-functional requirements
- Python 3.11+ standard library; local/offline operation, no service credentials.
- UTF-8 Markdown, stable sorting, no timestamps in generated content.
- Atomic replacement and lock-based cooperating-writer exclusion.
- Do not emit default expressions, module variable values or full source.
  Public docstrings are publishable content and must be reviewed for secrets.
- Minimize tokens through deterministic generation, bounded delegation and reuse.
- Expense dates use the local calendar; no currency conversion. Amounts represent
  one user-chosen currency with two decimal places. Categories are normalized with
  strip/casefold; descriptions retain spelling after trimming (limits 80/500).
- SQLite transactions provide atomic mutations. The local database is private
  runtime data, excluded from Git and generated API content.
- Browser UI uses plain HTML/CSS/vanilla JavaScript, system fonts and no CDN.
  The standard-library HTTP server is personal/local only, not public deployment.
  UI inventory uses static parsing/explicit metadata, not execution or inferred prose.

## Out of scope
Inferred business prose, full CSS/JavaScript grammar validation, dynamic/runtime APIs, inherited members,
external issue trackers, autonomous deployment, remote publication without approval,
authentication, public/multi-user hosting, budgets, recurring expenses, multi-currency and cloud sync.
