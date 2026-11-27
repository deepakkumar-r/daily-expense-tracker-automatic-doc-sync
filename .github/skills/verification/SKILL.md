---
name: verification
description: "Verify documentation-sync code, automation, agent configuration and output quality without fabricated evidence."
---
1. Run the available frontend regression test with Node.js; report skips explicitly.
2. Validate the GitHub Actions workflow, change-manifest contract and agent files.
3. Record commands, runtime, exit codes and exact output in docs/test-report.md.
4. If anything fails, report it and repair only affected work before re-running.
5. Distinguish tested hook contracts from unverified host loading and remote PR state.
