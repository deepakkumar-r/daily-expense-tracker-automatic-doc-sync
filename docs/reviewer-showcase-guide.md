# Reviewer showcase: complete runbook and speaking script

## How to use this guide

The application is now Daily Expense Tracker. Start with the CRUD/filter/total
commands in [README](../README.md) using an isolated `--database` file. Show
`0.10 + 0.20 = 0.30`, persistence across commands and invalid-input errors, then
continue with the preserved documentation automation demonstration below.
Historical verification counts are not current application evidence; consult the
latest section of [test report](test-report.md).

- **Say** contains the exact words to speak, in quotation marks.
- **Do** contains your actions. **Paste into Copilot** is a prompt, not speech.
- Commands are for PowerShell in Windows. Run repository commands from the project root.
- Expected results below are demonstration targets, not claims that those steps have already run.
- Keep the main checkout unchanged during the source-edit demonstration: use the isolated demo folder below.
- Do not claim all agents executed, hooks loaded, CI passed, or a PR merged without observing evidence.

Recommended presentation: 25-35 minutes for the core walkthrough; allow another
15-25 minutes for optional agent execution and reviewer questions. Agent latency varies.
If time is short, prioritize sections 1-8, one bounded agent demo, and the closing.

## 0. Prepare before the reviewer joins

### 0.1 Open the right workspace

Open the implementation checkout in VS Code. In the integrated PowerShell terminal:

```powershell
Set-Location "C:\Users\DeepakKumarR\Desktop\GH"
python --version
git --no-pager status --short --branch
git branch --show-current
git config --get core.hooksPath
```

Python must be 3.11 or newer. A missing `core.hooksPath` value means the local
Git hook path is not configured; it does not mean the engine is broken.
Do not change that setting simply to make the presentation look complete.

For a fresh checkout, use the implementation branch, not the brief-only baseline:

```powershell
git clone --branch capstone/us-001 https://github.com/deepakkumar-r/automated-documentation-sync.git
Set-Location ".\automated-documentation-sync"
```

Do not clone into an existing project folder or switch a dirty checkout blindly.
If your workspace differs from the path above, substitute its actual root.
No `pip install`, service account, API key, or database setup is needed.

### 0.2 Prepare the screen

Open these tabs, in order:

1. [README](../README.md)
2. [Requirements](requirements.md)
3. [Architecture](architecture.md) and [workflow](workflow.md), in Markdown preview
4. [Agent catalog](agent-catalog.md)
5. [Sync engine](../src/docsync.py)
6. [Generated reference](api.md)
7. [Test report](test-report.md)
8. [PR description](pr-description.md)

Keep one terminal for checks and a second terminal for the watcher.
Open Copilot Chat and confirm whether **Orchestrator**, **Documentation Sync**,
**Code Review**, and **Testing** appear in the agent picker.

If they are missing, use the Command Palette's **Developer: Reload Window**,
then check again. Custom agents/delegation/hooks require a supporting Copilot host
and a trusted workspace. If unavailable, use the terminal demo and disclose the limitation.
Do not install software or alter trust/security policy during the review without approval.

### 0.3 Preflight the engine

```powershell
python src\docsync.py check
python -m unittest discover -s tests -v
```

Read the actual output. If `check` reports drift, investigate before presenting;
do not manually repair [the generated reference](api.md). If appropriate, run
`python src\docsync.py sync` and then rerun the check.

The existing [test report](test-report.md) includes historical runs of 43 tests
with one Windows symlink-privilege skip. Your live count, runtime, skips and exit
codes take precedence. Do not memorize a historical runtime as a fresh result.

### 0.4 Decide the presentation boundary

Default: show existing artifacts, run local verification, use an isolated source
demo, and optionally execute a bounded agent task.
Do not commit, push, create a second PR, or merge during the presentation.
Keep all existing uncommitted work.

## 1. Opening: explain the project and the problem

**Do:** Show [README](../README.md).

**Say:**

> "My application is Daily Expense Tracker. It manages expenses through a persistent local Python CLI, supported by automated documentation and a human-gated Agentic SDLC pipeline."

> "US-001 lets a user add, view, update and delete expenses, filter categories and calculate exact totals. The original documentation infrastructure remains in place."

> "The expense application uses SQLite and integer cents. Its supporting infrastructure includes a deterministic documentation engine and a human-gated Copilot workflow covering eight software delivery stages."

> "I will first explain the requirements and architecture, then demonstrate synchronization and failure recovery, then show verification and the agent workflow. I will distinguish what executes locally from what still depends on the Copilot host and human approval."

