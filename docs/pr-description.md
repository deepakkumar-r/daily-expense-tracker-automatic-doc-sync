# PR description - published as PR #1

[Pull request](https://github.com/deepakkumar-r/automated-documentation-sync/pull/1):
`capstone/us-001` into `main`. Existing PR is reused for this migration.
Awaiting human review; not merged.

## Summary
Replace the documentation-only sample with Daily Expense Tracker, the only US-001.
Provide persistent Python/SQLite CLI expense CRUD, category filtering and exact
integer-cent totals. Preserve the deterministic documentation-sync engine,
ten-agent human-gated SDLC pipeline, automation hooks and Git workflows.
Extend the same story with a responsive local HTML/CSS/JavaScript dashboard,
Python JSON HTTP adapter and separate generated frontend documentation.
These website changes are local; no new publication is claimed.

## Changes Made
- `.github/copilot-instructions.md`: shared scope, trust and verification rules.
- `.github/agents/orchestrator.agent.md`: central delegation and human gates.
- `.github/agents/requirements.agent.md`: requirements clarification.
- `.github/agents/architecture.agent.md`: component design.
- `.github/agents/design-review.agent.md`: design risk review.
- `.github/agents/planning.agent.md`: dependency planning.
- `.github/agents/development.agent.md`: approved implementation.
- `.github/agents/documentation-sync.agent.md`: deterministic synchronization.
- `.github/agents/code-review.agent.md`: read-only review.
- `.github/agents/testing.agent.md`: executable evidence.
- `.github/agents/pr-management.agent.md`: approved local/remote delivery.
- `.github/instructions/python.instructions.md`: implementation invariants.
- `.github/instructions/documentation.instructions.md`: doc ownership/evidence.
- `.github/skills/documentation-sync/SKILL.md`: reusable sync procedure.
- `.github/skills/verification/SKILL.md`: reusable test procedure.
- `.github/skills/start-sdlc/SKILL.md`: preserved manual workflow skill with corrected links.
- `.github/skills/sync-docs/SKILL.md`: preserved manual synchronization skill.
- `.github/skills/verify/SKILL.md`: preserved manual verification skill.
- `.github/prompts/start-sdlc.prompt.md`: resume the coordinator workflow.
- `.github/prompts/sync-docs.prompt.md`: focused sync trigger.
- `.github/prompts/verify.prompt.md`: focused verification trigger.
- `.github/hooks/docsync.json`: VS Code lifecycle wiring.
- `.github/hooks/pre-commit`: staged-source/doc gate.
- `.gitignore`: omit transient locks, caches and temporary output.
- `.gitattributes`: consistent line endings and portable hook script.
- `src/docsync.py`: AST engine, atomic sync, check and watcher.
- `src/expenses.py`: persistent expense CLI/service, validated CRUD, category filters and exact totals.
- `src/web.py`: loopback HTTP API/static server reusing the existing service and SQLite database.
- `src/static/index.html`: accessible dashboard, filters, charts, expense editor and delete confirmation.
- `src/static/styles.css`: responsive professional dashboard layout and components.
- `src/static/app.js`: vanilla JavaScript CRUD, exact summaries, charts and explicit error states.
- `src/ui_docs.py`: non-executing frontend structure and functionality documentation renderer.
- `src/copilot_hook.py`: permissions and automatic post-tool synchronization.
- `src/git_gate.py`: isolated staged-index validation.
- `tests/test_docsync.py`: engine, safety, CLI and live watcher tests.
- `tests/test_automation.py`: hook/index contracts and optional real Git integration.
- `tests/test_customizations.py`: agent, workflow and output-quality contracts.
- `tests/test_expenses.py`: isolated expense API, persistence, money, validation and real CLI tests.
- `tests/test_web.py`: real loopback HTTP CRUD, summaries, validation, storage failures and request-policy tests.
- `tests/test_ui_docs.py`: frontend sync, independent fingerprints, ownership, watcher, hook and staged-gate regressions.
- `tests/test_frontend.py`: optional dependency-free Node controller test runner.
- `tests/frontend.test.js`: ten DOM-controller tests for CRUD, charts, precision, filters, errors and stale responses.
- `docs/requirements.md`: single story and acceptance criteria.
- `docs/architecture.md`: components, contracts and Mermaid diagram.
- `docs/design-review.md`: risks and decisions.
- `docs/impl-plan.md`: dependency-ordered plan.
- `docs/agent-catalog.md`: roles and tool permissions.
- `docs/workflow.md`: eight stages, Mermaid and delivery state.
- `docs/guardrails.md`: approvals, trust and failure boundaries.
- `docs/code-review.md`: seven-area review and resolved findings.
- `docs/test-report.md`: real evidence and disclosed limitations.
- `docs/reviewer-showcase-guide.md`: end-to-end speaking script, isolated demonstration and bounded agent prompts.
- `docs/pr-description.md`: required PR sections and complete change manifest.
- `docs/api.md`: generated source-of-truth reference.
- `docs/ui.md`: generated frontend pages, components, functions, styles and functionality reference.
- `CHANGELOG.md`: release summary.
- `README.md`: usage, automation, Git setup and deliverable index.

The supplied `EPAM_Capstone_proj_breif.md` remains unchanged.

## Test Evidence
See [test-report.md](test-report.md) for commands, output and skip reasons.
Run `python -m unittest discover -s tests -v` and `python src/docsync.py check`.
Website extension: 81 tests in 16.606s, 80 passed and one Windows symlink-privilege
skip, zero failures/errors; ten JavaScript controller checks also pass.
Both references pass sync/check with unchanged second synchronization.
Real browser visual checks were not executed because browser-tool discovery
was denied by the approval hook. No remote PR update is claimed for this extension.

Historical CLI migration:
Executed on 2026-11-10: 61 tests in 7.287s, 60 passed, 1 Windows symlink-privilege
skip, 0 failures/errors. All 17 new expense tests and real Git/pre-commit tests pass.
Drift check: `Documentation is current`; second sync: `Documentation unchanged`.
Final staged-index check: `Staged documentation is current`. New Python source
uses the existing LF convention so index and working-tree fingerprints agree.
Historical infrastructure evidence is retained separately in the test report.

## Known Limitations
`Not Found` explicitly identifies missing docstrings or modules without public APIs.
Dynamic/inherited APIs and annotation rendering are outside scope.
Expense Tracker is local and single-currency, without authentication, public hosting,
budgets or cloud synchronization. SQLite files must be backed up by the user.
The website's standard-library server is loopback-only and not for production.
UI docs provide a conservative static inventory, not full CSS/JS grammar validation.
Real Git and OS symlink integration depend on local tooling/permissions; see test report.
Real Git integration now passes. Windows symlink creation remains unavailable.
Copilot host discovery/delegation needs a supported trusted workspace; local contract
tests do not prove all agents were invoked. Repository creation and PR publication
are approved by the human; merge is not approved.

## Reviewer Checklist
- [ ] Confirm US-001 acceptance criteria and eight-stage artifacts.
- [ ] Exercise expense CRUD, persistent data, category filters and exact totals.
- [ ] Review generated docstrings for correctness and secrets.
- [ ] Run tests and drift check; inspect every skip.
- [ ] Verify live watcher and supported VS Code hook behavior.
- [ ] Install Git gate and verify partial-staging rejection with real Git.
- [ ] Confirm agents, delegation and approval prompts in the Copilot host.
- [ ] Approve exact remote/base branch and PR publication separately.
- [ ] Obtain human code review and separate merge approval.
