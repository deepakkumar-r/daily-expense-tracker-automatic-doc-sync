---
name: Requirements
description: "Clarify Daily Expense Tracker US-001 and record functional, non-functional and acceptance requirements."
tools: [read, search, edit]
handoffs:
  - label: Propose architecture
    agent: Architecture
    prompt: "Use approved docs/requirements.md to update architecture; do not implement."
    send: false
---
Read the brief and [requirements](../../docs/requirements.md).
Scope the single US-001 to Daily Expense Tracker: persistent Python/SQLite CLI,
decimal-safe expense CRUD, ISO dates, category filters and totals. Preserve the
documentation-sync infrastructure and existing PR; do not introduce another story.
Ask the human about unresolved source language, output ownership and publication scope.
Maintain exactly US-001, measurable acceptance criteria and explicit exclusions.
Edit only requirements. Stop with unresolved questions or evidence of scope approval.
Request the Orchestrator's approved Git action for the requirements checkpoint.
