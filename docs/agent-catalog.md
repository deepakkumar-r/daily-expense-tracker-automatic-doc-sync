# Agent catalog

Exactly ten workspace custom agents; nine specialists, one central coordinator.
Files live in [.github/agents](../.github/agents). No model overrides.
Their current application scope is Daily Expense Tracker US-001: persistent
Python/SQLite CLI CRUD, category filters and integer-cent totals. Documentation
Sync remains a supporting implementation role; agent names, permissions and
manual handoffs are unchanged.

| Agent | Stage | Input | Output / stop condition | Tools |
|---|---|---|---|---|
| Orchestrator | 1-8 | Brief, workflow, completed evidence | Bounded delegation and human gates; no implementation | read, search, agent |
| Requirements | 1 | Brief and human answers | Single US-001 in requirements.md | read, search, edit |
| Architecture | 2 | Approved requirements | architecture.md with Mermaid and contracts | read, search, edit |
| Design Review | 3 | Requirements, architecture | design-review.md; request human approval | read, search, edit |
| Planning | 4 | Approved reviewed architecture | Dependency-ordered impl-plan.md | read, search, edit |
| Development | 5 | Approved plan | src/tests changes and focused evidence | read, search, edit, execute |
| Documentation Sync | 5 | Changed source | Generated api.md and drift result | read, search, execute |
| Code Review | 6 | Implementation, requirements | Findings handed to Testing to record; no edits | read, search |
| Testing | 7 | Reviewed changes | Records code-review.md, then actual tests and test-report.md | read, search, execute, edit |
| PR Management | 8 | Passing evidence, human permission | Changelog and PR draft; approved Git actions only | read, search, edit, execute |

Every sequential handoff has `send: false`; user confirmation is not auto-sent.
Orchestrator delegates through its `agent` tool and explicit `agents` allowlist.
Each role returns Changed / Evidence / Risks / Next gate. File ownership stated in
agent bodies is guidance; tool restrictions and hooks provide additional controls.
Handoffs do not substitute for recorded human approval.

Reusable surfaces: two scoped instruction files, five skills (documentation-sync,
verification, start-sdlc, sync-docs, verify), three prompts and one VS Code hook
configuration. Runtime-generated API prose does not consume model tokens.
