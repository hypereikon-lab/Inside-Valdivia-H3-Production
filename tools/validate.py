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


def is_h3_visual_boundary(value: Any) -> bool:
    """Return whether a local pixel-frame boundary maps to whole H3 tokens."""

    if not isinstance(value, int) or value < 0:
        return False
    covered = 0
    index = 0
    pattern = (1, 4, 4, 4, 4)
    while covered < value:
        covered += pattern[index % len(pattern)]
        index += 1
    return covered == value


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
            "video-reference-with-guide": {
                "reference_images",
                "reference_clips",
                "temporal_guide",
            },
        }.get(variant)
        if expected is not None and set(inputs) != expected:
            errors.append(f"{path}: {variant} requires exactly {sorted(expected)}")
        if variant == "image-reference-match" and bindings.get("reference_image_size") != "match":
            errors.append(f"{path}: image-reference-match must guard ref_image_size=match")
        if variant == "image-reference-max" and bindings.get("reference_image_size") != "max":
            errors.append(f"{path}: image-reference-max must guard ref_image_size=max")
        if variant in {"video-reference", "video-reference-with-guide"}:
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
        elif variant == "first-last-interior":
            guides = inputs.get("guides")
            if (
                set(inputs) != {"first_frame", "last_frame", "guides"}
                or not isinstance(guides, list)
                or not guides
            ):
                errors.append(
                    f"{path}: first-last-interior requires endpoint frames and guides"
                )
        else:
            guides = inputs.get("guides")
            expected_count = {"single-anchor": 1, "multi-anchor": 2}.get(variant)
            if expected_count is not None and (
                set(inputs) != {"guides"}
                or not isinstance(guides, list)
                or len(guides) != expected_count
            ):
                errors.append(f"{path}: {variant} requires exactly {expected_count} guide records")
    elif operation == "continue.native_av":
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
        expected_transport = {
            "keyframe-overlap": "minimax_keyframes",
            "masked-overlap": "noise_mask",
            "masked-overlap-future-guide": "noise_mask",
        }.get(variant)
        if expected_transport and bindings.get("overlap_transport") != expected_transport:
            errors.append(f"{path}: continuation overlap transport does not match variant")
        if variant.startswith("masked-overlap"):
            errors.extend(_validate_mask_bindings(bindings.get("mask"), path))
        expected_inputs = {
            "keyframe-overlap": {"source_native_av_latent", "source_timeline_origin"},
            "masked-overlap": {"source_native_av_latent", "source_timeline_origin"},
            "masked-overlap-future-guide": {
                "source_native_av_latent",
                "source_timeline_origin",
                "future_guide",
            },
        }.get(variant)
        if expected_inputs is not None and set(inputs) != expected_inputs:
            errors.append(f"{path}: continuation inputs do not match {variant}")
    elif operation == "complete.native_av":
        target = bindings.get("target_frames")
        start = bindings.get("unknown_start_frame")
        count = bindings.get("unknown_frame_count")
        if not is_h3_frame_count(target):
            errors.append(f"{path}: completion target must satisfy 17k+5")
        if (
            not isinstance(start, int)
            or not isinstance(count, int)
            or count < 1
            or not isinstance(target, int)
            or start < 0
            or start + count > target
            or not is_h3_visual_boundary(start)
            or not is_h3_visual_boundary(start + count)
        ):
            errors.append(f"{path}: completion interval must end on visual-token boundaries")
        errors.extend(_validate_mask_bindings(bindings.get("mask"), path))
        expected_inputs = {
            "two-sided-infill": {"target_native_av_latent"},
            "local-replacement": {"base_native_av_latent"},
            "backward-prefix": {"known_right_native_av_latent"},
            "two-source-connection": {
                "left_native_av_latent",
                "right_native_av_latent",
            },
        }.get(variant)
        if expected_inputs is not None and set(inputs) != expected_inputs:
            errors.append(f"{path}: completion inputs do not match {variant}")
        if variant == "backward-prefix" and (
            bindings.get("known_right_target_frame") != start + count
            or bindings.get("known_right_frames") != target - (start + count)
        ):
            errors.append(f"{path}: backward-prefix ranges do not cover the target")
        if variant == "two-source-connection":
            left = bindings.get("left_span")
            right = bindings.get("right_span")
            if (
                not isinstance(left, dict)
                or not isinstance(right, dict)
                or left.get("target_frame") != 0
                or left.get("frame_count") != start
                or right.get("target_frame") != start + count
                or right.get("frame_count") != target - (start + count)
            ):
                errors.append(f"{path}: two-source spans do not exactly flank the interval")
    elif operation == "rollback.native_av":
        source_frames = bindings.get("source_frame_count")
        cut = bindings.get("cut_frame")
        if (
            not is_h3_frame_count(source_frames)
            or not is_h3_frame_count(cut)
            or not isinstance(source_frames, int)
            or not isinstance(cut, int)
            or cut >= source_frames
            or (source_frames - cut) % 17
        ):
            errors.append(f"{path}: rollback cut must leave a synchronized non-empty suffix")
        if set(inputs) != {"source_native_av_latent"}:
            errors.append(f"{path}: rollback requires exactly one native AV source")
    elif operation == "frames.assemble" and variant == "ordered-concatenation":
        sources = inputs.get("sources")
        if bindings.get("frame_rate") != 24:
            errors.append(f"{path}: frame assembly must use 24 fps")
        if not isinstance(sources, list) or len(sources) < 2:
            errors.append(f"{path}: ordered concatenation requires at least two source ranges")
    return errors


