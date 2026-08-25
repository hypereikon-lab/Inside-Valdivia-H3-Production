#!/usr/bin/env python3
"""Validate project operation invocations without third-party packages."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
EVIDENCE = {
    "planned",
    "schema-validated",
    "executes",
    "visually-accepted",
    "rejected",
    "blocked",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_h3_frame_count(value: Any) -> bool:
    return isinstance(value, int) and value >= 5 and (value - 5) % 17 == 0


def validate_operation_lock(value: Any, path: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.cauce-operation-lock/1":
        return [f"{path}: invalid operation lock"], {}
    source = value.get("source")
    if not isinstance(source, dict):
        errors.append(f"{path}: source must be an object")
    else:
        if not isinstance(source.get("repository"), str) or not source["repository"]:
            errors.append(f"{path}: source repository is required")
        if not isinstance(source.get("commit"), str) or not GIT_SHA.fullmatch(source["commit"]):
            errors.append(f"{path}: source commit must be a full Git SHA")
        if not isinstance(source.get("catalog_hash"), str) or not SHA256.fullmatch(
            source["catalog_hash"]
        ):
            errors.append(f"{path}: catalog_hash must be lowercase SHA-256")
    entries = value.get("operations")
    if not isinstance(entries, list) or not entries:
        return errors + [f"{path}: operations must be a non-empty list"], {}
    registry: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not {"id", "version", "contract_hash"} <= set(entry):
            errors.append(f"{path}: malformed operation entry {entry!r}")
            continue
        operation_id = entry.get("id")
        if not isinstance(operation_id, str) or not OPERATION_ID.fullmatch(operation_id):
            errors.append(f"{path}: invalid operation id {operation_id!r}")
            continue
        if operation_id in registry:
            errors.append(f"{path}: duplicate operation id {operation_id!r}")
        if not isinstance(entry.get("version"), int) or entry["version"] < 1:
            errors.append(f"{path}: operation {operation_id!r} needs a positive version")
        if not isinstance(entry.get("contract_hash"), str) or not SHA256.fullmatch(
            entry["contract_hash"]
        ):
            errors.append(f"{path}: operation {operation_id!r} needs a contract hash")
        registry[operation_id] = entry
    if list(registry) != sorted(registry):
        errors.append(f"{path}: operation entries must be sorted by id")
    return errors, registry


def _validate_operation_reference(
    value: dict[str, Any],
    path: Path,
    registry: dict[str, dict[str, Any]],
    *,
    require_hash: bool,
) -> list[str]:
    errors: list[str] = []
    operation_id = value.get("operation")
    locked = registry.get(operation_id)
    if locked is None:
        return [f"{path}: unknown operation {operation_id!r}"]
    if value.get("operation_version") != locked["version"]:
        errors.append(f"{path}: operation version does not match lock")
    if require_hash and value.get("operation_contract_hash") != locked["contract_hash"]:
        errors.append(f"{path}: operation contract hash does not match lock")
    return errors


def validate_invocation(
    value: Any, path: Path, registry: dict[str, dict[str, Any]]
) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path}: invocation must be an object"]
    errors: list[str] = []
    if value.get("schema") != "inside-valdivia.operation-invocation/1":
        errors.append(f"{path}: invalid invocation schema")
    errors.extend(_validate_operation_reference(value, path, registry, require_hash=True))
    if value.get("status") not in EVIDENCE | {"materialized", "queued"}:
        errors.append(f"{path}: invalid invocation status")
    if not isinstance(value.get("inputs"), dict) or not isinstance(value.get("parameters"), dict):
        errors.append(f"{path}: inputs and parameters must be objects")
    return errors


def validate_segment(value: Any, path: Path, invocation_ids: set[str]) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path}: segment must be an object"]
    errors: list[str] = []
    if value.get("schema") != "inside-valdivia.production-segment/2":
        errors.append(f"{path}: invalid segment schema")
    if value.get("frame_rate") != 24:
        errors.append(f"{path}: production segments must use 24 fps")
    frame_range = value.get("frame_range")
    if (
        not isinstance(frame_range, list)
        or len(frame_range) != 2
        or not all(isinstance(item, int) for item in frame_range)
        or frame_range[0] < 0
        or frame_range[1] <= frame_range[0]
    ):
        errors.append(f"{path}: frame_range must be a non-empty half-open integer range")
    sources = value.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{path}: sources must be a non-empty list")
    else:
        for source in sources:
            if not isinstance(source, dict) or not {"invocation", "output"} <= set(source):
                errors.append(f"{path}: malformed segment source {source!r}")
                continue
            if source["invocation"] not in invocation_ids:
                errors.append(f"{path}: unknown invocation {source['invocation']!r}")
            accepted = source.get("accepted_range")
            if accepted is not None and (
                not isinstance(accepted, list)
                or len(accepted) != 2
                or not all(isinstance(item, int) for item in accepted)
                or accepted[0] < 0
                or accepted[1] <= accepted[0]
            ):
                errors.append(f"{path}: accepted_range must be a non-empty half-open range")
    if value.get("status") not in {"planned", "assembled", "visually-accepted", "rejected", "blocked"}:
        errors.append(f"{path}: invalid segment status")
    return errors


def validate_experiment_catalog(
    value: Any, path: Path, registry: dict[str, dict[str, Any]]
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.h3-experiment-catalog/1":
        return [f"{path}: invalid experiment catalog"]
    errors: list[str] = []
    ids: set[str] = set()
    for experiment in value.get("experiments", []):
        if not isinstance(experiment, dict):
            errors.append(f"{path}: experiment must be an object")
            continue
        required = {
            "id",
            "operations",
            "question",
            "fixed",
            "variable",
            "measure",
            "status",
        }
        if not required <= set(experiment):
            errors.append(f"{path}: malformed experiment {experiment.get('id')!r}")
            continue
        if experiment["id"] in ids:
            errors.append(f"{path}: duplicate experiment id {experiment['id']!r}")
        ids.add(experiment["id"])
        operations = experiment.get("operations")
        if not isinstance(operations, list) or not operations:
            errors.append(f"{path}: experiment {experiment['id']!r} needs operations")
        else:
            for operation in operations:
                if not isinstance(operation, dict):
                    errors.append(f"{path}: malformed experiment operation {operation!r}")
                    continue
                normalized = {
                    "operation": operation.get("id"),
                    "operation_version": operation.get("version"),
                }
                errors.extend(
                    _validate_operation_reference(normalized, path, registry, require_hash=False)
                )
        if experiment["status"] not in EVIDENCE:
            errors.append(f"{path}: invalid experiment status {experiment['status']!r}")
        if not isinstance(experiment["variable"], dict) or len(experiment["variable"]) != 1:
            errors.append(f"{path}: experiment {experiment['id']!r} must change one variable")
        if not isinstance(experiment["measure"], list) or not experiment["measure"]:
            errors.append(f"{path}: experiment {experiment['id']!r} needs a measure")
    return errors


def validate_materialization_plan(
    value: Any, path: Path, registry: dict[str, dict[str, Any]]
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.materialization-plan/1":
        return [f"{path}: invalid materialization plan"]
    errors = _validate_operation_reference(value, path, registry, require_hash=True)
    if not isinstance(value.get("variant"), str) or not value["variant"]:
        errors.append(f"{path}: variant must be a non-empty string")
    if not isinstance(value.get("bindings"), dict):
        errors.append(f"{path}: bindings must be an object")
    sources = value.get("sources")
    if not isinstance(sources, dict) or set(sources) != {
        "workspace_export",
        "parameterization",
        "runtime_manifest",
        "operation_ref",
    }:
        errors.append(f"{path}: sources must name the four materialization inputs")
    outputs = value.get("outputs")
    if not isinstance(outputs, dict):
        errors.append(f"{path}: outputs must be an object")
    elif set(outputs) != {
        "ui_graph",
        "api_template",
        "bindings",
        "materialization_manifest",
        "ui_graph_hash",
        "api_template_hash",
        "bindings_hash",
    }:
        errors.append(f"{path}: outputs must name the complete materialized draft")
    manifest_hash = value.get("runtime_manifest_hash")
    if manifest_hash is not None and (
        not isinstance(manifest_hash, str) or not SHA256.fullmatch(manifest_hash)
    ):
        errors.append(f"{path}: runtime_manifest_hash must be null or lowercase SHA-256")
    return errors


def validate_runtime_operation_ref(
    value: Any, path: Path, registry: dict[str, dict[str, Any]]
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.operation-ref/1":
        return [f"{path}: invalid operation reference"]
    normalized = {
        "operation": value.get("id"),
        "operation_version": value.get("version"),
        "operation_contract_hash": value.get("contract_hash"),
    }
    return _validate_operation_reference(normalized, path, registry, require_hash=True)


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for schema_path in sorted((root / "schemas").glob("*.json")):
        try:
            load_json(schema_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{schema_path}: invalid JSON: {exc}")

    lock_path = root / "operations.lock.json"
    try:
        lock = load_json(lock_path)
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"{lock_path}: invalid JSON: {exc}"]
    lock_errors, registry = validate_operation_lock(lock, lock_path)
    errors.extend(lock_errors)

    invocation_ids: set[str] = set()
    for path in sorted((root / "invocations").glob("*.json")):
        value = load_json(path)
        errors.extend(validate_invocation(value, path, registry))
        if isinstance(value, dict) and isinstance(value.get("id"), str):
            if value["id"] in invocation_ids:
                errors.append(f"{path}: duplicate invocation id {value['id']!r}")
            invocation_ids.add(value["id"])
    for path in sorted((root / "segments").glob("*.json")):
        errors.extend(validate_segment(load_json(path), path, invocation_ids))
    catalog_path = root / "experiments" / "catalog.json"
    errors.extend(validate_experiment_catalog(load_json(catalog_path), catalog_path, registry))
    for path in sorted((root / "fixtures").glob("*.json")):
        try:
            value = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if value.get("schema") == "inside-valdivia.materialization-plan/1":
            errors.extend(validate_materialization_plan(value, path, registry))
        elif value.get("schema") == "inside-valdivia.operation-ref/1":
            errors.extend(validate_runtime_operation_ref(value, path, registry))
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("validated: operation lock, project invocations, experiments, fixtures, and schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
