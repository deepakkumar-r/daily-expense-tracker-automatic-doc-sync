"""Deterministic, local-only API documentation synchronization."""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import math
import os
from pathlib import Path
import sys
import tempfile
import threading
from typing import Callable
from urllib.parse import quote

from ui_docs import SUFFIXES, render_ui

MARKER = "<!-- docsync:generated:v1 -->\n"
SOURCE_SUFFIXES = (".py", *SUFFIXES)
DEFAULT_ROOT = Path(__file__).resolve().parent.parent


class SyncError(Exception):
    """Signal invalid source, unsafe output or a conflicting sync operation."""


def snapshot(root: Path, suffixes: tuple[str, ...] = (".py",)) -> dict[str, bytes]:
    """Read sorted requested source types without following symbolic links."""
    source = root / "src"
    if source.is_symlink() or not source.is_dir():
        raise SyncError("src must be an existing, non-symlink directory")
    files: dict[str, bytes] = {}

    def walk_error(error: OSError) -> None:
        raise error

    for directory, folders, names in os.walk(source, followlinks=False, onerror=walk_error):
        base = Path(directory)
        for name in folders + names:
            if (base / name).is_symlink():
                raise SyncError(f"Symlink is not allowed: {base / name}")
        folders[:] = sorted(name for name in folders if name != "__pycache__")
        for name in sorted(names):
            path = base / name
            if path.suffix not in suffixes:
                continue
            if not path.is_file():
                raise SyncError(f"Source is not a regular file: {path}")
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    if not any(name.endswith(".py") for name in files):
        raise SyncError("Not Found: no Python source files in src")
    return dict(sorted(files.items()))


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Describe parameter kinds without publishing default expressions."""
    args = node.args
    positional = args.posonlyargs + args.args
    first_default = len(positional) - len(args.defaults)
    parts: list[str] = []
    for index, arg in enumerate(positional):
        parts.append(arg.arg + ("=..." if index >= first_default else ""))
        if args.posonlyargs and index + 1 == len(args.posonlyargs):
            parts.append("/")
    if args.vararg:
        parts.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append("*")
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(arg.arg + ("=..." if default is not None else ""))
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    return prefix + node.name + "(" + ", ".join(parts) + ")"


def render(files: dict[str, bytes]) -> str:
    """Render escaped public declarations and a fingerprint of every source byte."""
    digest = hashlib.sha256()
    sections: list[str] = []

    def description(node: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        text = ast.get_docstring(node) or "Not Found"
        return "<pre>" + html.escape(text) + "</pre>\n"

    def declaration(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef, prefix: str = "") -> None:
        label = prefix + (node.name if isinstance(node, ast.ClassDef) else signature(node))
        sections.extend([f"### <code>{html.escape(label)}</code>\n", description(node)])
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not member.name.startswith("_") or member.name == "__init__":
                        declaration(member, node.name + ".")

    for name, content in sorted(files.items()):
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(len(content).to_bytes(8, "big") + content)
        try:
            tree = ast.parse(content, filename=name)
        except (SyntaxError, ValueError) as error:
            raise SyncError(f"Cannot parse {name}: {error}") from error
        sections.extend([
            f"## <code>{html.escape(name)}</code>\n",
            f"[Source](../{quote(name, safe='/')})\n",
            description(tree),
        ])
        count = 0
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    declaration(node)
                    count += 1
        if not count:
            sections.append("Public API: Not Found.\n")
    return (
        MARKER
        + "# Python API reference\n\n"
        + "Generated from source; do not edit manually. Defaults and annotations are omitted.\n\n"
        + f"Source fingerprint: `{digest.hexdigest()}`\n\n"
        + "\n".join(sections)
    )


def output_bytes(root: Path, name: str = "api.md") -> bytes | None:
    """Read only a regular generated file under a safe docs directory."""
    docs = root / "docs"
    if name not in ("api.md", "ui.md"):
        raise SyncError("Unsupported generated output")
    target = docs / name
    if docs.is_symlink() or (docs.exists() and not docs.is_dir()):
        raise SyncError("docs must be a non-symlink directory")
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise SyncError(f"docs/{name} must be a regular, non-symlink file")
    if not target.exists():
        return None
    content = target.read_bytes()
    if not content.startswith(MARKER.encode("utf-8")):
        raise SyncError(f"Refusing to overwrite unowned docs/{name}")
    return content


def documents(root: Path, files: dict[str, bytes]) -> dict[str, bytes]:
    """Render separate backend/frontend references before any output is replaced."""
    outputs = {"api.md": render({name: data for name, data in files.items() if name.endswith(".py")}).encode("utf-8")}
    frontend = {name: data for name, data in files.items() if name.endswith(SUFFIXES)}
    previous_ui = output_bytes(root, "ui.md")
    if frontend or previous_ui is not None:
        try:
            outputs["ui.md"] = render_ui(frontend).encode("utf-8")
        except (UnicodeError, ValueError) as error:
            raise SyncError(f"Cannot parse frontend source: {error}") from error
    return outputs


def check(root: Path) -> bool:
    """Return whether all generated documents exactly match their source types."""
    expected = documents(root, snapshot(root, SOURCE_SUFFIXES))
    actual = {name: output_bytes(root, name) for name in expected}
    return actual == expected


def sync(root: Path) -> bool:
    """Atomically synchronize owned output; return true only when bytes changed."""
    lock = root / ".docsync.lock"
    try:
        handle = lock.open("x", encoding="ascii")
    except FileExistsError as error:
        raise SyncError("Sync lock exists; check its PID before removing a stale lock") from error
    temporary: list[str] = []
    try:
        with handle:
            handle.write(str(os.getpid()))
        files = snapshot(root, SOURCE_SUFFIXES)
        expected = documents(root, files)
        actual = {name: output_bytes(root, name) for name in expected}
        changed = {name: content for name, content in expected.items() if actual[name] != content}
        if not changed:
            return False
        docs = root / "docs"
        docs.mkdir(exist_ok=True)
        if snapshot(root, SOURCE_SUFFIXES) != files:
            raise SyncError("Source changed during rendering; retry synchronization")
        replacements: list[tuple[str, str]] = []
        for name, content in changed.items():
            with tempfile.NamedTemporaryFile(dir=docs, prefix=f".{name[:-3]}-", suffix=".tmp", delete=False) as stream:
                temporary.append(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                replacements.append((stream.name, name))
        for source, name in replacements:
            os.replace(source, docs / name)
            temporary.remove(source)
        return True
    finally:
        try:
            for name in temporary:
                Path(name).unlink(missing_ok=True)
        finally:
            lock.unlink()


def watch(
    root: Path,
    interval: float = 1.0,
    stop: threading.Event | None = None,
    report: Callable[[str], None] = print,
) -> None:
    """Continuously synchronize, report failures and recover after valid edits."""
    if not math.isfinite(interval) or interval <= 0:
        raise SyncError("Watch interval must be finite and greater than zero")
    stopped = stop if stop is not None else threading.Event()
    last_error: str | None = None
    report("Watching src; press Ctrl+C to stop")
    while not stopped.is_set():
        try:
            if sync(root):
                report("Synchronized documentation: docs/api.md and docs/ui.md"
                       if (root / "docs" / "ui.md").exists() else "Synchronized docs/api.md")
            if last_error is not None:
                report("Recovered: source and output are valid")
            last_error = None
        except (SyncError, OSError) as error:
            message = f"ERROR: {error}"
            if message != last_error:
                report(message)
            last_error = message
        stopped.wait(interval)


def main(argv: list[str] | None = None) -> int:
    """Run sync, check or watch with explicit 0/1/2 exit semantics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "check", "watch"))
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "check":
            current = check(root)
            print("Documentation is current" if current else "Documentation drift: run sync and stage generated docs")
            return 0 if current else 1
        if args.command == "watch":
            watch(root, args.interval, report=lambda message: print(
                message, file=sys.stderr if message.startswith("ERROR:") else sys.stdout, flush=True
            ))
        else:
            print("Synchronized generated documentation" if sync(root) else "Documentation unchanged")
        return 0
    except KeyboardInterrupt:
        print("Watcher stopped")
        return 0
    except (SyncError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