def _validate_mask_bindings(value: Any, path: Path) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path}: masked native operation requires a mask object"]
    required = {
        "inside_strength_video",
        "outside_strength_video",
        "inside_strength_audio",
        "outside_strength_audio",
        "fade_in_frames",
        "fade_out_frames",
        "curve",
        "combine",
    }
    allowed = required | {"start_frame", "frame_count"}
    errors: list[str] = []
    if not required <= set(value) or not set(value) <= allowed:
        errors.append(f"{path}: mask fields are incomplete or unexpected")
        return errors
    for name in (
        "inside_strength_video",
        "outside_strength_video",
        "inside_strength_audio",
        "outside_strength_audio",
    ):
        strength = value[name]
        if not isinstance(strength, (int, float)) or not 0 <= strength <= 1:
            errors.append(f"{path}: {name} must lie in [0,1]")
    if value["curve"] not in {"linear", "smoothstep", "smootherstep"}:
        errors.append(f"{path}: invalid mask curve")
    if value["combine"] not in {"replace", "maximum", "minimum", "multiply"}:
        errors.append(f"{path}: invalid mask combine mode")
    if any(not isinstance(value[name], int) or value[name] < 0 for name in ("fade_in_frames", "fade_out_frames")):
        errors.append(f"{path}: mask fades must be non-negative integers")
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


def _safe_project_path(value: Any, path: Path, root: Path, prefix: tuple[str, ...]) -> tuple[Path | None, list[str]]:
    relative = PurePosixPath(str(value))
    if relative.is_absolute() or ".." in relative.parts or relative.parts[: len(prefix)] != prefix:
        return None, [f"{path}: unsafe project path {value!r}"]
    return root / Path(*relative.parts), []


