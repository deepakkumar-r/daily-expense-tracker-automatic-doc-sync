# Daily Expense Tracker - Agentic SDLC Pipeline

One story, eight SDLC stages, one Orchestrator and nine Copilot specialist agents.
The application adds, views, updates and deletes daily expenses, filters by
category and calculates exact totals. Local SQLite storage persists between runs.
The existing Python AST documentation engine, hooks and Git workflows are retained.

[Public repository](https://github.com/deepakkumar-r/automated-documentation-sync) |
[Open PR #1](https://github.com/deepakkumar-r/automated-documentation-sync/pull/1).
Implementation is on `capstone/us-001` pending human review; `main` contains the
capstone brief baseline. Clone/check out the PR branch to run the application.

## Daily Expense Tracker quick start
Requires Python 3.11+; no pip install needed. Run from the workspace root:

```powershell
python src\expenses.py add --amount 12.50 --category Food --description "Lunch" --date 2026-11-10
python src\expenses.py add --amount 3.25 --category Travel --description "Bus"
python src\expenses.py view
python src\expenses.py view --category food
python src\expenses.py update 1 --amount 10.00 --description "Lunch discount"
python src\expenses.py total
python src\expenses.py total --category FOOD
python src\expenses.py delete 1
python src\expenses.py --help
```

In a new database the first two IDs are 1 and 2. `total` after the update is
`13.25`; filtered `FOOD` total is `10.00`. After deleting ID 1 the total is `3.25`.
The default database is `expenses.sqlite3` in the repository root, ignored by Git.
To keep a separate file, put the option before the command:

```powershell
python src\expenses.py --database "C:\existing-folder\personal.sqlite3" view
```

Amounts are positive plain decimal strings (`0.01` to `999999999.99`, up to two
decimal places). Integer cents avoid rounding errors; currency is user-chosen,
with no conversion. Category matching is exact after trimming and Unicode
casefolding; `Food` is stored as `food`. Descriptions are trimmed; category and
description limits are 80 and 500 printable characters. Dates require `YYYY-MM-DD`
and default to the local day. Views sort by date then ID; missing categories return
no rows and total `0.00`. Updates change only supplied fields; deleted IDs are not
reused. Invalid input, missing IDs and database failures report to stderr and exit 2;
successful commands exit 0. Authentication and cloud sync are not included.

## Website quick start

```powershell
python src\web.py
```

Open **http://127.0.0.1:8000** in your browser. The responsive dashboard uses plain
HTML, CSS and JavaScript with no dependencies, CDN, account or build step.
It shares the unchanged `ExpenseTracker` service and default `expenses.sqlite3`
with the CLI; existing records appear when their month is selected.
Choose a month/category to filter the table, exact monthly total, transaction
count, rounded-to-nearest-cent average, daily bars and category chart together.
Clear the month to view all dates. Reset restores the current local month and all
categories. Add/edit validates fields on the server; delete requires confirmation.
Refresh picks up external CLI changes. Empty states and storage/network errors are
visible; failed saves retain entered values. Amounts use your chosen currency.

For another database or port:

```powershell
python src\web.py --database "C:\existing-folder\personal.sqlite3" --port 8080
```

The server binds only to loopback; stop it with Ctrl+C. This is a private local
tool, **not a production/public or multi-user server**. Do not expose it through
a proxy or port forwarding. The server validates Host/Origin and requires
`X-Expense-Request: 1` for mutations; CORS is not enabled.
Open the served URL, not the HTML file directly.

### JSON HTTP API

| Method | Endpoint | Result |
|---|---|---|
| GET | `/api/expenses?month=2026-11&category=food` | Records, all available categories, filtered summary and daily/category series |
| POST | `/api/expenses` | Create from `amount`, `category`, `description`, optional `date`; 201 |
| PUT | `/api/expenses/{id}` | Update any supplied expense fields; 200 |
| DELETE | `/api/expenses/{id}` | Delete one existing record; 200 |

Filters are optional and use the existing Unicode category normalization. Bodies
are UTF-8 JSON objects, at most 64 KiB, with string fields and no unknown fields.
Send `Content-Type: application/json` and `X-Expense-Request: 1` on writes.
IDs, integer cents and decimal amounts are strings to preserve browser precision;
counts are JSON integers. Errors return `{"error":"..."}` (400 input, 403 origin,
404 missing record/path, 405 method, 503 storage/asset failure). Dates/order,
limits and SQLite schema remain the same as the CLI. See [API reference](docs/api.md).

## Documentation and verification

```powershell
python src\docsync.py sync
python src\docsync.py check
python -m unittest discover -s tests -v
python src\docsync.py watch
```

The watcher performs an initial sync, polls every second, and stops with Ctrl+C.
Use `--interval 0.25` for faster polling or `--root "C:\path\to\project"` to document
another workspace's `src` directory. No watcher is installed as a background service.
`check` exits 0 when current, 1 for drift/missing output, and 2 for operational errors.
On a syntax error the previous document remains intact; repair source to recover.

The engine writes [docs/api.md](docs/api.md) for Python APIs and
[docs/ui.md](docs/ui.md) for frontend pages, components and functionality.
It discovers nested `.py`, `.html`, `.css` and `.js` files under `src`.
Each reference has an independent raw-byte fingerprint: frontend-only edits leave
the API reference untouched and vice versa. Additions, modifications, renames and
deletions, including removal of the final frontend file, are reflected by sync,
watch, PostToolUse and the staged-index gate. Projects without frontend source
or an existing generated UI reference keep Python-only output.
Handwritten docs are untouched; unowned API/UI references are never overwritten.
Public modules, functions, classes, constructors and methods are documented.
Private declarations, runtime/inherited APIs, annotations and literal defaults are
excluded. Missing descriptions say `Not Found`; public docstrings require human
secret/content review. Output must retain its generator ownership marker.
UI documentation statically inventories titles/headings, controls, linked assets,
CSS selectors/responsive rules and named JavaScript functions/classes. Use
`data-component="Name" data-doc="Description"` in HTML and
`/** @ui Description. */` comments in JavaScript for explicit functionality prose.
No source is executed; defaults, arbitrary field values and full source are not
published. This is a conservative static inventory, not a full CSS/JS parser or
runtime behavior inference. Frontend input must be UTF-8; errors preserve good output.
All outputs are rendered and ownership-checked before per-file atomic replacement
under one lock. A failed filesystem replacement can leave one reference stale;
`check` detects this and rerunning `sync` repairs it.

The standard unittest command also runs ten dependency-free JavaScript controller
checks through Node when available (otherwise explicitly skipped).
Node is optional for testing, never required to run the website.

## Copilot automation
Open a trusted workspace with a current VS Code/Copilot version supporting custom
agents, delegation and hooks. Select **Orchestrator** or `/start-sdlc`.
Use `/sync-docs` or `/verify` for focused tasks; reload the window if needed.
The [agent catalog](docs/agent-catalog.md) lists responsibilities and tool boundaries.
Handoffs are manual confirmation points (`send: false`).

[VS Code hooks](.github/hooks/docsync.json) ask approval for non-read tools and run
sync after approved tool use. They use the VS Code lifecycle JSON contract, not a
universal CLI hook format. The watcher works independently when hooks are unavailable.
Automatic synchronization is executable code, not an instruction asking an LLM
to remember documentation.

## Install the local Git gate
Git is optional for sync/tests but required for commits and staged-index verification.
After installing Git, from this repository root:

```powershell
git init
git config core.hooksPath .github/hooks
python src\docsync.py sync
git add .
git update-index --chmod=+x .github/hooks/pre-commit
python src\git_gate.py
```

Then commit with your configured identity and the Copilot co-author trailer.
Check an existing repository's `core.hooksPath` before changing it; do not replace
team hooks blindly. Git for Windows supplies the shell for the pre-commit entry.
On POSIX also run `chmod +x .github/hooks/pre-commit`.
The gate checks staged blobs, not the working tree: stage matching source AND
generated docs. It never stages files automatically. Git attributes keep Python
source line endings stable so fingerprints survive checkout.

## Repository
```text
.github/
  agents/          # Orchestrator + nine specialists
  instructions/    # Scoped Python and documentation rules
  skills/          # Reusable sync and verification workflows
  prompts/         # Start/resume, sync and verify
  hooks/           # VS Code hooks and opt-in Git gate
src/               # Expense CLI/service, loopback HTTP API, sync engine and adapters
  static/          # Plain HTML/CSS/JavaScript dashboard
tests/             # Isolated unit/integration/contract tests
docs/              # Required SDLC deliverables + generated API/UI
```

## Deliverables
- [Reviewer showcase guide](docs/reviewer-showcase-guide.md): complete presentation
  script, safe live demo, exact speaking lines and optional agent prompts.
- [Requirements](docs/requirements.md), [architecture](docs/architecture.md),
  [design review](docs/design-review.md), [implementation plan](docs/impl-plan.md).
- [Agent catalog](docs/agent-catalog.md), [workflow](docs/workflow.md),
  [guardrails](docs/guardrails.md), [code review](docs/code-review.md).
- [Test report](docs/test-report.md), [changelog](CHANGELOG.md),
  [PR description](docs/pr-description.md), [generated API](docs/api.md).

## Delivery limitations
Python checks run locally; see the report for exact evidence and skips.
Git and GitHub CLI are now available, the authenticated account is `deepakkumar-r`,
and real staged-index/pre-commit integration passes. Windows symlink creation is
unavailable; symlink rejection paths are still unit-tested.
Repository/PR publication is approved; merge requires separate human approval.
This migration updates existing PR #1; no new PR or merge is permitted.
Copilot host discovery/delegation must be confirmed after loading the workspace;
configuration tests are not proof that ten agents ran in this session.
