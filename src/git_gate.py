"""Reject staged source and generated-document drift without changing the Git index."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

import docsync


def git(root: Path, *arguments: str) -> bytes:
    """Run Git without a shell and report failures explicitly."""
    result = subprocess.run(
        ["git", "--no-pager", "-C", str(root), *arguments],
        capture_output=True, check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
        raise docsync.SyncError(detail or f"Git failed with exit {result.returncode}")
    return result.stdout


def check_index(root: Path) -> bool:
    """Validate staged blobs, including partially staged files, in isolation."""
    entries = git(root, "ls-files", "--stage", "-z", "--", "src", "docs/api.md", "docs/ui.md")
    with tempfile.TemporaryDirectory(prefix="docsync-index-") as directory:
        staged = Path(directory)
        for entry in entries.split(b"\0"):
            if not entry:
                continue
            metadata, raw_name = entry.split(b"\t", 1)
            mode, object_id, stage = metadata.decode("ascii").split()
            name = raw_name.decode("utf-8")
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise docsync.SyncError("Unsafe staged path")
            if stage != "0":
                raise docsync.SyncError("Resolve index conflicts before committing")
            if mode not in ("100644", "100755"):
                raise docsync.SyncError(f"Non-regular staged source/output: {name}")
            relevant = name in ("docs/api.md", "docs/ui.md") or (
                path.parts[0] == "src" and path.suffix in docsync.SOURCE_SUFFIXES
            )
            if not relevant:
                continue
            target = staged.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(root, "cat-file", "blob", object_id))
        return docsync.check(staged)


def main() -> int:
    """Check the index of the current workspace; never stage or rewrite files."""
    try:
        current = check_index(docsync.DEFAULT_ROOT)
        print("Staged documentation is current" if current else "Staged documentation drift: sync and stage matching files")
        return 0 if current else 1
    except (docsync.SyncError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