def validate_rolling_plan(
    value: Any,
    path: Path,
    registry: dict[str, dict[str, Any]],
    root: Path,
    cauce_commit: str,
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.rolling-plan/1":
        return [f"{path}: invalid rolling plan"]
    errors: list[str] = []
    if value.get("status") != "offline-ready" or value.get("frame_rate") != 24:
        errors.append(f"{path}: rolling plans must be offline-ready at 24 fps")
    locks = value.get("source_locks")
    if not isinstance(locks, dict) or set(locks) != {
        "cauce_commit", "runtime_repository", "runtime_commit"
    }:
        errors.append(f"{path}: rolling plan needs exact CAUCE and Runtime source locks")
    else:
        if locks.get("cauce_commit") != cauce_commit:
            errors.append(f"{path}: rolling CAUCE commit does not match operation lock")
        if not isinstance(locks.get("runtime_commit"), str) or not GIT_SHA.fullmatch(
            locks["runtime_commit"]
        ):
            errors.append(f"{path}: rolling Runtime commit must be a full Git SHA")
        if not isinstance(locks.get("runtime_repository"), str) or not locks["runtime_repository"]:
            errors.append(f"{path}: rolling Runtime repository is required")
    if value.get("execution") != {
        "runtime_schema": "comfy.run-series/1",
        "requires_materialized_graphs": True,
        "auto_wire_outputs": False,
        "binding_mode": "explicit-prebound",
    }:
        errors.append(f"{path}: rolling execution boundary is not explicit")
    if value.get("checkpoint_policy") != {
        "frequency": "after-each-step",
        "immutability": "content-addressed",
        "receipt_required": True,
    }:
        errors.append(f"{path}: every rolling step needs an immutable checkpoint")
    branch = value.get("branch_policy")
    if not isinstance(branch, dict) or branch.get("mode") != "new-plan-from-checkpoint" or branch.get("mutate_existing_plan") is not False:
        errors.append(f"{path}: branches must start as new plans from checkpoints")
    elif {
        "operation": branch.get("rollback_operation"),
        "operation_version": branch.get("rollback_operation_version"),
        "operation_contract_hash": branch.get("rollback_operation_contract_hash"),
    } != {
        "operation": "rollback.native_av",
        "operation_version": registry.get("rollback.native_av", {}).get("version"),
        "operation_contract_hash": registry.get("rollback.native_av", {}).get("contract_hash"),
    }:
        errors.append(f"{path}: branch rollback operation does not match lock")

    steps = value.get("steps")
    if not isinstance(steps, list) or not steps:
        return errors + [f"{path}: rolling plan requires steps"]
    ids: set[str] = set()
    states: set[str] = set()
    previous_id: str | None = None
    previous_state: str | None = None
    for position, step in enumerate(steps, start=1):
        materialization: Any = None
        if not isinstance(step, dict):
            errors.append(f"{path}: rolling step must be an object")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or not step_id or step_id in ids:
            errors.append(f"{path}: invalid or duplicate rolling step id {step_id!r}")
        ids.add(step_id)
        if step.get("position") != position or step.get("depends_on") != previous_id:
            errors.append(f"{path}: rolling steps must form one exact serial chain")
        errors.extend(_validate_operation_reference(step, path, registry, require_hash=True))
        expected_key = f"{step.get('operation')}@{step.get('variant')}"
        if step.get("topology_key") != expected_key or step.get("status") != "offline-ready":
            errors.append(f"{path}: rolling step topology or status is invalid")
        plan_path, path_errors = _safe_project_path(
            step.get("materialization_plan"), path, root, ("materialization", "plans")
        )
        errors.extend(path_errors)
        if plan_path is not None:
            try:
                materialization = load_json(plan_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{plan_path}: invalid JSON: {exc}")
            else:
                for field in (
                    "operation", "operation_version", "operation_contract_hash",
                    "variant", "topology_key",
                ):
                    if step.get(field) != materialization.get(field):
                        errors.append(f"{path}: rolling step {step_id!r} disagrees with its materialization plan")
                        break
        state = step.get("output_native_state")
        if not isinstance(state, str) or not state or state in states:
            errors.append(f"{path}: invalid or duplicate rolling native state {state!r}")
        states.add(state)
        bindings = step.get("input_bindings")
        if not isinstance(bindings, dict):
            errors.append(f"{path}: rolling input_bindings must be an object")
        else:
            planned_inputs = (
                materialization.get("bindings", {}).get("inputs")
                if isinstance(materialization, dict)
                else None
            )
            if isinstance(planned_inputs, dict) and set(bindings) != set(planned_inputs):
                errors.append(
                    f"{path}: step {step_id!r} input bindings disagree with its materialization plan"
                )
            if previous_id is not None:
                links = [item for item in bindings.values() if isinstance(item, dict)]
                if not any(
                    item.get("from_step") == previous_id
                    and item.get("output_native_state") == previous_state
                    for item in links
                ):
                    errors.append(f"{path}: step {step_id!r} must explicitly bind the preceding native state")
        previous_id = step_id if isinstance(step_id, str) else None
        previous_state = state if isinstance(state, str) else None
    return errors


def validate_rolling_catalog(
    value: Any,
    path: Path,
    registry: dict[str, dict[str, Any]],
    root: Path,
    cauce_commit: str,
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.rolling-catalog/1":
        return [f"{path}: invalid rolling catalog"]
    entries = value.get("plans")
    if not isinstance(entries, list) or not entries:
        return [f"{path}: rolling catalog needs plans"]
    errors: list[str] = []
    ids: set[str] = set()
    paths: set[Path] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"id", "plan", "status"}:
            errors.append(f"{path}: malformed rolling catalog entry {entry!r}")
            continue
        if entry["id"] in ids or entry["status"] != "offline-ready":
            errors.append(f"{path}: duplicate id or invalid rolling status {entry['id']!r}")
        ids.add(entry["id"])
        plan_path, path_errors = _safe_project_path(entry["plan"], path, root, ("rolling", "plans"))
        errors.extend(path_errors)
        if plan_path is None:
            continue
        try:
            plan = load_json(plan_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{plan_path}: invalid JSON: {exc}")
            continue
        paths.add(plan_path.resolve())
        errors.extend(validate_rolling_plan(plan, plan_path, registry, root, cauce_commit))
        if plan.get("id") != entry["id"] or plan.get("status") != entry["status"]:
            errors.append(f"{plan_path}: rolling plan does not match catalog entry")
    expected_paths = {item.resolve() for item in (root / "rolling" / "plans").glob("*.json")}
    if paths != expected_paths:
        errors.append(f"{path}: rolling catalog and plan directory differ")
    return errors


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
    rolling_path = root / "rolling" / "catalog.json"
    errors.extend(
        validate_rolling_catalog(
            load_json(rolling_path),
            rolling_path,
            registry,
            root,
            lock.get("source", {}).get("commit"),
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
        "rolling plans, media, experiments, fixtures, and schemas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
