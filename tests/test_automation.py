"""Hook contract, staged-index unit tests and real Git integration when available."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import copilot_hook
import docsync
import git_gate


class HookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "example.py").write_text("def example(): pass\n", encoding="utf-8")

    def invoke(self, event: str, raw: str) -> tuple[int, dict, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "stdin", io.StringIO(raw)), patch.object(docsync, "DEFAULT_ROOT", self.root):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = copilot_hook.main([event])
        return code, json.loads(stdout.getvalue()), stderr.getvalue()

    def test_reads_allowed_and_all_writes_execution_unknown_require_approval(self) -> None:
        for tool in ("read_file", "functions.view", "search"):
            result = copilot_hook.permission({"tool_name": tool})
            self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "allow")
        for tool in ("execute", "run_in_terminal", "apply_patch", "create_file", "github/create_pull_request", "new_tool"):
            result = copilot_hook.permission({"tool_name": tool, "tool_input": {"command": "git push"}})
            self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_invalid_input_fails_closed(self) -> None:
        for raw in ("", "{bad", "[]", "{}", '{"tool_name": 2}', '{"tool_name": ""}', "x" * 1_048_577):
            with self.subTest(raw=raw[:40]):
                code, result, error = self.invoke("pre", raw)
                self.assertEqual(code, 2)
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")
                self.assertIn("ERROR:", error)

    def test_post_hook_actually_syncs_source_edits(self) -> None:
        payload = json.dumps({"tool_name": "replace_string_in_file", "tool_input": {}})
        code, result, error = self.invoke("post", payload)
        self.assertEqual((code, error), (0, ""))
        self.assertEqual(result["systemMessage"], "Documentation synchronized")
        self.assertTrue(docsync.check(self.root))
        source = self.root / "src" / "example.py"
        source.write_text("def changed(): pass\n", encoding="utf-8")
        self.invoke("post", payload)
        self.assertIn("changed()", (self.root / "docs" / "api.md").read_text(encoding="utf-8"))
        _, result, _ = self.invoke("post", payload)
        self.assertEqual(result["systemMessage"], "Documentation unchanged")

    def test_post_hook_ignores_untrusted_cwd_and_commands(self) -> None:
        marker = self.root / "should-not-exist"
        payload = json.dumps({"tool_name": "execute", "cwd": "not-a-root", "tool_input": {"command": f"touch {marker}"}})
        self.assertEqual(self.invoke("post", payload)[0], 0)
        self.assertFalse(marker.exists())
        self.assertTrue(docsync.check(self.root))

    def test_post_hook_blocks_on_invalid_source(self) -> None:
        (self.root / "src" / "example.py").write_text("def invalid(", encoding="utf-8")
        code, result, error = self.invoke("post", '{"tool_name":"edit"}')
        self.assertEqual(code, 2)
        self.assertEqual(result["decision"], "block")
        self.assertIn("Cannot parse", error)


class IndexTests(unittest.TestCase):
    def test_staged_snapshot_passes_and_drift_fails_without_git_binary(self) -> None:
        source = b"def indexed(): pass\n"
        document = docsync.render({"src/example.py": source}).encode("utf-8")
        entries = b"100644 aaa 0\tsrc/example.py\0" + b"100644 bbb 0\tdocs/api.md\0"
        with patch.object(git_gate, "git", side_effect=[entries, source, document]):
            self.assertTrue(git_gate.check_index(Path(".")))
        with patch.object(git_gate, "git", side_effect=[entries, b"def changed(): pass\n", document]):
            self.assertFalse(git_gate.check_index(Path(".")))

    def test_staged_missing_output_is_drift(self) -> None:
        entries = b"100644 aaa 0\tsrc/example.py\0"
        with patch.object(git_gate, "git", side_effect=[entries, b"pass\n"]):
            self.assertFalse(git_gate.check_index(Path(".")))

    def test_unsafe_conflicted_and_symlink_entries_fail(self) -> None:
        for entry in (
            b"100644 aaa 0\tsrc/../outside.py\0",
            b"100644 aaa 0\t/absolute.py\0",
            b"100644 aaa 0\tsrc\\outside.py\0",
            b"100644 aaa 0\tsrc/C:outside.py\0",
            b"100644 aaa 1\tsrc/conflict.py\0",
            b"120000 aaa 0\tsrc/link.py\0",
            b"120000 aaa 0\tsrc/link\0",
        ):
            with self.subTest(entry=entry), patch.object(git_gate, "git", return_value=entry):
                with self.assertRaises(docsync.SyncError):
                    git_gate.check_index(Path("."))

    def test_no_staged_source_fails_explicitly(self) -> None:
        with patch.object(git_gate, "git", return_value=b""):
            with self.assertRaises(docsync.SyncError):
                git_gate.check_index(Path("."))

    def test_git_command_errors_are_reported(self) -> None:
        result = subprocess.CompletedProcess([], 128, b"", b"fatal: not a repository")
        with patch.object(subprocess, "run", return_value=result):
            with self.assertRaisesRegex(docsync.SyncError, "not a repository"):
                git_gate.git(Path("."), "status")

    def test_git_hook_stdout_failure_is_reported(self) -> None:
        result = subprocess.CompletedProcess([], 1, b"Staged documentation drift", b"")
        with patch.object(subprocess, "run", return_value=result):
            with self.assertRaisesRegex(docsync.SyncError, "drift"):
                git_gate.git(Path("."), "commit", "-m", "test")


@unittest.skipUnless(shutil.which("git"), "Git executable unavailable; staged-blob logic tested separately")
class RealGitTests(unittest.TestCase):
    def test_partial_staging_and_installed_precommit_gate(self) -> None:
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(project / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__"))
            hooks = root / ".github" / "hooks"
            hooks.mkdir(parents=True)
            shutil.copyfile(project / ".github" / "hooks" / "pre-commit", hooks / "pre-commit")
            (hooks / "pre-commit").chmod(0o755)
            git_gate.git(root, "init")
            git_gate.git(root, "config", "user.name", "Documentation Sync Test")
            git_gate.git(root, "config", "user.email", "test@example.invalid")
            git_gate.git(root, "config", "core.autocrlf", "false")
            git_gate.git(root, "config", "core.hooksPath", ".github/hooks")
            docsync.sync(root)
            git_gate.git(root, "add", ".")
            self.assertTrue(git_gate.check_index(root))
            git_gate.git(root, "commit", "-m", "Test synchronized snapshot")
            example = root / "src" / "new.py"
            example.write_text("def new_api(): pass\n", encoding="utf-8")
            git_gate.git(root, "add", "src/new.py")
            docsync.sync(root)
            self.assertTrue(docsync.check(root))
            self.assertFalse(git_gate.check_index(root))
            with self.assertRaisesRegex(docsync.SyncError, "drift"):
                git_gate.git(root, "commit", "-m", "Must reject unstaged documentation")
            git_gate.git(root, "add", "docs/api.md")
            self.assertTrue(git_gate.check_index(root))
            git_gate.git(root, "commit", "-m", "Test updated synchronized snapshot")