## 2. Show scope and acceptance criteria

**Do:** Open [requirements](requirements.md). Point to US-001 and AC1-AC13.

**Say:**

> "The scope is intentionally limited to Python 3.11 or newer using only standard libraries. There is exactly one story, not a collection of unrelated features."

> "The engine recursively discovers Python files under src and parses their abstract syntax trees. It documents public modules, functions, classes, constructors and direct public methods without importing or executing the source."

> "The acceptance criteria require deterministic output, automatic change detection, protection of handwritten documentation, explicit failure handling, and a staged Git documentation gate."

> "Missing docstrings are shown as Not Found rather than being invented by an AI. Dynamic APIs, inherited members, annotation rendering and non-Python parsing are outside the implemented scope."

> "The workflow criteria also require the eight delivery stages, ten agent configurations, reusable customizations, real test evidence, and a structured PR description."

**Reviewer checkpoint:** Ask the reviewer to compare the upcoming demonstrations
against AC1-AC5, documentation automation against AC6-AC10, and workflow/evidence
against AC11-AC13.

## 3. Explain architecture and the source of truth

**Do:** Show [architecture](architecture.md) in preview, then the application and infrastructure in [src](../src).

**Say:**

> "The architecture separates coordination from generation. Copilot agents manage bounded engineering tasks, but Python code generates the reference."

> "The core engine is docsync.py. It snapshots sorted source paths and bytes, parses ASTs, renders public declarations, and computes a SHA-256 source fingerprint."

> "The fingerprint includes relative paths and raw source bytes. A comment-only change affects it too, while unchanged input produces identical output."

> "The output is one owned file, docs/api.md. All the other documentation is handwritten and preserved."

> "Before replacement, the engine checks ownership and safe paths, uses a cooperating-writer lock, and rechecks source stability. It writes through a temporary file and atomically replaces the generated document."

> "copilot_hook.py adapts the supported VS Code lifecycle hooks. git_gate.py checks staged Git blobs in an isolated temporary workspace, rather than trusting the working tree."

> "There are three automation entry points: a polling watcher for editor or external changes, a post-tool hook for supported Copilot hosts, and a Git gate before committing. They reuse the same deterministic generation logic."

**Do:** Open [generated reference](api.md). Point to the ownership marker, fingerprint,
module sections, signatures and descriptions.

**Say:**

> "This is the generated artifact, not manually authored API prose. The marker identifies generator ownership, and the fingerprint connects the document to a specific source snapshot."

> "Default values are replaced with placeholders and annotations are omitted. Private declarations and module variable values are not published. Public docstrings still require human review because the generator is not a secret scanner."

## 4. Run the real project and prove the no-op behavior

**Do:** In the repository terminal:

```powershell
python src\docsync.py sync
$LASTEXITCODE
python src\docsync.py check
$LASTEXITCODE
```

Expected for an already synchronized checkout: `Documentation unchanged`,
then `Documentation is current`, with exit code 0 for each.
On the first run with missing/stale owned output, sync may instead report
`Synchronized docs/api.md`.

**Say:**

> "I am running the application from the project root. Sync generates or updates the reference. Check compares the expected output with the existing document without repairing it."

> "Check has three exit meanings: zero means current, one means missing or stale generated output, and two means an input or operational failure."

**Do:** Prove the second sync does not write:

```powershell
$before = (Get-Item ".\docs\api.md").LastWriteTimeUtc
python src\docsync.py sync
$syncExit = $LASTEXITCODE
$after = (Get-Item ".\docs\api.md").LastWriteTimeUtc
"Sync exit: $syncExit"
"Write timestamp unchanged: $($before -eq $after)"
```

Expected: sync exit 0 and `Write timestamp unchanged: True`.
Do not say it passed if the displayed value is false.

**Say, only after observing the expected result:**

> "The second unchanged run did not rewrite the file. This demonstrates idempotence at the filesystem level, not just similar-looking Markdown."

## 5. Build a safe, isolated live-demo workspace

**Do:** Leave the main repository's source and generated document untouched.
Create a new temporary folder in the first terminal:

```powershell
$engine = Join-Path (Get-Location) "src\docsync.py"
$demo = Join-Path ([System.IO.Path]::GetTempPath()) ("docsync-review-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path (Join-Path $demo "src") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $demo "docs") | Out-Null
@'
"""Small public API used only for the reviewer demonstration."""

def greet(name, punctuation="!"):
    """Return a friendly greeting."""
    return f"Hello, {name}{punctuation}"

def undocumented(value):
    return value

def _internal():
    """This private helper should not appear in the reference."""
    return None
'@ | Set-Content -LiteralPath (Join-Path $demo "src\sample.py") -Encoding utf8
"Engine: $engine"
"Demo root: $demo"
python $engine sync --root $demo
python $engine check --root $demo
```

