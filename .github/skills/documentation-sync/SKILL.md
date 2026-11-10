---
name: documentation-sync
description: "Synchronize generated API documentation after Python source changes or diagnose drift."
---
1. From the workspace root run `python src/docsync.py sync`.
2. On failure stop; repair source/ownership/path errors without deleting user docs.
3. Run `python src/docsync.py check`; exit 0 means current, 1 drift, 2 error.
4. Inspect only changed output or missing-docstring entries; do not regenerate other docs.
5. For editor changes outside Copilot run `python src/docsync.py watch`.
The watcher stays in the foreground until Ctrl+C. Hooks invoke the same engine.
