#!/usr/bin/env python3
"""Derive all project-side CAUCE locks from one committed contract bundle."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r'^version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"\s*$', re.MULTILINE)


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _content_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def inspect_cauce(cauce_root: Path) -> dict[str, Any]:
    """Read only content committed at CAUCE HEAD; ignore mutable worktree data."""

    cauce_root = cauce_root.resolve()
    commit = _git(cauce_root, "rev-parse", "HEAD")
    tree = _git(cauce_root, "rev-parse", "HEAD^{tree}")
    bundle = json.loads(
        _git(cauce_root, "show", "HEAD:operations/contract-bundle.json")
    )
    if bundle.get("schema") != "cauce.contract-bundle/1":
        raise ValueError("CAUCE HEAD does not contain a supported contract bundle")
    unhashed = {key: value for key, value in bundle.items() if key != "bundle_hash"}
    if bundle.get("bundle_hash") != _content_hash(unhashed):
        raise ValueError("CAUCE contract bundle hash does not match its contents")
    metadata = _git(cauce_root, "show", "HEAD:pyproject.toml") + "\n"
    match = VERSION.search(metadata)
    if match is None or match.group(1) != bundle.get("package_version"):
        raise ValueError("CAUCE package metadata and contract bundle versions differ")
    return {
        "root": cauce_root,
        "commit": commit,
        "tree": tree,
        "captured_at": _git(cauce_root, "show", "-s", "--format=%cI", "HEAD"),
        "version": match.group(1),
        "metadata_sha256": hashlib.sha256(metadata.encode("utf-8")).hexdigest(),
        "bundle": bundle,
    }


def compile_project_updates(
    project_root: Path, cauce: dict[str, Any]
) -> dict[Path, Any]:
    """Return every exact project artifact derived from the CAUCE source lock."""

    project_root = project_root.resolve()
    bundle = cauce["bundle"]
    repository = _load(project_root / "operations.lock.json")["source"]["repository"]
    source = {
        "repository": repository,
        "commit": cauce["commit"],
    }
    operations = {
        "schema": "inside-valdivia.cauce-operation-lock/1",
        "source": {
            **source,
            "catalog_hash": bundle["operations"]["catalog_hash"],
        },
        "operations": bundle["operations"]["current"],
    }
    history = {
        "schema": "inside-valdivia.cauce-operation-history-lock/1",
        "source": {
            **source,
            "catalog_hash": bundle["operations"]["history_catalog_hash"],
        },
        "contracts": bundle["operations"]["historical"],
    }
    archetypes = {
        "schema": "inside-valdivia.cauce-archetype-lock/1",
        "source": {
            **source,
            "catalog_hash": bundle["archetypes"]["catalog_hash"],
        },
        "archetypes": bundle["archetypes"]["entries"],
    }
    nodes = {
        "schema": "inside-valdivia.cauce-node-lock/1",
        "source": {
            **source,
            "bundle_hash": bundle["bundle_hash"],
        },
        "nodes": bundle["nodes"],
    }

    compatibility_path = project_root / "runtime" / "compatibility-lock.json"
    compatibility = copy.deepcopy(_load(compatibility_path))
    compatibility["captured_at"] = cauce["captured_at"]
    component = compatibility["components"]["cauce"]
    component.update(
        {
            "version": cauce["version"],
            "commit": cauce["commit"],
            "tree": cauce["tree"],
            "metadata_sha256": cauce["metadata_sha256"],
        }
    )

    live_gate_path = project_root / "materialization" / "live-gate.json"
    live_gate = copy.deepcopy(_load(live_gate_path))
    live_gate["source_locks"]["cauce_commit"] = cauce["commit"]

    updates: dict[Path, Any] = {
        project_root / "operations.lock.json": operations,
        project_root / "operations.history.lock.json": history,
        project_root / "archetypes.lock.json": archetypes,
        project_root / "cauce.nodes.lock.json": nodes,
        compatibility_path: compatibility,
        live_gate_path: live_gate,
    }
    for path in sorted((project_root / "rolling" / "plans").glob("*.json")):
        plan = copy.deepcopy(_load(path))
        plan["source_locks"]["cauce_commit"] = cauce["commit"]
        updates[path] = plan
    return updates


def _write_atomic(path: Path, value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(path)


def _is_dirty(project_root: Path, path: Path) -> bool:
    relative = path.relative_to(project_root)
    return bool(_git(project_root, "status", "--porcelain", "--", str(relative)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cauce_checkout", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        cauce = inspect_cauce(args.cauce_checkout)
        updates = compile_project_updates(ROOT, cauce)
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"cannot compile CAUCE locks: {exc}", file=sys.stderr)
        return 2

    stale: list[Path] = []
    for path, expected in updates.items():
        try:
            current = _load(path)
        except (OSError, json.JSONDecodeError):
            current = None
        if current != expected:
            stale.append(path)
    if args.check:
        if stale:
            for path in stale:
                print(
                    f"stale derived CAUCE artifact: {path.relative_to(ROOT)}",
                    file=sys.stderr,
                )
            return 1
        print(f"verified: {len(updates)} CAUCE-derived artifacts at {cauce['commit']}")
        return 0

    dirty = [path for path in stale if path.exists() and _is_dirty(ROOT, path)]
    if dirty:
        for path in dirty:
            print(
                f"refusing to overwrite dirty derived artifact: {path.relative_to(ROOT)}",
                file=sys.stderr,
            )
        return 2
    for path in stale:
        _write_atomic(path, updates[path])
    print(f"synchronized: {len(stale)} artifacts from CAUCE {cauce['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