Open the printed demo root through **File > Open Folder** in a separate VS Code
window, or open its two files in the existing window:

- The temporary `src\sample.py`
- The temporary `docs\api.md`

Use the printed absolute path, not the main repository's files.
The `--root` option directs the engine to this workspace's source/output.
Only this newly created demonstration folder will be edited below.

**Say:**

> "For source edits, I am using a separate temporary workspace. This prevents demonstration changes from contaminating the implementation branch or overwriting anyone's existing work."

> "The same engine can document another workspace through the root option. There is no second implementation for the demo."

**Do:** Show the temporary reference.

**Say, after inspecting it:**

> "The documented greeting appears with a default placeholder, not its literal default value. The undocumented public function says Not Found, and the private helper is excluded."

## 6. Show drift detection before automatic repair

**Do:** With no watcher running yet, change the temporary source's greeting
docstring to the following and save:

```python
    """Return a personalized greeting for the reviewer."""
```

Run in the first terminal:

```powershell
python $engine check --root $demo
$LASTEXITCODE
```

Expected: documentation drift message and exit 1.
Then:

```powershell
python $engine sync --root $demo
python $engine check --root $demo
$LASTEXITCODE
```

Expected: synchronization followed by current documentation and exit 0.

**Say:**

> "I changed the source description but did not regenerate the document. Check now detects the mismatch and returns one."

> "After sync, the reference contains the revised description and check returns zero. Detection and repair are separate operations, which is useful for verification and commit gates."

## 7. Show automatic watcher updates

### 7.1 Start the watcher

**Do:** In the second terminal, substitute the two absolute paths printed in section 5:

```powershell
python "C:\YOUR\PROJECT\src\docsync.py" watch --root "C:\YOUR\TEMP\docsync-review-ID" --interval 0.25
```

Keep this terminal visible. Expected startup: `Watching src; press Ctrl+C to stop`.
The watcher synchronizes the initial snapshot and then polls.

**Say:**

> "The watcher is now running with a quarter-second polling interval. It detects a change on a polling pass, plus the time needed to process it; it is not an instantaneous event stream or an installed background service."

### 7.2 Demonstrate a function addition

**Do:** Add this to the temporary source and save:

```python
def farewell(name):
    """Return a farewell message."""
    return f"Goodbye, {name}"
```

Wait for `Synchronized docs/api.md`; inspect the temporary reference.
If VS Code warns about an externally changed document, reload it rather than
saving an older editor buffer over the generated file.

**Say, after observing the update:**

> "I added a public function and saved the source. The watcher regenerated the reference without my running sync manually. The new signature, description and source fingerprint are visible."

### 7.3 Demonstrate nested discovery and rename

**Do:** Under the temporary `src` folder, create a `helpers` folder and a
`formatting.py` file:

```python
"""Formatting helpers for the demonstration."""

def upper_name(name):
    """Return the supplied name in uppercase."""
    return name.upper()
```

Save, wait for synchronization, and show its module section.
Rename this demo file to `text.py`, wait again, and inspect the reference.

**Say:**

> "Discovery is recursive. This nested module appears automatically. Renaming it updates the documented source path and fingerprint rather than leaving the old module section behind."

### 7.4 Demonstrate deletion

**Do:** Remove the `farewell` function from the temporary source and save.
Delete only the temporary `helpers\text.py` you just created.
Keep `sample.py` present. Wait for synchronization.

**Say, after inspecting the reference:**

> "The deleted function and module disappear from the reference. This demonstrates additions, edits, renames and deletions using the same snapshot mechanism."

## 8. Demonstrate safe failure, recovery and no source execution

### 8.1 Break syntax without destroying the last good document

**Do:** Keep the watcher running. In the first terminal:

```powershell
$goodHash = (Get-FileHash -LiteralPath (Join-Path $demo "docs\api.md") -Algorithm SHA256).Hash
```

Temporarily change the demo function header to `def greet(` and save.
Wait for the watcher to report an error. Then:

```powershell
python $engine check --root $demo
$failureExit = $LASTEXITCODE
$afterFailure = (Get-FileHash -LiteralPath (Join-Path $demo "docs\api.md") -Algorithm SHA256).Hash
"Check exit: $failureExit"
"Last good document preserved: $($goodHash -eq $afterFailure)"
```

Expected: exit 2 and preservation `True`.

