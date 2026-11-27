---
name: documentation-sync
description: "Synchronize only documentation affected by changed functionality."
---
1. Inspect the current local diff first; use a GitHub Actions change manifest only as supplemental evidence.
2. Classify added, modified and deleted functionality and identify affected docs.
3. Update only relevant API, architecture, UI, README, test-plan and changelog sections.
4. Before editing, ask the human with a Yes/No form whether the identified documentation should be updated.
5. On No, leave docs unchanged and report the sync as deferred.
6. Preserve unrelated handwritten docs, local runtime data and all human approval gates.
7. Report Changed / Evidence / Risks / Next gate. Use **Not Found** for missing facts.
8. Never execute or recreate a Python/Java documentation engine.
