#!/usr/bin/env python3
"""Verify operations.lock.json against an explicit local CAUCE checkout."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
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
    bundle = load_json(cauce_root / "operations" / "contract-bundle.json")
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
        errors.append(
            f"CAUCE checkout is {actual_commit}, lock requires {expected_commit}"
        )
    if bundle.get("schema") != "cauce.contract-bundle/1":
        return errors + ["CAUCE contract bundle schema is unsupported"]
    unhashed = {key: value for key, value in bundle.items() if key != "bundle_hash"}
    if bundle.get("bundle_hash") != content_hash(unhashed):
        errors.append("CAUCE contract bundle hash does not match its contents")
    expected_source = {
        "repository": "https://github.com/hypereikon-lab/ComfyUI-Cauce",
        "commit": actual_commit,
        "catalog_hash": bundle["operations"]["catalog_hash"],
    }
    if lock.get("source") != expected_source:
        errors.append("CAUCE operation source lock differs from the contract bundle")
    if lock.get("operations") != bundle["operations"]["current"]:
        errors.append("locked operations differ from the CAUCE contract bundle")

    history_lock = load_json(project_root / "operations.history.lock.json")
    expected_history_source = {
        "repository": "https://github.com/hypereikon-lab/ComfyUI-Cauce",
        "commit": actual_commit,
        "catalog_hash": bundle["operations"]["history_catalog_hash"],
    }
    if history_lock.get("source") != expected_history_source:
        errors.append("CAUCE history source lock differs from the contract bundle")
    if history_lock.get("contracts") != bundle["operations"]["historical"]:
        errors.append(
            "historical operation tuples differ from the CAUCE contract bundle"
        )

    node_lock = load_json(project_root / "cauce.nodes.lock.json")
    if node_lock.get("source") != {
        "repository": "https://github.com/hypereikon-lab/ComfyUI-Cauce",
        "commit": actual_commit,
        "bundle_hash": bundle["bundle_hash"],
    }:
        errors.append("CAUCE node source lock differs from the contract bundle")
    if node_lock.get("nodes") != bundle["nodes"]:
        errors.append("locked CAUCE nodes differ from the contract bundle")

    topology_keys = {entry["key"] for entry in bundle["topologies"]["entries"]}

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
    unplanned_topologies = sorted(topology_keys - planned_keys)
    if unplanned_topologies:
        errors.append(
            "CAUCE topology dossiers lack materialization plans: "
            + ", ".join(unplanned_topologies)
        )

    archetype_lock = load_json(project_root / "archetypes.lock.json")
    if archetype_lock.get("source", {}).get("commit") != actual_commit:
        errors.append("CAUCE archetype lock requires a different source commit")
    if (
        archetype_lock.get("source", {}).get("catalog_hash")
        != bundle["archetypes"]["catalog_hash"]
    ):
        errors.append("CAUCE archetype catalog hash does not match lock")
    if archetype_lock.get("archetypes") != bundle["archetypes"]["entries"]:
        errors.append("locked graph archetypes differ from the CAUCE contract bundle")
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
        "verified: CAUCE bundle, current/historical operations, node registry, "
        "graph archetypes, and complete topology-plan coverage"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