**Say, after observing those values:**

> "Invalid syntax is an operational failure, not normal documentation drift. Check returns two, the watcher reports the error, and the last good generated document remains unchanged."

**Do:** Restore the valid header:

```python
def greet(name, punctuation="!"):
```

Change its docstring to `"""Return a greeting after recovery."""` and save.
Wait for synchronization and recovery messages, then run:

```powershell
python $engine check --root $demo
$LASTEXITCODE
```

**Say, after a successful check:**

> "After repairing the source, the watcher recovers without a restart, synchronizes the valid edit, and check returns zero again."

### 8.2 Prove the parser does not execute documented source

**Do:** After the demo module docstring, add:

```python
raise RuntimeError("This module must not be executed by documentation sync")
```

Save and wait for the watcher. Run the demo check again.
Do not run the demo source as a Python program.

**Say, if generation and check succeed:**

> "This source would raise an exception if imported or executed. Documentation still synchronizes because the engine parses syntax rather than running the module."

> "This is evidence of the no-source-execution requirement. It is not a claim that the filesystem or Copilot tools run inside a security sandbox."

### 8.3 Stop the watcher

**Do:** Press Ctrl+C in the watcher terminal. Confirm it returns to the prompt.

**Say:**

> "I am stopping the watcher explicitly. Editor changes will no longer synchronize through this watcher until it is started again."

## 9. Show tests and the staged Git gate

### 9.1 Full verification

**Do:** Return to the main repository terminal:

```powershell
python -m unittest discover -s tests -v
$LASTEXITCODE
python src\docsync.py check
$LASTEXITCODE
```

**Say before running:**

> "The verification suite includes unit tests, real watcher recovery, hook adapter behavior, staged-index validation, customization contracts, and generated-document quality checks."

**Say after reading the output:**

> "These are the actual results from this run. I will report the displayed test count, runtime, failures and skips rather than claiming an unobserved pass."

If the symlink test skips:

> "The real symlink integration test is skipped because this Windows environment lacks the required privilege. Controlled rejection paths are tested, but that is not equivalent to a successful real symlink run."

**Do:** Open [test report](test-report.md). Explain that historical evidence and
new live output are distinct. Do not claim Python 3.11 itself was tested unless it was.

### 9.2 Demonstrate the gate safely through its real Git integration test

**Do:**

```powershell
python -m unittest discover -s tests -p test_automation.py -k partial_staging -v
$LASTEXITCODE
```

This test creates temporary Git repositories and exercises the installed
pre-commit hook and partial-staging rejection. It does not stage demo changes
or commit in the main checkout. Inspect whether it passed or skipped.

**Say:**

> "The gate validates the Git index, which is the snapshot about to be committed. An up-to-date working-tree document cannot conceal stale staged documentation."

> "This integration test exercises matching staged content, stale partial staging, and the installed pre-commit gate in temporary repositories. I am not changing the main project's index during the presentation."

> "In normal development, I synchronize first and stage the matching source and generated document together. The gate never stages files for me and must not be bypassed."

Optional, read-only observation of the current index:

```powershell
python src\git_gate.py
$LASTEXITCODE
```

An index failure may concern the staged snapshot even when working-tree `check`
passes. Explain it; do not repair by blindly running `git add .`.
A direct gate run alone is not proof that Git will invoke an installed hook.

## 10. Explain all eight SDLC stages

**Do:** Show [workflow](workflow.md) and [agent catalog](agent-catalog.md).

**Say:**

> "There are eight stages and ten agent configurations: one Orchestrator and nine specialists. Documentation Sync is a specialist within implementation, so nine specialists do not mean nine SDLC stages."

| Stage | Show | Exact words to say |
|---|---|---|
| 1. Requirements | [Requirements](requirements.md) | "Requirements clarifies the supplied brief and records the single story, functional requirements, constraints and acceptance criteria." |
| 2. Architecture | [Architecture](architecture.md) | "Architecture defines the components, data flow, technology choices and contracts, including the Mermaid diagram." |
| 3. Design Review | [Design review](design-review.md) | "Design Review identifies risks before implementation. Human scope and design decisions gate development; a handoff button does not manufacture approval." |
| 4. Planning | [Implementation plan](impl-plan.md) | "Planning orders tasks by actual dependencies, so work does not begin before its prerequisites are resolved." |
| 5. Implementation | [Source](../src) and [API reference](api.md) | "Development implements approved source and tests. Documentation Sync then runs the deterministic engine; it does not ask a language model to author the generated API." |
| 6. Review | [Code review](code-review.md) | "Code Review evaluates correctness, security, error handling, coverage, clarity, duplication and dependency safety. Its tools are read-only." |
| 7. Verify | [Test report](test-report.md) | "Testing records handed-off review findings verbatim and runs executable verification. It records failures and skips instead of treating predictions as evidence." |
| 8. PR Management | [Changelog](../CHANGELOG.md) and [PR description](pr-description.md) | "PR Management prepares the required delivery sections. Local commits, publication and merge are separate human permission boundaries." |

