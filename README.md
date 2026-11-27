# Daily Expense Tracker - Agentic Documentation Sync

Daily Expense Tracker is US-001, the only story in this capstone. The repository
preserves local expense data, the responsive HTML/CSS/JavaScript frontend, ten Copilot
custom agents, eight-stage SDLC, Markdown artifacts and human approval gates.

## Documentation synchronisation

Documentation is synchronised by the `Documentation Sync` Copilot agent using
the [sync-docs skill](.github/skills/sync-docs/SKILL.md) and
[/sync-docs prompt](.github/prompts/sync-docs.prompt.md). No Python or Java
documentation engine is present.

GitHub Actions detects added, modified and deleted files, publishes a change
manifest, validates the agent configuration and runs the optional frontend
test. The agent maps changed functionality to only the relevant
`docs/api.md`, `docs/architecture.md`, `docs/ui.md`, `README.md`,
`docs/test-report.md` and `CHANGELOG.md` sections. Unrelated handwritten
documentation is preserved.

The workflow is defined in
[documentation-sync.yml](.github/workflows/documentation-sync.yml). The
supported VS Code hook in
[docsync.json](.github/hooks/docsync.json) exposes changed-file information;
it does not execute application or documentation code.

## Frontend

The preserved frontend is under [src/static](src/static). It is dependency-free
HTML, CSS and JavaScript and can be served by any approved local static server.
The local JSON store remains runtime data and is ignored by Git. The Java
backend is dependency-free and runs locally with the JDK. Node.js is
used only when available for the frontend regression test.

Start the application from the workspace root:

```powershell
javac --add-modules jdk.httpserver -d .build src\web.java
java -cp .build web
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Expenses are persisted
atomically in the ignored local `expenses-java.json` file. Stop the server with
Ctrl+C.

## Agentic SDLC

Run the workflow in trusted VS Code with Copilot custom-agent support. Start
with **Orchestrator** or `/start-sdlc`; use `/sync-docs` for bounded
documentation updates and `/verify` for validation. Requirements and design
decisions remain human approval gates. Agents must report executed evidence and
must not invent approvals, test results, commits or remote publication.

See [requirements](docs/requirements.md),
[architecture](docs/architecture.md), [workflow](docs/workflow.md), and the
[agent catalog](docs/agent-catalog.md).
