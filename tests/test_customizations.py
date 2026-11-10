"""Contract checks for this repository's constrained YAML and Markdown artifacts."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import docsync

AGENTS = {
    "Orchestrator", "Requirements", "Architecture", "Design Review", "Planning",
    "Development", "Documentation Sync", "Code Review", "Testing", "PR Management",
}


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise AssertionError(f"Missing YAML frontmatter: {path}")
    header = text.split("---\n", 2)[1]
    if "\t" in header:
        raise AssertionError(f"Tabs in YAML frontmatter: {path}")
    return header


class CustomizationTests(unittest.TestCase):
    def test_exactly_ten_agents_and_resolvable_handoffs(self) -> None:
        files = list((ROOT / ".github" / "agents").glob("*.agent.md"))
        self.assertEqual(len(files), 10)
        names = set()
        for path in files:
            header = frontmatter(path)
            name = re.search(r"^name: (.+)$", header, re.MULTILINE)
            self.assertIsNotNone(name, path)
            names.add(name.group(1))
            description = re.search(r'^description: (".+")$', header, re.MULTILINE)
            self.assertIsNotNone(description, path)
            self.assertTrue(json.loads(description.group(1)))
            self.assertRegex(header, r"tools: \[[^\n]+\]")
            self.assertNotRegex(header, r"(?m)^model:")
            self.assertNotIn("send: true", header)
            for target in re.findall(r"^\s+agent: (.+)$", header, re.MULTILINE):
                self.assertIn(target, AGENTS)
        self.assertEqual(names, AGENTS)

    def test_orchestrator_allowlist_and_readonly_review(self) -> None:
        header = frontmatter(ROOT / ".github" / "agents" / "orchestrator.agent.md")
        self.assertIn("tools: [read, search, agent]", header)
        allowed = re.search(r"^agents: \[(.+)\]$", header, re.MULTILINE).group(1)
        self.assertEqual(set(allowed.split(", ")), AGENTS - {"Orchestrator"})
        review = frontmatter(ROOT / ".github" / "agents" / "code-review.agent.md")
        self.assertIn("tools: [read, search]", review)

    def test_skills_prompts_and_scoped_instructions(self) -> None:
        for path in (ROOT / ".github" / "skills").glob("*/SKILL.md"):
            header = frontmatter(path)
            self.assertIn(f"name: {path.parent.name}\n", header)
            self.assertIn("description:", header)
        for path in (ROOT / ".github" / "prompts").glob("*.prompt.md"):
            header = frontmatter(path)
            target = re.search(r"^agent: (.+)$", header, re.MULTILINE).group(1)
            self.assertIn(target, AGENTS)
            self.assertIn("description:", header)
        for path in (ROOT / ".github" / "instructions").glob("*.instructions.md"):
            header = frontmatter(path)
            value = re.search(r'^applyTo: (".+")$', header, re.MULTILINE).group(1)
            self.assertNotEqual(json.loads(value), "**")
            self.assertIn("description:", header)

    def test_hook_contract_and_commands(self) -> None:
        config = json.loads((ROOT / ".github" / "hooks" / "docsync.json").read_text(encoding="utf-8"))
        self.assertEqual(set(config["hooks"]), {"PreToolUse", "PostToolUse"})
        for event, argument in (("PreToolUse", "pre"), ("PostToolUse", "post")):
            hook = config["hooks"][event][0]
            self.assertEqual(hook["type"], "command")
            self.assertEqual(hook["command"], f"python src/copilot_hook.py {argument}")
            self.assertEqual(hook["windows"], f"python src\\copilot_hook.py {argument}")
            self.assertEqual(hook["cwd"], ".")
            self.assertGreater(hook["timeout"], 0)
        gate = (ROOT / ".github" / "hooks" / "pre-commit").read_bytes()
        self.assertTrue(gate.startswith(b"#!/bin/sh\n"))
        self.assertNotIn(b"\r", gate)
        self.assertIn(b"exec python src/git_gate.py", gate)

    def test_deliverables_one_story_and_diagrams(self) -> None:
        names = (
            "requirements.md", "architecture.md", "design-review.md", "impl-plan.md",
            "agent-catalog.md", "workflow.md", "guardrails.md", "test-report.md",
            "code-review.md", "api.md", "pr-description.md",
        )
        for name in names:
            self.assertTrue((ROOT / "docs" / name).is_file(), name)
        requirements = (ROOT / "docs" / "requirements.md").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"US-\d+", requirements)), {"US-001"})
        self.assertEqual(len(re.findall(r"^## US-", requirements, re.MULTILINE)), 1)
        for name in ("architecture.md", "workflow.md"):
            self.assertIn("```mermaid\n", (ROOT / "docs" / name).read_text(encoding="utf-8"))
        workflow = (ROOT / "docs" / "workflow.md").read_text(encoding="utf-8")
        for stage in range(1, 9):
            self.assertRegex(workflow, rf"\| {stage} [A-Za-z]")

    def test_expense_scope_and_preserved_infrastructure(self) -> None:
        for name in ("requirements.md", "architecture.md", "impl-plan.md"):
            text = (ROOT / "docs" / name).read_text(encoding="utf-8")
            self.assertIn("Daily Expense Tracker", text)
            self.assertIn("SQLite", text)
        for path in (ROOT / ".github" / "agents").glob("*.agent.md"):
            self.assertIn("Daily Expense Tracker", path.read_text(encoding="utf-8"), path)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for command in ("add", "view", "update", "delete", "total"):
            self.assertIn(f"expenses.py {command}", readme)
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*.sqlite3", ignored)
        for module in ("expenses.py", "docsync.py", "copilot_hook.py", "git_gate.py"):
            self.assertTrue((ROOT / "src" / module).is_file())

    def test_pr_sections_and_file_manifest(self) -> None:
        draft = (ROOT / "docs" / "pr-description.md").read_text(encoding="utf-8")
        for section in ("Summary", "Changes Made", "Test Evidence", "Known Limitations", "Reviewer Checklist"):
            self.assertIn(f"## {section}\n", draft)
        actual = {
            path.relative_to(ROOT).as_posix()
            for folder in (".github", "src", "tests", "docs")
            for path in (ROOT / folder).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        actual.update({".gitignore", ".gitattributes", "README.md", "CHANGELOG.md"})
        listed = set(re.findall(r"^- `([^`]+)`:", draft, re.MULTILINE))
        self.assertEqual(listed, actual)

    def test_markdown_relative_links_resolve(self) -> None:
        files = [ROOT / "README.md"]
        for directory in (ROOT / ".github", ROOT / "docs"):
            files.extend(directory.rglob("*.md"))
        for path in files:
            text = path.read_text(encoding="utf-8")
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in link or link.startswith("#"):
                    continue
                target = (path.parent / unquote(link.split("#")[0])).resolve()
                self.assertTrue(target.exists(), f"{path.name}: {link}")

    def test_generated_reference_content_quality(self) -> None:
        output = (ROOT / "docs" / "api.md").read_text(encoding="utf-8")
        self.assertTrue(docsync.check(ROOT))
        self.assertTrue(output.startswith(docsync.MARKER + "# Python API reference"))
        self.assertRegex(output, r"Source fingerprint: `[0-9a-f]{64}`")
        for name, content in docsync.snapshot(ROOT).items():
            self.assertIn(f"<code>{name}</code>", output)
            tree = ast.parse(content)
            self.assertTrue(ast.get_docstring(tree), f"Undocumented module: {name}")
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                    self.assertTrue(ast.get_docstring(node), f"Undocumented declaration: {name}:{node.name}")
        self.assertNotIn("<pre>Not Found</pre>", output)