**Say:**

> "The Orchestrator supplies bounded inputs, reuses completed artifacts and delegates only the current stage. It coordinates but does not implement or execute commands."

> "Each role returns Changed, Evidence, Risks and Next gate. Repair loops return to the affected specialist, with at most two attempts before asking the human."

> "The sequential handoffs use send false, so they require manual confirmation. This keeps the workflow human-gated rather than silently advancing."

## 11. Explain agents, instructions, skills, prompts and hooks

**Do:** Expand [.github](../.github) in Explorer.

**Say:**

> "Agents define role-specific responsibilities and available tools. Instructions carry shared or file-scoped rules. Skills package reusable procedures. Prompts provide focused entry points. Hooks run deterministic lifecycle commands where the host supports them."

> "The main prompt entry points are start-sdlc, sync-docs and verify. The project also contains similarly named reusable skills, so I inspect the selected entry rather than assuming every slash completion is the same thing."

> "The Python and documentation instructions are scoped to the relevant files. Only the sync engine writes the generated API, while handwritten documents are preserved."

> "The pre-tool adapter allows known read operations and requests approval for non-read or unknown tools. The post-tool adapter runs synchronization after approved tool use."

> "These controls depend on a supporting trusted host. They are defense in depth, not operating-system isolation, and terminal execution outside that host is not automatically protected by those hooks."

**Do:** Show [Orchestrator configuration](../.github/agents/orchestrator.agent.md),
[Code Review configuration](../.github/agents/code-review.agent.md),
[Testing configuration](../.github/agents/testing.agent.md), and
[hook configuration](../.github/hooks/docsync.json).

**Say:**

> "A deliberate tool boundary is visible here: Code Review has no edit tool. Its findings are handed to Testing, which can record the report. The Orchestrator must not pretend it can write the review file."

## 12. Run agents only if required: recommended live sequence

You do not need to rerun all historical stages to prove the engine works.
A compact live showcase is a bounded Orchestrator delegation, Documentation Sync,
Code Review and Testing. Use the current supported host; do not simulate unavailable tools.

### 12.1 Select an agent or a prompt

1. Open Copilot Chat.
2. Use the agent picker to select the named custom agent.
3. Start a fresh chat for an independent task, or retain the relevant review
   conversation for its Testing handoff.
4. Paste the bounded prompt below.
5. Inspect proposed tools and approve only the stated operations.
6. Wait for completion and inspect actual changed paths and execution output.
7. Do not advance if a task reports blockers.

Alternatively type `/` and choose the intended prompt entry:
[start-sdlc](../.github/prompts/start-sdlc.prompt.md),
[sync-docs](../.github/prompts/sync-docs.prompt.md), or
[verify](../.github/prompts/verify.prompt.md).
If slash entries are missing or ambiguous, select the custom agent and paste the prompt.

### 12.2 Orchestrator: demonstrate one bounded delegation

**Select:** Orchestrator.

**Paste into Copilot:**

```text
Reviewer demonstration for US-001. Reuse the existing requirements, architecture,
design review, plan and test report. Do not restart the full SDLC or assume a new
approval. Delegate only a read-only review to Code Review of the current
src/docsync.py, src/copilot_hook.py, src/git_gate.py and their tests against
AC1-AC5 and the seven review areas. Supply those bounded inputs. No edits,
commands, commits, publication or merge. Return Changed / Evidence / Risks /
Next gate, and stop after the specialist result. If delegation is unavailable,
report that blocker; do not pretend the specialist ran.
```

**Say:**

> "This request deliberately delegates one current task, not the whole pipeline. I will show the actual specialist invocation if the host supports it."

**Evidence to show:** The real delegation/tool record, the Code Review response,
and the Orchestrator's stop at the next gate. A description of delegation without
an invocation is not proof of agent execution.

### 12.3 Documentation Sync: execute the application through an agent

**Select:** Documentation Sync, or the intended `/sync-docs` prompt.

**Paste into Copilot:**

