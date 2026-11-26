<!-- copilot-agent-owned -->
# API documentation

This reference is maintained by the `Documentation Sync` Copilot agent.
The previous Python and SQLite application paths are not part of the current
copy-pasteable application. The current adapter is the dependency-free Java
`web` server with atomic local JSON persistence.

## Current supported surface

- The preserved browser surface is documented in [ui.md](ui.md).
- The Java adapter exposes loopback-only JSON CRUD at `/api/expenses` and
  persists runtime records in ignored `expenses-java.json`.
- `POST`, `PUT` and `DELETE` require `X-Expense-Request: 1`; API requests must
  use the local Host/Origin values.
- Amounts accept positive decimal strings with at most two places and are
  bounded at `999999999.99`; categories are limited to 80 characters and
  descriptions to 500 characters.
- Added, modified and deleted functionality is identified by the GitHub Actions
  change manifest before the agent updates relevant documentation.
- Missing implementation or test evidence is recorded as **Not Found** rather
  than inferred.

Do not regenerate unrelated Markdown. Human requirements and design approvals
remain mandatory before implementation or publication.
