#!/usr/bin/env python3
"""Verify operations.lock.json against an explicit local CAUCE checkout."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def content_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_lock(project_root: Path, cauce_root: Path) -> list[str]:
    errors: list[str] = []
    lock = load_json(project_root / "operations.lock.json")
    catalog = load_json(cauce_root / "operations" / "catalog.json")
    expected_commit = lock["source"]["commit"]
    try:
        actual_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cauce_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"cannot resolve CAUCE commit: {exc}"]
    if actual_commit != expected_commit:
        errors.append(f"CAUCE checkout is {actual_commit}, lock requires {expected_commit}")
    actual_catalog_hash = content_hash(catalog)
    if actual_catalog_hash != lock["source"]["catalog_hash"]:
        errors.append("CAUCE catalog hash does not match lock")

    locked = {entry["id"]: entry for entry in lock["operations"]}
    catalog_entries = {entry["id"]: entry for entry in catalog["operations"]}
    if set(locked) != set(catalog_entries):
        errors.append("locked operation ids differ from CAUCE catalog")
    for operation_id in sorted(set(locked) & set(catalog_entries)):
        entry = catalog_entries[operation_id]
        relative = PurePosixPath(entry["spec"])
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"unsafe CAUCE spec path for {operation_id}")
            continue
        spec = load_json(cauce_root / "operations" / Path(*relative.parts))
        if entry["version"] != locked[operation_id]["version"]:
            errors.append(f"version mismatch for {operation_id}")
        if content_hash(spec) != locked[operation_id]["contract_hash"]:
            errors.append(f"contract hash mismatch for {operation_id}")

    topology_catalog = load_json(cauce_root / "operations" / "topologies" / "catalog.json")
    if topology_catalog.get("schema") != "cauce.operation-topology-catalog/2":
        errors.append("CAUCE topology catalog is not variant-addressable schema 2")
        topology_keys: set[str] = set()
    else:
        topology_keys = {
            f"{entry.get('operation')}@{entry.get('variant')}"
            for entry in topology_catalog.get("topologies", [])
            if isinstance(entry, dict)
        }
        if len(topology_keys) != len(topology_catalog.get("topologies", [])):
            errors.append("CAUCE topology catalog contains duplicate or malformed variants")

    materialization = load_json(project_root / "materialization" / "catalog.json")
    planned_keys = {
        entry.get("topology_key")
        for entry in materialization.get("plans", [])
        if isinstance(entry, dict)
    }
    missing_topologies = sorted(planned_keys - topology_keys)
    if missing_topologies:
        errors.append(
            "materialization plans lack CAUCE topology dossiers: "
            + ", ".join(missing_topologies)
        )
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_cauce_lock.py /path/to/ComfyUI-Cauce", file=sys.stderr)
        return 2
    errors = verify_lock(PROJECT_ROOT, Path(argv[1]).resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        "verified: CAUCE source commit, catalog hash, operation hashes, "
        "and planned topology variants"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