```text
Run a bounded US-001 synchronization demonstration in this workspace. Use the
documentation-sync skill: run python src\docsync.py sync, then
python src\docsync.py check. Only the engine may update docs/api.md.
Preserve handwritten documents and all existing uncommitted work. Report actual
commands, exit codes and changed/unchanged output. Stop on failure. Do not edit
source, stage, commit, push, create a PR or merge. Request host tool approval
where required.
```

**Say:**

> "This agent executes the existing engine and reports its real result. The language model coordinates the action; Python still owns generation."

**Evidence to show:** Actual command execution and result, not just a suggested command.

### 12.4 Code Review: standalone alternative

Skip this if section 12.2 already produced the required review.

**Select:** Code Review.

**Paste into Copilot:**

```text
Read-only US-001 review. Compare src/docsync.py, src/copilot_hook.py,
src/git_gate.py and their tests with docs/requirements.md and the seven review
areas in the supplied brief. Return findings with file/line, severity, evidence
and proposed fix, or an explicit no-findings result within this scope. Preserve
all files; do not run commands, claim tests ran or self-approve. Return Changed /
Evidence / Risks / Next gate. Propose the Testing handoff only if no blocking
findings remain.
```

**Say:**

> "The reviewer agent is intentionally read-only. If it finds a blocking issue, I stop the demonstration workflow and route the issue for an approved fix rather than presenting delivery as complete."

### 12.5 Testing: record review and execute verification

If a review just completed without blockers, click **Verify reviewed implementation**.
The handoff is not auto-sent; inspect it and confirm manually.
When using a fresh Testing chat, attach the complete, unmodified review response.
If that response is unavailable, do not reconstruct findings from memory.

**Select:** Testing, or the intended `/verify` prompt for verification without a new review.

**Paste into Copilot:**

```text
US-001 verification demonstration. I approve updating only docs/code-review.md
with the complete review findings handed off in this conversation, and
docs/test-report.md with actual verification evidence. Preserve existing report
history and unrelated work. If no review was supplied, do not invent one or
modify the code-review report. If blocking review findings remain, stop.
Use the verification skill: run python -m unittest discover -s tests -v and
python src\docsync.py check. Record exact commands, output, runtimes, exit codes
and skips. Do not repair source, change policy, stage, commit, push, publish or
merge. Stop with Changed / Evidence / Risks / Next gate.
```

**Say:**

> "I am authorizing only the report updates and verification in this prompt. That is not permission to commit, publish or merge."

> "Testing records the review verbatim before verification when findings are handed off. It distinguishes executable local results from unverified Copilot-host behavior."

**Evidence to show:** Actual test output, drift output, report changes and explicit next gate.

### 12.6 Observe hooks without making a risky policy change

If the supporting host exposes hook logs, inspect the lifecycle records for the
approved non-read operation and post-tool synchronization above.
Observe an approval request before an operation, and the actual post-tool result afterward.

Do not run a watcher against the same source during a hook-only demonstration:
otherwise the watcher could update the document and obscure which trigger caused it.
A post-tool `Documentation unchanged` result proves that hook invocation only if
the host log identifies it; it does not by itself prove automatic post-edit repair.

**Say when host logs establish the invocation:**

> "The host shows the configured hook invocation around this approved operation. This is live-host evidence, separate from the adapter's unit tests."

**Say if host support or evidence is absent:**

> "I cannot verify hook loading in this host. The adapter is tested locally, and the watcher and Git gate remain independent executable alternatives. I am not claiming a live hook demonstration succeeded."

For a denied-approval demonstration, reject a harmless proposed report update
before it executes. Verify no edit/command proceeds, then stop that attempt.
Never use push, deletion, merge or a policy change as a theatrical approval test.

## 13. Optional: exact prompts for the remaining specialists

Use these only if the reviewer asks to see every role. These prompts inspect
completed artifacts rather than regenerating them. Running one read-only
walkthrough per role is not proof that each role originally authored the artifacts.

