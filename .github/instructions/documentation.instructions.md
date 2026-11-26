---
description: "Use when changing capstone documentation, acceptance evidence or generated API references."
applyTo: "docs/**/*.md,README.md,CHANGELOG.md"
---
- Keep US-001 as the only story; reference its acceptance criteria.
- Update docs/api.md through the Documentation Sync agent and sync-docs prompt.
- Keep handwritten architecture and workflow Mermaid diagrams.
- Report missing facts as Not Found and blocked work as blocked.
- Record only executed test results and explicit human approvals.
- Map changed source files to only the relevant API, architecture, UI, README,
  test-plan, and changelog sections; do not rewrite unrelated documents.
