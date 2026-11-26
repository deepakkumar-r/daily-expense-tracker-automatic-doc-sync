---
name: sync-docs
description: "Synchronize local affected documentation after source changes with a human Yes/No gate."
agent: Documentation Sync
---
Use the Documentation Sync agent and the current local diff. Before editing,
ask the human through a Yes/No approval form whether the corresponding
documentation should be updated. On No, do not edit docs. On Yes, update only
documentation affected by added, modified, or deleted functionality. Preserve
unrelated Markdown and report evidence, risks, and the next approval gate.