| Select agent | Paste into Copilot |
|---|---|
| Requirements | "US-001 artifact walkthrough only. Read the supplied capstone brief and docs/requirements.md. Explain the existing scope, functional and non-functional requirements, AC1-AC8 and unresolved facts. Ask only about an actual unresolved requirement. Do not add another story, edit files, execute commands or invent approval. Return Changed / Evidence / Risks / Next gate and stop." |
| Architecture | "US-001 artifact walkthrough only. Read docs/requirements.md and docs/architecture.md. Explain the existing components, data flow, AST choice, ownership marker, fingerprint, lock and atomic replacement. Identify any concrete gap with evidence. Do not redesign, edit files or execute commands. Return Changed / Evidence / Risks / Next gate and stop." |
| Design Review | "US-001 artifact walkthrough only. Read docs/requirements.md, docs/architecture.md and docs/design-review.md. Explain existing decisions and residual risks. Identify unresolved blockers without claiming human design approval. Do not modify artifacts or execute commands. Return Changed / Evidence / Risks / Next gate and stop before implementation." |
| Planning | "US-001 artifact walkthrough only. Read docs/design-review.md and docs/impl-plan.md. Explain P1-P8, actual dependencies and the pending human review/merge gate. Reuse the plan; do not add tasks, edit files or execute commands. Return Changed / Evidence / Risks / Next gate and stop." |
| Development | "US-001 implementation walkthrough only. Read the approved plan, applicable Python instructions and current src/tests. Explain how the existing implementation satisfies AC1-AC5 and identify any concrete blocker. This prompt approves no implementation changes or commands. Preserve files, do not edit generated docs, and return Changed / Evidence / Risks / Next gate and stop." |
| PR Management | "US-001 delivery walkthrough only. Read docs/code-review.md, docs/test-report.md, CHANGELOG.md and docs/pr-description.md. Explain the five required PR sections and separate commit, publication and merge gates. Treat remote status in these files as dated evidence, not a fresh query. Do not edit files, run commands, stage, commit, push, create another PR or merge. Return Changed / Evidence / Risks / Next gate and stop." |

**Say:**

> "These bounded walkthroughs demonstrate the configured roles responding to their inputs. I am reusing completed work, not spending tokens or creating new changes merely to reenact history."

If the reviewer requests a real new implementation, clarify and approve that
change separately before Development. Follow the existing stage sequence:
Requirements -> Architecture -> Design Review -> human gate -> Planning ->
Development -> Documentation Sync -> Code Review -> Testing -> delivery gates.
Do not treat a read-only walkthrough as approval for production edits.

## 14. Show PR delivery honestly

**Do:** Open [PR description](pr-description.md) and [changelog](../CHANGELOG.md).
Show Summary, Changes Made, Test Evidence, Known Limitations and Reviewer Checklist.

**Say:**

> "The PR description contains all five required sections and links to executable evidence. The reviewer checklist includes content review, tests, automation, agent-host confirmation and human delivery approvals."

> "The repository documents that PR number one was published from capstone/us-001 into main and verified open on November eighth, twenty twenty-six. That is historical evidence, not a fresh remote-status claim."

If GitHub CLI is already installed/authenticated and remote access is allowed,
refresh read-only status:

```powershell
gh pr view 1 --repo deepakkumar-r/automated-documentation-sync --json url,state,isDraft,mergeable,baseRefName,headRefName,reviews,statusCheckRollup
```

Inspect the actual response. If `mergeable` is unknown, do not call it mergeable.
If the CLI fails, disclose the failure instead of asserting current status.
No checks shown means no demonstrated CI result, not a CI pass.

**Say after reading a successful query:**

> "This is the live PR state returned by GitHub. Publication is separate from human review and merge, and mergeability is not the same as approval."

**Say:**

> "I will not create a duplicate PR or merge as part of this showcase. Any delivery action needs its own explicit approval."

## 15. Likely reviewer questions: exact answers

### Why not let Copilot generate the whole API document?

> "API extraction is deterministic work. AST generation avoids invented API semantics, reduces model-token use for regeneration, and gives checkable output. Copilot remains useful for requirements, design, implementation, review and orchestration."

### Why AST instead of importing modules?

> "Importing can execute arbitrary module code and require runtime dependencies. AST parsing extracts the supported declarations without execution. The trade-off is that dynamic and inherited APIs are outside scope."

### Does every change trigger documentation?

> "With the watcher running, polling detects source changes and output drift. With supported Copilot hooks, approved tool use triggers sync. The staged Git gate checks the commit snapshot. Without an active automation entry point, I must run sync manually."

### What happens when a source file has no docstring?

> "The output explicitly says Not Found. It does not infer a description. A reviewer can see the gap and decide whether the public API needs a handwritten source docstring."

### What if source syntax is invalid or every source file is deleted?

> "The operation fails explicitly and preserves the last good document. Check uses exit two for input or operational failure, while the watcher reports the error and can recover after valid source is restored."

### Is it secure against every threat?

> "No. It avoids executing documented source, omits defaults and variable values, escapes rendered text and rejects unsafe paths and foreign output. Public docstrings still need secret review. The filesystem and supporting host are trusted; this is not a sandbox or a complete secret-detection system."

### Why check staged files instead of working-tree files?

> "Git commits the index. Partial staging can make the index differ from the working tree, so the gate reconstructs staged source and documentation in isolation and checks that exact snapshot."

