"""Frontend documentation ownership, drift, watcher and staged-index regressions."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import copilot_hook
import docsync
import git_gate
import ui_docs


class FrontendSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "src"
        self.source.mkdir()
        (self.source / "backend.py").write_text('"""Backend."""\ndef public(): pass\n', encoding="utf-8")
        self.assets = self.source / "static"
        self.assets.mkdir()
        self.page = self.assets / "index.html"
        self.page.write_text(
            '<title>Dashboard</title><meta name="description" content="Track expenses">'
            '<h1>Overview</h1><section data-component="Editor" data-doc="Add expenses">'
            '<form id="expense-form"><input id="amount" value="never-publish"></form></section>'
            '<script src="app.js"></script><link href="styles.css" rel="stylesheet">',
            encoding="utf-8",
        )
        self.css = self.assets / "styles.css"
        self.css.write_text('.card { color: red; } @media (max-width: 700px) { .card { color: blue; } }', encoding="utf-8")
        self.js = self.assets / "app.js"
        self.js.write_text('/** @ui Save an expense. */\nasync function save() {}\nconst refresh = () => {};\n', encoding="utf-8")
        self.api = self.root / "docs" / "api.md"
        self.ui = self.root / "docs" / "ui.md"

    def test_inventory_and_independent_fingerprints_noop_and_escaping(self) -> None:
        self.assertTrue(docsync.sync(self.root))
        text = self.ui.read_text(encoding="utf-8")
        for expected in ("Dashboard", "Track expenses", "Overview", "Editor", "Add expenses",
                         "input #amount", ".card", "@media", "save", "refresh", "Save an expense."):
            self.assertIn(expected, text)
        self.assertNotIn("never-publish", text)
        api, ui = self.api.read_bytes(), self.ui.read_bytes()
        timestamps = (self.api.stat().st_mtime_ns, self.ui.stat().st_mtime_ns)
        self.assertFalse(docsync.sync(self.root))
        self.assertEqual(timestamps, (self.api.stat().st_mtime_ns, self.ui.stat().st_mtime_ns))
        self.css.write_text(self.css.read_text(encoding="utf-8") + "\n/* changed */", encoding="utf-8")
        self.assertFalse(docsync.check(self.root))
        docsync.sync(self.root)
        self.assertEqual(self.api.read_bytes(), api)
        self.assertNotEqual(self.ui.read_bytes(), ui)
        ui = self.ui.read_bytes()
        (self.source / "backend.py").write_text('"""Changed backend."""\n', encoding="utf-8")
        docsync.sync(self.root)
        self.assertEqual(self.ui.read_bytes(), ui)
        self.assertNotEqual(self.api.read_bytes(), api)
        escaped = ui_docs.render_ui({"src/page.html": b'<title>&lt;script&gt;</title><div data-component="&lt;x&gt;" data-doc="&lt;img&gt;"></div>'})
        self.assertIn("&lt;script&gt;", escaped)
        self.assertNotIn("<script>", escaped)

    def test_add_modify_rename_remove_all_source_types(self) -> None:
        docsync.sync(self.root)
        for extension, content in (
            ("html", '<title>Added</title><div data-component="Added component" data-doc="New function"></div>'),
            ("css", ".added-component { color: green; }"),
            ("js", "/** @ui Added behavior. */ function addedFunction() {}"),
        ):
            extra = self.assets / f"extra.{extension}"
            extra.write_text(content, encoding="utf-8")
            self.assertFalse(docsync.check(self.root))
            docsync.sync(self.root)
            self.assertIn(f"extra.{extension}", self.ui.read_text(encoding="utf-8"))
            extra.write_text(content + "\n", encoding="utf-8")
            self.assertTrue(docsync.sync(self.root))
            renamed = extra.rename(self.assets / f"renamed.{extension}")
            docsync.sync(self.root)
            text = self.ui.read_text(encoding="utf-8")
            self.assertNotIn(f"extra.{extension}", text)
            self.assertIn(f"renamed.{extension}", text)
            renamed.unlink()
            self.assertTrue(docsync.sync(self.root))
            self.assertNotIn(f"renamed.{extension}", self.ui.read_text(encoding="utf-8"))
        for asset in (self.page, self.css, self.js):
            asset.unlink()
        self.assertTrue(docsync.sync(self.root))
        self.assertIn("Not Found", self.ui.read_text(encoding="utf-8"))
        self.assertNotIn("Editor", self.ui.read_text(encoding="utf-8"))
        self.assertTrue(docsync.check(self.root))

    def test_unowned_ui_and_invalid_encoding_preserve_both_good_outputs(self) -> None:
        docsync.sync(self.root)
        api, ui = self.api.read_bytes(), self.ui.read_bytes()
        for asset in (self.page, self.css, self.js):
            original = asset.read_bytes()
            asset.write_bytes(b"\xff")
            with self.assertRaisesRegex(docsync.SyncError, "frontend"):
                docsync.sync(self.root)
            self.assertEqual((self.api.read_bytes(), self.ui.read_bytes()), (api, ui))
            asset.write_bytes(original)
        self.ui.write_text("Handwritten UI guide", encoding="utf-8")
        for operation in (docsync.sync, docsync.check):
            with self.assertRaisesRegex(docsync.SyncError, "unowned docs/ui.md"):
                operation(self.root)
        self.assertEqual(self.ui.read_text(encoding="utf-8"), "Handwritten UI guide")
        self.assertFalse((self.root / ".docsync.lock").exists())

    def test_ui_drift_and_symlink_outputs_or_assets_are_rejected(self) -> None:
        docsync.sync(self.root)
        self.ui.write_bytes(self.ui.read_bytes() + b"tampered")
        self.assertFalse(docsync.check(self.root))
        self.assertTrue(docsync.sync(self.root))
        original = Path.is_symlink
        for target in (self.page, self.css, self.js, self.ui):
            with patch.object(Path, "is_symlink", lambda path: path == target or original(path)):
                with self.assertRaises(docsync.SyncError):
                    docsync.sync(self.root)

    def test_invalid_backend_preserves_ui_and_api(self) -> None:
        docsync.sync(self.root)
        original = self.api.read_bytes(), self.ui.read_bytes()
        self.css.write_text(".new {}", encoding="utf-8")
        (self.source / "backend.py").write_text("def broken(", encoding="utf-8")
        with self.assertRaises(docsync.SyncError):
            docsync.sync(self.root)
        self.assertEqual(original, (self.api.read_bytes(), self.ui.read_bytes()))

    def test_js_declarations_not_string_contents_and_deterministic_order(self) -> None:
        files = {
            "src/z.js": b'const text = "function fake() {}"; // function commented() {}\nfunction real() {}\nclass Panel {}\n',
            "src/a.html": b"<title>Page</title>",
        }
        rendered = ui_docs.render_ui(files)
        self.assertEqual(rendered, ui_docs.render_ui(dict(reversed(list(files.items())))))
        self.assertIn("<code>real</code>", rendered)
        self.assertIn("<code>Panel</code>", rendered)
        self.assertNotIn("<code>fake</code>", rendered)
        self.assertNotIn("<code>commented</code>", rendered)
        self.assertIn("Not Found", rendered)

    def test_hook_synchronizes_frontend_and_preserves_api(self) -> None:
        import contextlib
        import io
        docsync.sync(self.root)
        original = self.api.read_bytes()
        self.js.write_text("/** @ui New behavior. */ function newAction() {}", encoding="utf-8")
        with patch.object(docsync, "DEFAULT_ROOT", self.root), patch.object(sys, "stdin", io.StringIO('{"tool_name":"edit"}')):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(copilot_hook.main(["post"]), 0)
        self.assertEqual(json.loads(output.getvalue())["systemMessage"], "Documentation synchronized")
        self.assertIn("newAction", self.ui.read_text(encoding="utf-8"))
        self.assertEqual(self.api.read_bytes(), original)

    def test_live_watcher_detects_each_frontend_type_within_deadline(self) -> None:
        stop = threading.Event()
        messages: list[str] = []
        worker = threading.Thread(target=docsync.watch, args=(self.root, 0.02, stop, messages.append))
        worker.start()

        def wait_for(predicate) -> None:
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                if predicate():
                    return
                time.sleep(0.01)
            self.fail(f"Watcher deadline exceeded: {messages}")

        try:
            wait_for(lambda: any(message.startswith("Synchronized documentation") for message in messages))
            for asset in (self.page, self.css, self.js):
                original = self.ui.read_bytes()
                before = messages.count("Synchronized documentation: docs/api.md and docs/ui.md")
                asset.write_bytes(asset.read_bytes() + b"\n")
                wait_for(lambda: messages.count("Synchronized documentation: docs/api.md and docs/ui.md") > before)
                self.assertNotEqual(self.ui.read_bytes(), original)
        finally:
            stop.set()
            worker.join(timeout=3)
        self.assertFalse(worker.is_alive())

    @unittest.skipUnless(shutil.which("git"), "Git executable unavailable")
    def test_staged_frontend_and_ui_must_match_independently_of_worktree(self) -> None:
        git_gate.git(self.root, "init")
        git_gate.git(self.root, "config", "core.autocrlf", "false")
        docsync.sync(self.root)
        git_gate.git(self.root, "add", ".")
        self.assertTrue(git_gate.check_index(self.root))
        for asset in (self.page, self.css, self.js):
            asset.write_bytes(asset.read_bytes() + b"\n")
            git_gate.git(self.root, "add", str(asset))
            docsync.sync(self.root)
            self.assertFalse(git_gate.check_index(self.root))
            git_gate.git(self.root, "add", "docs/ui.md")
            self.assertTrue(git_gate.check_index(self.root))
        self.js.unlink()
        git_gate.git(self.root, "add", str(self.js))
        self.assertFalse(git_gate.check_index(self.root))
        docsync.sync(self.root)
        git_gate.git(self.root, "add", "docs/ui.md")
        self.assertTrue(git_gate.check_index(self.root))


if __name__ == "__main__":
    unittest.main()
