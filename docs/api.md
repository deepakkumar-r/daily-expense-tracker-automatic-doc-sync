<!-- docsync:generated:v1 -->
# Python API reference

Generated from source; do not edit manually. Defaults and annotations are omitted.

Source fingerprint: `a1dd80e342e37f2075516eba9974b0d77eaee0dcd82c9d4622eb30b2e7dc46b4`

## <code>src/copilot_hook.py</code>

[Source](../src/copilot_hook.py)

<pre>VS Code Copilot lifecycle adapter; input never becomes an executable command.</pre>

### <code>permission(payload)</code>

<pre>Allow known reads; request human approval for every other tool.</pre>

### <code>main(argv=...)</code>

<pre>Validate hook input and return the VS Code permission or sync result.</pre>

## <code>src/docsync.py</code>

[Source](../src/docsync.py)

<pre>Deterministic, local-only API documentation synchronization.</pre>

### <code>SyncError</code>

<pre>Signal invalid source, unsafe output or a conflicting sync operation.</pre>

### <code>snapshot(root, suffixes=...)</code>

<pre>Read sorted requested source types without following symbolic links.</pre>

### <code>signature(node)</code>

<pre>Describe parameter kinds without publishing default expressions.</pre>

### <code>render(files)</code>

<pre>Render escaped public declarations and a fingerprint of every source byte.</pre>

### <code>output_bytes(root, name=...)</code>

<pre>Read only a regular generated file under a safe docs directory.</pre>

### <code>documents(root, files)</code>

<pre>Render separate backend/frontend references before any output is replaced.</pre>

### <code>check(root)</code>

<pre>Return whether all generated documents exactly match their source types.</pre>

### <code>sync(root)</code>

<pre>Atomically synchronize owned output; return true only when bytes changed.</pre>

### <code>watch(root, interval=..., stop=..., report=...)</code>

<pre>Continuously synchronize, report failures and recover after valid edits.</pre>

### <code>main(argv=...)</code>

<pre>Run sync, check or watch with explicit 0/1/2 exit semantics.</pre>

## <code>src/expenses.py</code>

[Source](../src/expenses.py)

<pre>Daily Expense Tracker CLI with persistent SQLite storage and exact cent totals.

Run python src\expenses.py --help for add, view, update, delete and total commands.
Amounts use a single user-chosen currency with two decimal places. Categories are
trimmed and casefolded; dates are ISO YYYY-MM-DD. No network services are used.</pre>

### <code>ExpenseError</code>

<pre>Signal invalid expense input or an expense ID that does not exist.</pre>

### <code>format_amount(cents)</code>

<pre>Format nonnegative integer cents as a two-decimal currency-neutral amount.</pre>

### <code>Expense</code>

<pre>Immutable persisted expense: ID, amount in cents, category, description, date.</pre>

### <code>ExpenseTracker</code>

<pre>Manage a local SQLite expense file; methods raise on invalid or missing data.</pre>

### <code>ExpenseTracker.__init__(self, database=...)</code>

<pre>Create the expense table if needed; surface database/open failures.</pre>

### <code>ExpenseTracker.add(self, amount, category, description, date=...)</code>

<pre>Persist a positive decimal expense; omit date to use the local day.</pre>

### <code>ExpenseTracker.view(self, category=...)</code>

<pre>List expenses by date then ID, optionally matching a normalized category.</pre>

### <code>ExpenseTracker.update(self, expense_id, *, amount=..., category=..., description=..., date=...)</code>

<pre>Update supplied fields atomically; reject missing IDs or an empty update.</pre>

### <code>ExpenseTracker.delete(self, expense_id)</code>

<pre>Delete one expense by ID; raise ExpenseError if it does not exist.</pre>

### <code>ExpenseTracker.total(self, category=...)</code>

<pre>Return exact integer cents for all expenses or one normalized category.</pre>

### <code>main(argv=...)</code>

<pre>Run the expense CLI; return 0 on success or 2 for input/database errors.</pre>

## <code>src/git_gate.py</code>

[Source](../src/git_gate.py)

<pre>Reject staged source and generated-document drift without changing the Git index.</pre>

### <code>git(root, *arguments)</code>

<pre>Run Git without a shell and report failures explicitly.</pre>

### <code>check_index(root)</code>

<pre>Validate staged blobs, including partially staged files, in isolation.</pre>

### <code>main()</code>

<pre>Check the index of the current workspace; never stage or rewrite files.</pre>

## <code>src/ui_docs.py</code>

[Source](../src/ui_docs.py)

<pre>Static frontend inventory rendering; never import or execute documented assets.</pre>

### <code>PageInventory</code>

<pre>Collect explicit HTML metadata, components, controls and local assets.</pre>

### <code>PageInventory.__init__(self)</code>

<pre>Initialize an empty semantic page inventory.</pre>

### <code>PageInventory.handle_starttag(self, tag, attrs)</code>

<pre>Read only allowlisted publishable metadata, not arbitrary field values.</pre>

### <code>PageInventory.handle_data(self, data)</code>

<pre>Capture visible title and heading text.</pre>

### <code>PageInventory.handle_endtag(self, tag)</code>

<pre>Finalize text of the currently captured title or heading.</pre>

### <code>masked_source(text, javascript=...)</code>

<pre>Mask comments and strings for a conservative declaration-only inventory.</pre>

### <code>render_ui(files)</code>

<pre>Render deterministic frontend structure, explicit descriptions and raw-byte fingerprint.</pre>

## <code>src/web.py</code>

[Source](../src/web.py)

<pre>Local expense website and JSON API backed by the existing SQLite service.

Run python src\web.py and open http://127.0.0.1:8000. This loopback-only server
is for personal local use, not public deployment or multi-user authentication.
GET /api/expenses accepts optional month (YYYY-MM) and category filters.
POST /api/expenses creates; PUT and DELETE /api/expenses/{id} mutate a record.
Mutation requests require JSON and X-Expense-Request: 1. Amounts, cents and IDs
are decimal strings in JSON to preserve precision in browser JavaScript.</pre>

### <code>expense_json(expense)</code>

<pre>Serialize a persisted record without lossy JavaScript integers.</pre>

### <code>dashboard(tracker, month, category)</code>

<pre>Build exact filtered totals and chart series from one persisted snapshot.</pre>

### <code>ExpenseServer</code>

<pre>Serve loopback requests using the unchanged expense service.</pre>

### <code>ExpenseServer.__init__(self, database=..., port=...)</code>

<pre>Validate/open SQLite before binding the loopback HTTP listener.</pre>

### <code>ExpenseHandler</code>

<pre>Handle a small allowlisted static website and same-origin JSON API.</pre>

### <code>ExpenseHandler.setup(self)</code>

<pre>Bound request socket reads to avoid indefinitely blocked clients.</pre>

### <code>ExpenseHandler.do_GET(self)</code>

<pre>Return the dashboard assets or filtered expense collection.</pre>

### <code>ExpenseHandler.do_HEAD(self)</code>

<pre>Return GET response headers without a body.</pre>

### <code>ExpenseHandler.do_POST(self)</code>

<pre>Create a validated expense from JSON.</pre>

### <code>ExpenseHandler.do_PUT(self)</code>

<pre>Update supplied expense fields without changing its ID.</pre>

### <code>ExpenseHandler.do_DELETE(self)</code>

<pre>Delete a persisted expense by ID.</pre>

### <code>main(argv=...)</code>

<pre>Run the local website until Ctrl+C; report startup failures explicitly.</pre>
