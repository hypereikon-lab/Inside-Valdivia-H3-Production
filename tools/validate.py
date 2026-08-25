#!/usr/bin/env python3
"""Validate the repository's semantic contracts without third-party packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_WORKFLOWS = {f"W{value}" for value in range(1, 8)}
OWNERS = {"official-comfy", "cauce", "vanilla-comfy"}
EVIDENCE = {
    "planned",
    "schema-validated",
    "executes",
    "visually-accepted",
    "rejected",
    "blocked",
}
BANNED_SPEC_LANGUAGE = (
    "plate sketch",
    "confluence",
    "seam fix",
    "continuity engine",
    "timeline entity",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_h3_frame_count(value: Any) -> bool:
    return isinstance(value, int) and value >= 5 and (value - 5) % 17 == 0


def validate_workflow_spec(value: Any, path: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path}: spec must be an object"]
    required = {
        "schema",
        "id",
        "version",
        "name",
        "operation",
        "input_contract",
        "output_contract",
        "constraints",
        "graph_contract",
        "evidence",
    }
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{path}: missing fields {missing}")
    if value.get("schema") != "inside-valdivia.h3-workflow-spec/1":
        errors.append(f"{path}: invalid workflow schema")
    if value.get("id") not in EXPECTED_WORKFLOWS:
        errors.append(f"{path}: invalid workflow id {value.get('id')!r}")
    if not isinstance(value.get("version"), int) or value.get("version", 0) < 1:
        errors.append(f"{path}: version must be a positive integer")
    for contract_name in ("input_contract", "output_contract"):
        contract = value.get(contract_name)
        if not isinstance(contract, list) or (contract_name == "output_contract" and not contract):
            errors.append(f"{path}: {contract_name} must be a valid list")
            continue
        names: set[str] = set()
        for port in contract:
            if not isinstance(port, dict) or not {"name", "type", "required"} <= set(port):
                errors.append(f"{path}: malformed {contract_name} port {port!r}")
                continue
            if port["name"] in names:
                errors.append(f"{path}: duplicate {contract_name} port {port['name']!r}")
            names.add(port["name"])
            if not isinstance(port["required"], bool):
                errors.append(f"{path}: required must be boolean for {port['name']!r}")

    stages = value.get("graph_contract")
    if not isinstance(stages, list) or not stages:
        errors.append(f"{path}: graph_contract must be non-empty")
    else:
        orders = []
        for stage in stages:
            if not isinstance(stage, dict):
                errors.append(f"{path}: graph stage must be an object")
                continue
            orders.append(stage.get("order"))
            if stage.get("owner") not in OWNERS:
                errors.append(f"{path}: invalid graph owner {stage.get('owner')!r}")
            if not isinstance(stage.get("role"), str) or not stage["role"].strip():
                errors.append(f"{path}: every graph stage requires a role")
        if orders != list(range(1, len(stages) + 1)):
            errors.append(f"{path}: graph stage order must be contiguous from one")

    constraints = value.get("constraints", {})
    if constraints.get("frame_count_rule") == "17k+5":
        preferred = constraints.get("preferred_frame_count_range")
        if preferred and (
            not isinstance(preferred, list)
            or len(preferred) != 2
            or not all(is_h3_frame_count(item) for item in preferred)
        ):
            errors.append(f"{path}: preferred frame-count endpoints must follow 17k+5")
        for key in ("default_target_frames", "default_guide_frames"):
            if key in constraints and not is_h3_frame_count(constraints[key]):
                errors.append(f"{path}: {key} must follow 17k+5")
        for key in ("valid_guide_lengths", "valid_multi_frame_guide_lengths"):
            if key in constraints and not all(is_h3_frame_count(item) for item in constraints[key]):
                errors.append(f"{path}: every {key} value must follow 17k+5")

    normalized = json.dumps(value, ensure_ascii=False).lower()
    for phrase in BANNED_SPEC_LANGUAGE:
        if phrase in normalized:
            errors.append(f"{path}: rejected legacy phrase {phrase!r}")
    return errors


def validate_segment(value: Any, path: Path, workflow_ids: set[str]) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path}: segment must be an object"]
    errors: list[str] = []
    if value.get("schema") != "inside-valdivia.production-segment/1":
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
    if value.get("workflow_spec") not in workflow_ids:
        errors.append(f"{path}: unknown workflow_spec {value.get('workflow_spec')!r}")
    if value.get("status") not in EVIDENCE | {"materialized", "queued"}:
        errors.append(f"{path}: invalid segment status")
    return errors


def validate_experiment_catalog(value: Any, path: Path, workflow_ids: set[str]) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.h3-experiment-catalog/1":
        return [f"{path}: invalid experiment catalog"]
    errors: list[str] = []
    ids: set[str] = set()
    for experiment in value.get("experiments", []):
        if not isinstance(experiment, dict):
            errors.append(f"{path}: experiment must be an object")
            continue
        required = {"id", "workflow_spec", "question", "fixed", "variable", "measure", "status"}
        if not required <= set(experiment):
            errors.append(f"{path}: malformed experiment {experiment.get('id')!r}")
            continue
        if experiment["id"] in ids:
            errors.append(f"{path}: duplicate experiment id {experiment['id']!r}")
        ids.add(experiment["id"])
        if experiment["workflow_spec"] not in workflow_ids:
            errors.append(f"{path}: unknown workflow {experiment['workflow_spec']!r}")
        if experiment["status"] not in EVIDENCE:
            errors.append(f"{path}: invalid experiment status {experiment['status']!r}")
        if not isinstance(experiment["variable"], dict) or len(experiment["variable"]) != 1:
            errors.append(f"{path}: experiment {experiment['id']!r} must change one variable")
        if not isinstance(experiment["measure"], list) or not experiment["measure"]:
            errors.append(f"{path}: experiment {experiment['id']!r} needs a measure")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for schema_path in sorted((root / "schemas").glob("*.json")):
        try:
            load_json(schema_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{schema_path}: invalid JSON: {exc}")

    workflow_paths = sorted((root / "workflow_specs").glob("*.json"))
    specs: list[dict[str, Any]] = []
    for path in workflow_paths:
        try:
            value = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        errors.extend(validate_workflow_spec(value, path))
        if isinstance(value, dict):
            specs.append(value)
    workflow_ids = {value.get("id") for value in specs}
    if workflow_ids != EXPECTED_WORKFLOWS:
        errors.append(f"workflow set must be W1-W7; found {sorted(workflow_ids)}")

    for path in sorted((root / "segments").glob("*.json")):
        errors.extend(validate_segment(load_json(path), path, workflow_ids))
    catalog_path = root / "experiments" / "catalog.json"
    errors.extend(validate_experiment_catalog(load_json(catalog_path), catalog_path, workflow_ids))
    for path in sorted((root / "fixtures").glob("*.json")):
        try:
            load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("validated: W1-W7, segments, experiments, fixtures, and JSON schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