### Have all ten agents actually run?

> "Ten configurations and their local contracts are tested. I only claim live execution for the agents whose invocation and output we actually observed. Configuration presence alone is not proof that every agent ran."

### Is the entire capstone finished through merge?

> "The engine, workflow configurations, artifacts and local tests are implemented. The project records PR publication, but current remote state must be verified. Human review, separate merge approval, and any unverified host acceptance remain explicit gates; I do not claim completion through merge."

### What would you improve next?

> "Within separately approved scope, I would confirm supported-host discovery, delegation and hooks, test the minimum Python version directly, and run real symlink integration in a permitted environment. Additional API coverage or CI would be new scope, not features I am claiming today."

## 16. Troubleshooting during the review

| Observation | Action and exact words |
|---|---|
| `python` is missing or older than 3.11 | Stop executable steps. "The required interpreter is unavailable. I can explain the artifacts, but I will not claim a live run or install software without approval." |
| Check returns 1 | Investigate source/output drift; run engine sync only when appropriate. "This is a detected stale or missing generated document, not an operational crash." |
| Check returns 2 | Read the reported error and inspect only the affected input/path/ownership/lock. "The engine is refusing an unsafe or invalid operation; I am not bypassing the failure." |
| Watcher appears inactive | Confirm the correct absolute demo root, saved source and running terminal. "The watcher must be running against the edited workspace; I will verify the path before claiming automation." |
| Generator refuses foreign output | Leave the existing file alone; use the fresh demo root. "This ownership check protects handwritten or unrelated output." |
| Stale lock is reported | Inspect the recorded PID and ownership; do not delete blindly. "The lock requires investigation, not automatic removal during a presentation." |
| Agents/prompts are missing | Reload the window once; use picker/pasted prompts if available. "This host has not established customization discovery. The terminal application remains independently demonstrable." |
| Hook evidence is missing | Use watcher and adapter tests, disclose host gap. "Local hook tests are not proof of live host loading." |
| Review finds a blocker or tests fail | Stop progression and retain actual evidence. "I will return the affected issue for an approved repair rather than advance with a false success." |
| Git integration skips | Show the skip reason. "This environment did not execute that integration check, so I am not counting it as a pass." |
| Remote query fails | Show dated local evidence only. "Current remote state is unavailable; I will not infer it from an older report." |

## 17. Closing, cleanup and final reviewer takeaway

**Do:**

1. Confirm the watcher is stopped.
2. Close temporary generated-document tabs without saving stale buffers.
3. Show the main repository state:

```powershell
git --no-pager status --short
python src\docsync.py check
$LASTEXITCODE
```

4. Compare with preflight status. Retain all pre-existing changes and any explicitly
   approved report updates. Do not use reset, checkout, blanket staging or cleanup.
5. The temporary demo folder is disposable. Remove only that exact printed folder
   after inspecting it and confirming it contains only your demo files. If unsure,
   leave it and disclose its location; never recursively clean the repository or temp root.

**Say:**

> "The demonstration showed deterministic generation, drift detection, automatic watcher updates, nested additions and renames, deletion handling, explicit missing documentation, no source execution, and recovery without losing the last good document."

> "The tests and staged-index gate provide executable verification. The Copilot workflow adds bounded roles, reusable customizations and human approval gates without making the language model the source of truth for generated APIs."

> "My final distinction is between implemented behavior and verified delivery state. I have shown the evidence that actually ran, disclosed skips and host limitations, and left review and merge under human control."

> "That completes my project walkthrough. I am ready for your questions and for any specific acceptance criterion you would like me to demonstrate again."

## Final rehearsal checklist

- [ ] Correct implementation checkout and Python 3.11+ are available.
- [ ] Existing uncommitted work is understood and preserved.
- [ ] Requirements, architecture, workflow and API tabs are ready.
- [ ] Sync/check and no-write timestamp demonstration are rehearsed.
- [ ] Temporary demo root is separate from the repository.
- [ ] Drift, watcher, nested rename/delete, syntax failure and recovery are rehearsed.
- [ ] No-source-execution example is parsed, never executed.
- [ ] Tests and skips are read aloud from actual output.
- [ ] Real Git integration is shown without touching the main index.
- [ ] Optional agents are visible; only bounded tasks are authorized.
- [ ] Hook evidence and agent invocation are not overstated.
- [ ] Historical PR evidence is distinguished from a live query.
- [ ] No commit, push, duplicate PR or merge occurs without separate approval.
- [ ] Watcher is stopped and demo-only cleanup is scoped.
