#!/usr/bin/env python3
"""Verify every source-component lock against explicit local checkouts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r'^version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"\s*$', re.MULTILINE)


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _git(root: Path, revision: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", revision],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _metadata(root: Path) -> tuple[str, str]:
    path = root / "pyproject.toml"
    content = path.read_bytes()
    match = VERSION.search(content.decode("utf-8"))
    if match is None:
        raise ValueError(f"{path}: project version was not found")
    return match.group(1), hashlib.sha256(content).hexdigest()


def verify_components(
    project_root: Path,
    checkouts: dict[str, Path],
) -> list[str]:
    lock = _load(project_root / "runtime" / "compatibility-lock.json")
    errors: list[str] = []
    for component_id, checkout in checkouts.items():
        expected = lock["components"][component_id]
        try:
            commit = _git(checkout, "HEAD")
            tree = _git(checkout, "HEAD^{tree}")
            version, metadata_hash = _metadata(checkout)
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            errors.append(f"{component_id}: cannot inspect checkout: {exc}")
            continue
        for field, actual in {
            "commit": commit,
            "tree": tree,
            "version": version,
            "metadata_sha256": metadata_hash,
        }.items():
            if actual != expected[field]:
                errors.append(
                    f"{component_id}: {field} is {actual}, lock requires {expected[field]}"
                )
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(
            "usage: verify_component_locks.py /path/to/ComfyUI-Cauce "
            "/path/to/ComfyUI-Runtime-Control /path/to/ComfyUI-Workspace-Control "
            "/path/to/ComfyUI-Repository-Control",
            file=sys.stderr,
        )
        return 2
    checkouts = {
        "cauce": Path(argv[1]).resolve(),
        "runtime_control": Path(argv[2]).resolve(),
        "workspace_control": Path(argv[3]).resolve(),
        "repository_control": Path(argv[4]).resolve(),
    }
    errors = verify_components(ROOT, checkouts)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("verified: component commit, tree, version, and metadata hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
