"""VS Code Copilot lifecycle adapter; input never becomes an executable command."""

from __future__ import annotations

import argparse
import json
import sys

import docsync

READ_TOOLS = {
    "read", "search", "view", "rg", "glob", "read_file", "list_dir",
    "file_search", "grep_search", "semantic_search",
}
def permission(payload: dict[str, object]) -> dict[str, object]:
    """Allow known reads; request human approval for every other tool."""
    name = payload.get("tool_name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("tool_name must be a nonempty string")
    tool = name.rsplit("/", 1)[-1].rsplit(".", 1)[-1]
    decision = "allow" if tool in READ_TOOLS else "ask"
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": (
                "Known read-only tool" if decision == "allow"
                else "Human approval required for writes, execution or unknown tools"
            ),
        }
    }


def main(argv: list[str] | None = None) -> int:
    """Validate hook input and return the VS Code permission or sync result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event", choices=("pre", "post"))
    args = parser.parse_args(argv)
    try:                               
        raw = sys.stdin.read(1_048_577)
        if len(raw) > 1_048_576:
            raise ValueError("Hook input exceeds 1 MiB")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("Hook input must be a JSON object")
        if not isinstance(payload.get("tool_name"), str) or not payload["tool_name"].strip():
            raise ValueError("tool_name must be a nonempty string")
        if args.event == "pre":
            result = permission(payload)
        else:
            changed = docsync.sync(docsync.DEFAULT_ROOT)
            result = {"systemMessage": "Documentation synchronized" if changed else "Documentation unchanged"}
        print(json.dumps(result))
        return 0
    except (ValueError, OSError, docsync.SyncError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        if args.event == "post":
            print(json.dumps({"decision": "block", "reason": str(error)}))
        else:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": str(error),
                }
            }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
