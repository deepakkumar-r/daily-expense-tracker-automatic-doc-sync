"""Unit and live watcher integration tests; all mutations use temporary workspaces."""

from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import docsync


class SyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "src").mkdir()
        self.source = self.root / "src" / "example.py"
        self.source.write_text('"""Example module."""\ndef hello(name):\n    """Greet a name."""\n    return name\n', encoding="utf-8")
        self.output = self.root / "docs" / "api.md"

    def test_public_api_signatures_and_missing_descriptions(self) -> None:
        self.source.write_text(
            '"""<script>alert(1)</script>"""\n'
            'SECRET = "never-publish"\n'
            'def public(a, /, b="never-publish", *items, required, optional=3, **kwargs): pass\n'
            'async def fetch(): pass\n'
            'def _private(): pass\n'
            'class Public:\n'
            '    """Documented class."""\n'
            '    def __init__(self, key="never-publish"): pass\n'
            '    def method(self): pass\n'
            '    def _hidden(self): pass\n',
            encoding="utf-8",
        )
        docsync.sync(self.root)
        text = self.output.read_text(encoding="utf-8")
        for expected in (
            "public(a, /, b=..., *items, required, optional=..., **kwargs)",
            "async fetch()", "Public.__init__(self, key=...)",
            "Public.method(self)", "Not Found", "&lt;script&gt;",
        ):
            self.assertIn(expected, text)
        for excluded in ("never-publish", "_private", "_hidden", "<script>"):
            self.assertNotIn(excluded, text)

    def test_keyword_only_separator(self) -> None:
        tree = docsync.ast.parse("def f(*, required, optional=None): pass")
        self.assertEqual(docsync.signature(tree.body[0]), "f(*, required, optional=...)")

    def test_idempotent_sync_preserves_mtime_and_handwritten_docs(self) -> None:
        (self.root / "docs").mkdir()
        manual = self.root / "docs" / "notes.md"
        manual.write_text("Human-owned\n", encoding="utf-8")
        self.assertTrue(docsync.sync(self.root))
        timestamp = self.output.stat().st_mtime_ns
        self.assertFalse(docsync.sync(self.root))
        self.assertEqual(self.output.stat().st_mtime_ns, timestamp)
        self.assertEqual(manual.read_text(encoding="utf-8"), "Human-owned\n")
        self.assertTrue(docsync.check(self.root))

    def test_source_is_never_executed(self) -> None:
        self.source.write_text('raise RuntimeError("must not execute")\ndef public(): pass\n', encoding="utf-8")
        self.assertTrue(docsync.sync(self.root))

    def test_nested_add_rename_delete_and_comment_change(self) -> None:
        docsync.sync(self.root)
        original = self.output.read_bytes()
        folder = self.root / "src" / "nested"
        folder.mkdir()
        extra = folder / "a b.py"
        extra.write_text("def added(): pass\n", encoding="utf-8")
        self.assertTrue(docsync.sync(self.root))
        self.assertIn("../src/nested/a%20b.py", self.output.read_text(encoding="utf-8"))
        renamed = extra.rename(folder / "renamed.py")
        docsync.sync(self.root)
        self.assertNotIn("a b.py", self.output.read_text(encoding="utf-8"))
        renamed.unlink()
        docsync.sync(self.root)
        self.assertEqual(self.output.read_bytes(), original)
        self.source.write_bytes(self.source.read_bytes() + b"# comment only\n")
        self.assertFalse(docsync.check(self.root))
        docsync.sync(self.root)
        self.assertNotEqual(self.output.read_bytes(), original)

    def test_render_is_sorted(self) -> None:
        files = {"src/z.py": b"pass", "src/a.py": b"pass"}
        self.assertEqual(docsync.render(files), docsync.render(dict(reversed(list(files.items())))))
        self.assertLess(docsync.render(files).index("src/a.py"), docsync.render(files).index("src/z.py"))

    def test_missing_source(self) -> None:
        self.source.unlink()
        (self.root / "src").rmdir()
        with self.assertRaisesRegex(docsync.SyncError, "existing"):
            docsync.sync(self.root)
        self.assertFalse((self.root / ".docsync.lock").exists())

    def test_empty_source_preserves_output(self) -> None:
        docsync.sync(self.root)
        original = self.output.read_bytes()
        self.source.unlink()
        with self.assertRaisesRegex(docsync.SyncError, "Not Found"):
            docsync.sync(self.root)
        self.assertEqual(self.output.read_bytes(), original)

    def test_invalid_source_preserves_output_and_cleans_lock(self) -> None:
        docsync.sync(self.root)
        original = self.output.read_bytes()
        for bad in (b"def broken(", b"\xff", b"x = '\x00'"):
            with self.subTest(source=bad):
                self.source.write_bytes(bad)
                with self.assertRaises(docsync.SyncError):
                    docsync.sync(self.root)
                self.assertEqual(self.output.read_bytes(), original)
                self.assertFalse((self.root / ".docsync.lock").exists())

    def test_declared_encoding_is_supported(self) -> None:
        self.source.write_bytes(b'# coding: latin-1\n"""caf\xe9"""\n')
        docsync.sync(self.root)
        self.assertIn("caf\u00e9", self.output.read_text(encoding="utf-8"))

    def test_unowned_output_is_never_overwritten(self) -> None:
        self.output.parent.mkdir()
        self.output.write_text("Handwritten reference\n", encoding="utf-8")
        for operation in (docsync.sync, docsync.check):
            with self.assertRaisesRegex(docsync.SyncError, "unowned"):
                operation(self.root)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "Handwritten reference\n")

    def test_missing_and_tampered_generated_output_are_drift(self) -> None:
        self.assertFalse(docsync.check(self.root))
        docsync.sync(self.root)
        self.output.write_bytes(self.output.read_bytes() + b"tampered")
        self.assertFalse(docsync.check(self.root))
        self.assertTrue(docsync.sync(self.root))

    def test_lock_conflict(self) -> None:
        lock = self.root / ".docsync.lock"
        lock.write_text("123", encoding="ascii")
        with self.assertRaisesRegex(docsync.SyncError, "lock exists"):
            docsync.sync(self.root)
        self.assertEqual(lock.read_text(encoding="ascii"), "123")

    def test_replace_failure_preserves_output_and_cleans_up(self) -> None:
        docsync.sync(self.root)
        original = self.output.read_bytes()
        self.source.write_bytes(self.source.read_bytes() + b"# changed\n")
        with patch.object(docsync.os, "replace", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                docsync.sync(self.root)
        self.assertEqual(self.output.read_bytes(), original)
        self.assertFalse((self.root / ".docsync.lock").exists())
        self.assertEqual(list(self.output.parent.glob(".api-*.tmp")), [])

    def test_source_change_during_render_is_rejected(self) -> None:
        files = docsync.snapshot(self.root)
        with patch.object(docsync, "snapshot", side_effect=[files, {"src/new.py": b"pass"}]):
            with self.assertRaisesRegex(docsync.SyncError, "changed during"):
                docsync.sync(self.root)
        self.assertFalse(self.output.exists())

    def test_directory_scan_errors_are_not_ignored(self) -> None:
        def failed_walk(source, **kwargs):
            kwargs["onerror"](PermissionError("denied"))
        with patch.object(docsync.os, "walk", side_effect=failed_walk):
            with self.assertRaises(PermissionError):
                docsync.sync(self.root)

    def test_output_directory_is_rejected(self) -> None:
        self.output.mkdir(parents=True)
        with self.assertRaisesRegex(docsync.SyncError, "regular"):
            docsync.sync(self.root)

    def test_symlink_source_and_output_guards(self) -> None:
        original = Path.is_symlink
        for unsafe in (self.root / "src", self.source, self.root / "docs", self.output):
            with self.subTest(path=unsafe):
                with patch.object(Path, "is_symlink", lambda path: path == unsafe or original(path)):
                    with self.assertRaises(docsync.SyncError):
                        docsync.sync(self.root)

    def test_real_symlink_is_rejected_when_supported(self) -> None:
        link = self.root / "src" / "linked.py"
        try:
            link.symlink_to(self.source)
        except OSError as error:
            self.skipTest(f"OS symlink creation unavailable: {error}")
        with self.assertRaisesRegex(docsync.SyncError, "Symlink"):
            docsync.sync(self.root)

    def test_cli_exit_codes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(docsync.main(["check", "--root", str(self.root)]), 1)
            self.assertEqual(docsync.main(["sync", "--root", str(self.root)]), 0)
            self.assertEqual(docsync.main(["check", "--root", str(self.root)]), 0)
            self.source.write_text("def invalid(", encoding="utf-8")
            self.assertEqual(docsync.main(["sync", "--root", str(self.root)]), 2)

    def test_cli_subprocess_from_another_working_directory(self) -> None:
        result = subprocess.run(
            [sys.executable, str(Path(docsync.__file__)), "sync", "--root", str(self.root)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(docsync.check(self.root))

    def test_invalid_watch_intervals(self) -> None:
        for interval in (0, -1, float("inf"), float("nan")):
            with self.subTest(interval=interval):
                with self.assertRaisesRegex(docsync.SyncError, "finite"):
                    docsync.watch(self.root, interval)

    def test_live_watcher_updates_and_recovers_within_deadline(self) -> None:
        stop = threading.Event()
        messages: list[str] = []
        worker = threading.Thread(
            target=docsync.watch, args=(self.root, 0.02, stop, messages.append),
        )
        worker.start()

        def wait_for(condition) -> None:
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                if condition():
                    return
                time.sleep(0.01)
            self.fail(f"Watcher did not react within 3 seconds: {messages}")

        try:
            wait_for(lambda: "Synchronized docs/api.md" in messages)
            original = self.output.read_bytes()
            self.source.write_text("def broken(", encoding="utf-8")
            wait_for(lambda: any("ERROR:" in message for message in messages))
            self.assertEqual(self.output.read_bytes(), original)
            self.source.write_text('def repaired():\n    """Recovered API."""\n', encoding="utf-8")
            wait_for(lambda: any("Recovered:" in message for message in messages))
            self.assertIn("repaired()", self.output.read_text(encoding="utf-8"))
            self.assertTrue(docsync.check(self.root))
        finally:
            stop.set()
            worker.join(timeout=3)
        self.assertFalse(worker.is_alive())
