#!/usr/bin/env python3
"""Validate project operation invocations without third-party packages."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
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
    topology_key = value.get("topology_key")
    expected_topology_key = f"{value.get('operation')}@{value.get('variant')}"
    if topology_key != expected_topology_key:
        errors.append(f"{path}: topology_key must match operation@variant")
    if not isinstance(value.get("priority"), int) or value["priority"] < 1:
        errors.append(f"{path}: priority must be a positive integer")
    if value.get("status") != "offline-ready":
        errors.append(f"{path}: materialization plan must remain offline-ready")
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
    errors.extend(_validate_canonical_bindings(value, path))
    return errors


def _validate_canonical_bindings(value: dict[str, Any], path: Path) -> list[str]:
    """Validate invariants that do not depend on live ComfyUI node schemas."""

    bindings = value.get("bindings")
    if not isinstance(bindings, dict):
        return []
    errors: list[str] = []
    operation = value.get("operation")
    variant = value.get("variant")
    inputs = bindings.get("inputs")
    if not isinstance(inputs, dict):
        errors.append(f"{path}: canonical bindings require an inputs object")
        return errors

    if operation == "generate.keyframed":
        expected = {
            "text-only": set(),
            "first-frame": {"first_frame"},
            "last-frame": {"last_frame"},
            "first-last": {"first_frame", "last_frame"},
        }.get(variant)
        if expected is not None and set(inputs) != expected:
            errors.append(f"{path}: {variant} requires exactly {sorted(expected)}")
    elif operation == "generate.from_references":
        expected = {
            "image-reference-match": {"reference_images"},
            "image-reference-max": {"reference_images"},
            "video-reference": {"reference_images", "reference_clips"},
        }.get(variant)
        if expected is not None and set(inputs) != expected:
            errors.append(f"{path}: {variant} requires exactly {sorted(expected)}")
        if variant == "image-reference-match" and bindings.get("reference_image_size") != "match":
            errors.append(f"{path}: image-reference-match must guard ref_image_size=match")
        if variant == "image-reference-max" and bindings.get("reference_image_size") != "max":
            errors.append(f"{path}: image-reference-max must guard ref_image_size=max")
        if variant == "video-reference":
            reference_frames = bindings.get("reference_frames")
            if not is_h3_frame_count(reference_frames) or not 48 <= reference_frames <= 360:
                errors.append(f"{path}: video-reference baseline must be a 2-15s H3 length")
            if bindings.get("reference_fps") != 24:
                errors.append(f"{path}: video-reference baseline must be 24 fps")
    elif operation == "generate.with_guides":
        if variant == "guide-clip":
            clips = inputs.get("guide_clips")
            guide_frames = bindings.get("guide_frames")
            if set(inputs) != {"guide_clips"} or not isinstance(clips, list) or len(clips) != 1:
                errors.append(f"{path}: guide-clip requires exactly one guide clip record")
            if not is_h3_frame_count(guide_frames):
                errors.append(f"{path}: guide clip baseline must be on the H3 frame grid")
        else:
            guides = inputs.get("guides")
            expected_count = {"single-anchor": 1, "multi-anchor": 2}.get(variant)
            if expected_count is not None and (
                set(inputs) != {"guides"}
                or not isinstance(guides, list)
                or len(guides) != expected_count
            ):
                errors.append(f"{path}: {variant} requires exactly {expected_count} guide records")
    elif operation == "continue.native_av" and variant == "characterized-layout":
        overlap = bindings.get("overlap_frames")
        extension = bindings.get("extension_frames")
        window = bindings.get("window_frames")
        if not is_h3_frame_count(overlap):
            errors.append(f"{path}: continuation overlap must be on the H3 frame grid")
        if not isinstance(extension, int) or extension < 17 or extension % 17:
            errors.append(f"{path}: continuation extension must be a positive 17-frame increment")
        if (
            not is_h3_frame_count(window)
            or not isinstance(overlap, int)
            or not isinstance(extension, int)
            or overlap + extension != window
        ):
            errors.append(f"{path}: continuation window must equal overlap plus extension")
    elif operation == "connect.two_sided_guides" and variant == "default":
        target = bindings.get("target_frames")
        guide = bindings.get("guide_frames")
        expected_right = target - guide if isinstance(target, int) and isinstance(guide, int) else None
        expected_range = [guide, expected_right]
        if not is_h3_frame_count(target) or not is_h3_frame_count(guide):
            errors.append(f"{path}: target and guide lengths must be on the H3 frame grid")
        if bindings.get("left_guide_frame") != 0 or bindings.get("right_guide_frame") != expected_right:
            errors.append(f"{path}: two-sided guide indices do not match the target")
        if bindings.get("accepted_center_range") != expected_range:
            errors.append(f"{path}: accepted center must exclude both guide ranges")
    elif operation == "frames.assemble" and variant == "ordered-concatenation":
        sources = inputs.get("sources")
        if bindings.get("frame_rate") != 24:
            errors.append(f"{path}: frame assembly must use 24 fps")
        if not isinstance(sources, list) or len(sources) < 2:
            errors.append(f"{path}: ordered concatenation requires at least two source ranges")
    return errors


def validate_materialization_catalog(
    value: Any,
    path: Path,
    registry: dict[str, dict[str, Any]],
    root: Path,
) -> list[str]:
    if (
        not isinstance(value, dict)
        or value.get("schema") != "inside-valdivia.materialization-catalog/1"
    ):
        return [f"{path}: invalid materialization catalog"]
    entries = value.get("plans")
    if not isinstance(entries, list) or not entries:
        return [f"{path}: materialization catalog needs plans"]
    errors: list[str] = []
    ids: set[str] = set()
    keys: set[str] = set()
    priorities: set[int] = set()
    paths: set[Path] = set()
    for entry in entries:
        required = {
            "id",
            "priority",
            "operation",
            "operation_version",
            "operation_contract_hash",
            "variant",
            "topology_key",
            "plan",
            "state",
        }
        if not isinstance(entry, dict) or set(entry) != required:
            errors.append(f"{path}: malformed materialization entry {entry!r}")
            continue
        entry_id = entry["id"]
        if not isinstance(entry_id, str) or not entry_id or entry_id in ids:
            errors.append(f"{path}: invalid or duplicate materialization id {entry_id!r}")
        ids.add(entry_id)
        priority = entry["priority"]
        if not isinstance(priority, int) or priority < 1 or priority in priorities:
            errors.append(f"{path}: invalid or duplicate materialization priority {priority!r}")
        priorities.add(priority)
        errors.extend(_validate_operation_reference(entry, path, registry, require_hash=True))
        expected_key = f"{entry['operation']}@{entry['variant']}"
        if entry["topology_key"] != expected_key or expected_key in keys:
            errors.append(f"{path}: invalid or duplicate topology key {entry['topology_key']!r}")
        keys.add(expected_key)
        if entry["state"] != "offline-ready":
            errors.append(f"{path}: catalog plans must remain offline-ready")
        relative = PurePosixPath(str(entry["plan"]))
        if relative.is_absolute() or ".." in relative.parts or relative.parts[:2] != (
            "materialization",
            "plans",
        ):
            errors.append(f"{path}: unsafe materialization plan path {entry['plan']!r}")
            continue
        plan_path = root / Path(*relative.parts)
        try:
            plan = load_json(plan_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{plan_path}: invalid JSON: {exc}")
            continue
        paths.add(plan_path.resolve())
        errors.extend(validate_materialization_plan(plan, plan_path, registry))
        for field in (
            "priority",
            "operation",
            "operation_version",
            "operation_contract_hash",
            "variant",
            "topology_key",
            "status",
        ):
            expected_field = "state" if field == "status" else field
            if plan.get(field) != entry.get(expected_field):
                errors.append(f"{plan_path}: {field} does not match catalog entry")
    if priorities != set(range(1, len(entries) + 1)):
        errors.append(f"{path}: priorities must be contiguous from one")
    expected_paths = {
        item.resolve() for item in (root / "materialization" / "plans").glob("*.json")
    }
    if paths != expected_paths:
        errors.append(f"{path}: materialization catalog and plan directory differ")
    return errors


def validate_media_catalog(value: Any, path: Path) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.media-catalog/1":
        return [f"{path}: invalid media catalog"]
    records = value.get("media")
    if not isinstance(records, list):
        return [f"{path}: media must be a list"]
    errors: list[str] = []
    logical_ids: set[str] = set()
    content_hashes: set[str] = set()
    for record in records:
        required = {
            "logical_id",
            "content_hash",
            "comfy_filename",
            "kind",
            "frame_count",
            "fps",
            "geometry",
            "size_bytes",
            "origin_invocation",
            "status",
        }
        if not isinstance(record, dict) or set(record) != required:
            errors.append(f"{path}: malformed media record {record!r}")
            continue
        logical_id = record["logical_id"]
        if not isinstance(logical_id, str) or not logical_id or logical_id in logical_ids:
            errors.append(f"{path}: invalid or duplicate media logical_id {logical_id!r}")
        logical_ids.add(logical_id)
        content_hash = record["content_hash"]
        if not isinstance(content_hash, str) or not SHA256.fullmatch(content_hash):
            errors.append(f"{path}: media content_hash must be lowercase SHA-256")
        elif content_hash in content_hashes:
            errors.append(f"{path}: duplicate media content_hash {content_hash!r}")
        else:
            content_hashes.add(content_hash)
        if record["kind"] not in {"image", "video", "native-av-latent"}:
            errors.append(f"{path}: invalid media kind {record['kind']!r}")
        if not isinstance(record["comfy_filename"], str) or not record["comfy_filename"]:
            errors.append(f"{path}: comfy_filename is required")
        if record["frame_count"] is not None and (
            not isinstance(record["frame_count"], int) or record["frame_count"] < 1
        ):
            errors.append(f"{path}: frame_count must be null or positive")
        if record["fps"] is not None and (
            not isinstance(record["fps"], (int, float)) or record["fps"] <= 0
        ):
            errors.append(f"{path}: fps must be null or positive")
        geometry = record["geometry"]
        if geometry is not None and (
            not isinstance(geometry, list)
            or len(geometry) != 2
            or not all(isinstance(item, int) and item > 0 for item in geometry)
        ):
            errors.append(f"{path}: geometry must be null or [width, height]")
        if not isinstance(record["size_bytes"], int) or record["size_bytes"] < 0:
            errors.append(f"{path}: size_bytes must be non-negative")
        if record["status"] not in {"hash-verified", "runtime-available", "archived"}:
            errors.append(f"{path}: invalid media status {record['status']!r}")
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
    materialization_path = root / "materialization" / "catalog.json"
    errors.extend(
        validate_materialization_catalog(
            load_json(materialization_path), materialization_path, registry, root
        )
    )
    media_path = root / "media" / "catalog.json"
    errors.extend(validate_media_catalog(load_json(media_path), media_path))
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
    print(
        "validated: operation lock, project invocations, materialization plans, "
        "media, experiments, fixtures, and schemas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
