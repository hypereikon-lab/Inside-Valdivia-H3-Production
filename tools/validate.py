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
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
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


def ceil_h3_frame_count(value: int) -> int:
    resolved = max(5, int(value))
    remainder = (resolved - 5) % 17
    return resolved if remainder == 0 else resolved + 17 - remainder


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


def validate_archetype_lock(
    value: Any,
    path: Path,
    materialization_catalog: dict[str, Any],
    cauce_commit: str,
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.cauce-archetype-lock/1":
        return [f"{path}: invalid archetype lock"]
    if set(value) != {"schema", "source", "archetypes"}:
        return [f"{path}: archetype lock fields are incomplete or unexpected"]
    errors: list[str] = []
    source = value.get("source")
    if not isinstance(source, dict) or set(source) != {"repository", "commit", "catalog_hash"}:
        errors.append(f"{path}: archetype source lock is incomplete")
    else:
        if source.get("commit") != cauce_commit:
            errors.append(f"{path}: archetype and operation locks require different CAUCE commits")
        if not isinstance(source.get("catalog_hash"), str) or not SHA256.fullmatch(
            source["catalog_hash"]
        ):
            errors.append(f"{path}: archetype catalog_hash must be lowercase SHA-256")
        if not isinstance(source.get("repository"), str) or not source["repository"]:
            errors.append(f"{path}: archetype source repository is required")

    entries = value.get("archetypes")
    if not isinstance(entries, list) or not entries:
        return errors + [f"{path}: archetype lock needs entries"]
    archetype_ids: set[str] = set()
    signatures: set[str] = set()
    topology_keys: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "id", "topology_signature", "topology_keys"
        }:
            errors.append(f"{path}: malformed archetype entry {entry!r}")
            continue
        archetype_id = entry["id"]
        signature = entry["topology_signature"]
        keys = entry["topology_keys"]
        if (
            not isinstance(archetype_id, str)
            or not re.fullmatch(r"[a-z][a-z0-9-]*", archetype_id)
            or archetype_id in archetype_ids
        ):
            errors.append(f"{path}: invalid or duplicate archetype id {archetype_id!r}")
        else:
            archetype_ids.add(archetype_id)
        if not isinstance(signature, str) or not SHA256.fullmatch(signature):
            errors.append(f"{path}: invalid or duplicate topology signature {signature!r}")
        elif signature in signatures:
            errors.append(f"{path}: invalid or duplicate topology signature {signature!r}")
        else:
            signatures.add(signature)
        if (
            not isinstance(keys, list)
            or not keys
            or any(not isinstance(key, str) for key in keys)
            or keys != sorted(set(keys))
        ):
            errors.append(f"{path}: archetype {archetype_id!r} needs sorted unique topology keys")
        else:
            topology_keys.extend(keys)
    planned = [entry["topology_key"] for entry in materialization_catalog.get("plans", [])]
    if len(topology_keys) != len(set(topology_keys)):
        errors.append(f"{path}: each topology may belong to only one archetype")
    if set(topology_keys) != set(planned):
        errors.append(f"{path}: archetypes must cover every materialization topology exactly once")
    return errors


def validate_compatibility_lock(
    value: Any,
    path: Path,
    *,
    cauce_commit: str,
    runtime_commit: str,
    workspace_commit: str,
    repository_control_commit: str,
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.compatibility-lock/1":
        return [f"{path}: invalid compatibility lock"]
    if set(value) != {"schema", "captured_at", "components", "platform"}:
        return [f"{path}: compatibility lock fields are incomplete or unexpected"]
    errors: list[str] = []
    if not isinstance(value.get("captured_at"), str) or not value["captured_at"]:
        errors.append(f"{path}: captured_at is required")
    components = value.get("components")
    expected_commits = {
        "cauce": cauce_commit,
        "runtime_control": runtime_commit,
        "workspace_control": workspace_commit,
        "repository_control": repository_control_commit,
    }
    if not isinstance(components, dict) or set(components) != set(expected_commits):
        errors.append(
            f"{path}: compatibility components must be cauce, runtime_control, "
            "workspace_control, repository_control"
        )
    else:
        expected_fields = {
            "repository", "version", "commit", "tree", "metadata_sha256",
            "distribution", "registry_node_id",
        }
        for component_id, expected_commit in expected_commits.items():
            component = components[component_id]
            if not isinstance(component, dict) or set(component) != expected_fields:
                errors.append(f"{path}: malformed component {component_id!r}")
                continue
            if not isinstance(component["repository"], str) or not component["repository"].startswith(
                "https://github.com/"
            ):
                errors.append(f"{path}: {component_id} repository must be an HTTPS GitHub URL")
            if not isinstance(component["version"], str) or not SEMVER.fullmatch(component["version"]):
                errors.append(f"{path}: {component_id} version must be semantic")
            if component["commit"] != expected_commit:
                errors.append(f"{path}: {component_id} commit disagrees with the live gate")
            if not isinstance(component["tree"], str) or not GIT_SHA.fullmatch(component["tree"]):
                errors.append(f"{path}: {component_id} tree must be a full Git object id")
            if not isinstance(component["metadata_sha256"], str) or not SHA256.fullmatch(
                component["metadata_sha256"]
            ):
                errors.append(f"{path}: {component_id} metadata hash must be SHA-256")
            if component["distribution"] not in {
                "registry-prepared-unpublished",
                "registry-published",
                "source-package",
                "public-git-extension",
            }:
                errors.append(f"{path}: invalid distribution state for {component_id}")
            registry_id = component["registry_node_id"]
            if registry_id is not None and (
                not isinstance(registry_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", registry_id)
            ):
                errors.append(f"{path}: invalid registry node id for {component_id}")

    platform = value.get("platform")
    if not isinstance(platform, dict) or set(platform) != {
        "core_profile", "full_profile", "frontend", "manager"
    }:
        return errors + [f"{path}: compatibility platform fields are incomplete"]
    for profile_id in ("core_profile", "full_profile"):
        profile = platform[profile_id]
        if not isinstance(profile, dict) or set(profile) != {"minimum_comfyui", "basis"}:
            errors.append(f"{path}: malformed {profile_id}")
        elif not isinstance(profile["minimum_comfyui"], str) or not SEMVER.fullmatch(
            profile["minimum_comfyui"]
        ):
            errors.append(f"{path}: {profile_id} minimum_comfyui must be semantic")
    frontend = platform["frontend"]
    if not isinstance(frontend, dict) or set(frontend) != {
        "last_live_tested", "next_compatibility_target", "target_state"
    }:
        errors.append(f"{path}: malformed frontend compatibility record")
    else:
        for name in ("last_live_tested", "next_compatibility_target"):
            if not isinstance(frontend[name], str) or not SEMVER.fullmatch(frontend[name]):
                errors.append(f"{path}: frontend {name} must be semantic")
        if frontend["target_state"] != "requires-live-diagnostic":
            errors.append(f"{path}: frontend target must remain requires-live-diagnostic")
    manager = platform["manager"]
    if not isinstance(manager, dict) or set(manager) != {
        "last_live_observed", "first_install_policy"
    }:
        errors.append(f"{path}: malformed Manager compatibility record")
    elif manager["first_install_policy"] != "public-registry-or-journaled-public-git-only":
        errors.append(f"{path}: Manager first-install policy is not fail-closed")
    core = platform["core_profile"]
    full = platform["full_profile"]
    if (
        isinstance(core, dict)
        and isinstance(full, dict)
        and isinstance(core.get("minimum_comfyui"), str)
        and isinstance(full.get("minimum_comfyui"), str)
        and SEMVER.fullmatch(core["minimum_comfyui"])
        and SEMVER.fullmatch(full["minimum_comfyui"])
        and tuple(map(int, full["minimum_comfyui"].split(".")))
        < tuple(map(int, core["minimum_comfyui"].split(".")))
    ):
        errors.append(f"{path}: full profile cannot require an older ComfyUI than core")
    return errors


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


def validate_training_catalog(value: Any, path: Path, root: Path) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.h3-training-catalog/1":
        return [f"{path}: invalid H3 training catalog"]
    errors: list[str] = []
    source = value.get("source")
    if not isinstance(source, dict):
        errors.append(f"{path}: training source must be an object")
    else:
        if not isinstance(source.get("repository"), str) or not source["repository"]:
            errors.append(f"{path}: training source repository is required")
        if not isinstance(source.get("commit"), str) or not GIT_SHA.fullmatch(source["commit"]):
            errors.append(f"{path}: training source commit must be a full Git SHA")
        if not isinstance(source.get("observed_at"), str) or not source["observed_at"]:
            errors.append(f"{path}: training source observation date is required")

    hardware = value.get("hardware_target")
    if not isinstance(hardware, dict):
        errors.append(f"{path}: training hardware target must be an object")
    else:
        for key in ("vram_gb", "ram_gb", "maximum_free_disk_gb"):
            if not isinstance(hardware.get(key), int) or hardware[key] <= 0:
                errors.append(f"{path}: hardware {key} must be a positive integer")

    entries = value.get("recipes")
    if not isinstance(entries, list) or not entries:
        return errors + [f"{path}: training recipes must be a non-empty list"]
    ids: set[str] = set()
    paths: set[Path] = set()
    allowed_status = {"lab-gated", "requires-task-adapter", "validated", "rejected"}
    required_recipe_fields = {
        "schema",
        "id",
        "objective",
        "status",
        "model",
        "adapter",
        "upstream_baseline",
        "dataset",
        "hardware_gate",
        "evaluation",
        "promotion",
    }
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"id", "path", "status"}:
            errors.append(f"{path}: malformed training recipe entry {entry!r}")
            continue
        recipe_id = entry.get("id")
        if not isinstance(recipe_id, str) or not recipe_id:
            errors.append(f"{path}: training recipe id is required")
            continue
        if recipe_id in ids:
            errors.append(f"{path}: duplicate training recipe id {recipe_id!r}")
        ids.add(recipe_id)
        if entry.get("status") not in allowed_status:
            errors.append(f"{path}: invalid training recipe status {entry.get('status')!r}")
        raw_recipe_path = entry.get("path")
        if not isinstance(raw_recipe_path, str) or not raw_recipe_path:
            errors.append(f"{path}: recipe {recipe_id!r} needs a path")
            continue
        posix_path = PurePosixPath(raw_recipe_path)
        if posix_path.is_absolute() or ".." in posix_path.parts:
            errors.append(f"{path}: unsafe training recipe path {raw_recipe_path!r}")
            continue
        recipe_path = root.joinpath(*posix_path.parts).resolve()
        if recipe_path in paths:
            errors.append(f"{path}: duplicate training recipe path {raw_recipe_path!r}")
        paths.add(recipe_path)
        if not recipe_path.is_file():
            errors.append(f"{path}: missing training recipe {raw_recipe_path!r}")
            continue
        recipe = load_json(recipe_path)
        if not isinstance(recipe, dict) or recipe.get("schema") != "inside-valdivia.h3-training-recipe/1":
            errors.append(f"{recipe_path}: invalid H3 training recipe")
            continue
        if set(recipe) != required_recipe_fields:
            errors.append(f"{recipe_path}: training recipe fields do not match the schema")
        if recipe.get("id") != recipe_id or recipe.get("status") != entry.get("status"):
            errors.append(f"{recipe_path}: recipe id/status does not match the catalog")
        model = recipe.get("model")
        if not isinstance(model, dict) or model.get("full_finetune") is not False:
            errors.append(f"{recipe_path}: full fine-tuning must remain disabled for the lab target")
        adapter = recipe.get("adapter")
        if not isinstance(adapter, dict) or adapter.get("method") != "LoRA":
            errors.append(f"{recipe_path}: current training recipes must use LoRA")
        else:
            if adapter.get("rank") != 32:
                errors.append(f"{recipe_path}: LoRA rank must match the pinned upstream baseline")
            expected_modules = {
                "attn.qkv_proj",
                "attn.out_proj",
                "mlp.fc1",
                "mlp.fc2",
            }
            if set(adapter.get("target_modules", [])) != expected_modules:
                errors.append(f"{recipe_path}: LoRA target modules differ from pinned upstream NF4 example")
        baseline = recipe.get("upstream_baseline")
        if not isinstance(baseline, dict):
            errors.append(f"{recipe_path}: upstream baseline must be an object")
        else:
            if not is_h3_frame_count(baseline.get("frames")):
                errors.append(f"{recipe_path}: training frame count must be legal for H3")
            for dimension in ("height", "width"):
                size = baseline.get(dimension)
                if not isinstance(size, int) or size <= 0 or size % 32:
                    errors.append(f"{recipe_path}: training {dimension} must be a positive multiple of 32")
        gate = recipe.get("hardware_gate")
        if not isinstance(gate, dict) or gate.get("full_finetune_allowed") is not False:
            errors.append(f"{recipe_path}: hardware gate must reject full fine-tuning")
        evaluation = recipe.get("evaluation")
        if not isinstance(evaluation, dict) or not evaluation.get("controls") or not evaluation.get("measures"):
            errors.append(f"{recipe_path}: training evaluation needs controls and measures")
        promotion = recipe.get("promotion")
        if not isinstance(promotion, dict) or not promotion.get("requires"):
            errors.append(f"{recipe_path}: training promotion requirements are missing")
    expected_paths = {item.resolve() for item in (root / "training" / "recipes").glob("*.json")}
    if paths != expected_paths:
        errors.append(f"{path}: training catalog and recipe directory differ")
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
    status = value.get("status")
    if status not in {"offline-ready", "schema-validated-draft"}:
        errors.append(
            f"{path}: materialization plan status must be offline-ready or "
            "schema-validated-draft"
        )
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
    validation = value.get("validation")
    if not isinstance(validation, dict):
        errors.append(f"{path}: validation must be an object")
    else:
        schema_status = validation.get("schema_status")
        has_all_outputs = isinstance(outputs, dict) and all(
            isinstance(outputs.get(field), str) and outputs[field]
            for field in (
                "ui_graph",
                "api_template",
                "bindings",
                "materialization_manifest",
                "ui_graph_hash",
                "api_template_hash",
                "bindings_hash",
            )
        )
        has_all_sources = isinstance(sources, dict) and all(
            isinstance(sources.get(field), str) and sources[field]
            for field in (
                "workspace_export",
                "parameterization",
                "runtime_manifest",
                "operation_ref",
            )
        )
        if status == "schema-validated-draft" and (
            schema_status != "validated"
            or not has_all_outputs
            or not has_all_sources
            or not isinstance(value.get("runtime_manifest_hash"), str)
        ):
            errors.append(
                f"{path}: schema-validated-draft requires validated schema, "
                "runtime manifest, sources, outputs, and hashes"
            )
        if status == "offline-ready" and schema_status != "pending":
            errors.append(f"{path}: offline-ready plans must remain pending")
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
    artifact = bindings.get("artifact")
    expected_artifact_fields = {
        "frame_rate",
        "filename_prefix",
        "format",
        "codec",
        "history_resolvable",
        "retain_native_state",
    }
    if not isinstance(artifact, dict) or set(artifact) != expected_artifact_fields:
        errors.append(f"{path}: canonical bindings require the exact artifact contract")
    else:
        expected_frame_rate: int | float = 24
        if operation == "densify.temporal":
            expected_frame_rate = bindings.get("delivery_fps")
        if artifact.get("frame_rate") != expected_frame_rate:
            errors.append(
                f"{path}: materialized artifact frame_rate must be "
                f"{expected_frame_rate} for {operation}"
            )
        if artifact.get("filename_prefix") is not None:
            errors.append(f"{path}: filename_prefix must remain null before live pairing")
        if artifact.get("format") != "auto" or artifact.get("codec") != "auto":
            errors.append(f"{path}: format and codec must remain auto before live pairing")
        if artifact.get("history_resolvable") is not True:
            errors.append(f"{path}: artifacts must be resolvable from prompt history")
        expected_native_state = operation != "frames.assemble"
        if artifact.get("retain_native_state") is not expected_native_state:
            errors.append(
                f"{path}: retain_native_state must be {expected_native_state} "
                f"for {operation}"
            )
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
    elif operation == "edit.masked_video":
        target = bindings.get("target_frames")
        start = bindings.get("mask_start_frame")
        count = bindings.get("mask_frame_count")
        if not is_h3_frame_count(target):
            errors.append(f"{path}: masked edit target must satisfy 17k+5")
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
            errors.append(f"{path}: masked edit interval must end on visual-token boundaries")
        video_mask = bindings.get("video_mask")
        errors.extend(_validate_video_mask_bindings(video_mask, path))
        expected_cardinality = {
            "static-spatial": "static",
            "animated-spatiotemporal": "per-selected-frame",
            "local-retake": "per-selected-frame",
        }.get(variant)
        if isinstance(video_mask, dict) and expected_cardinality is not None:
            if video_mask.get("cardinality") != expected_cardinality:
                errors.append(f"{path}: video-mask cardinality does not match {variant}")
        expected_inputs = {
            "static-spatial": {"source_native_av_latent", "video_mask"},
            "animated-spatiotemporal": {
                "source_native_av_latent",
                "video_mask_sequence",
            },
            "local-retake": {"source_native_av_latent", "video_mask_sequence"},
        }.get(variant)
        if expected_inputs is not None and set(inputs) != expected_inputs:
            errors.append(f"{path}: masked edit inputs do not match {variant}")
        if variant == "local-retake":
            errors.extend(_validate_mask_bindings(bindings.get("temporal_mask"), path))
            if isinstance(video_mask, dict) and video_mask.get("combine") != "multiply":
                errors.append(f"{path}: local retake must intersect temporal and video masks")
    elif operation == "reframe.outpaint_video":
        source_resolution = bindings.get("source_resolution")
        target_resolution = bindings.get("target_resolution")
        offset_x = bindings.get("offset_x")
        offset_y = bindings.get("offset_y")
        if not _is_aligned_resolution(source_resolution) or not _is_aligned_resolution(
            target_resolution
        ):
            errors.append(f"{path}: outpaint resolutions must be [height,width] multiples of 32")
        else:
            source_h, source_w = source_resolution
            target_h, target_w = target_resolution
            if target_h < source_h or target_w < source_w or target_resolution == source_resolution:
                errors.append(f"{path}: outpaint target must strictly expand the source canvas")
            if (
                not isinstance(offset_x, int)
                or not isinstance(offset_y, int)
                or offset_x < 0
                or offset_y < 0
                or offset_x % 32
                or offset_y % 32
                or offset_x + source_w > target_w
                or offset_y + source_h > target_h
            ):
                errors.append(f"{path}: outpaint offset must be aligned and fit the target canvas")
            elif variant == "centered" and (
                offset_x * 2 != target_w - source_w
                or offset_y * 2 != target_h - source_h
            ):
                errors.append(f"{path}: centered outpaint requires equal margins")
        if bindings.get("source_strength_video") != 0.0:
            errors.append(f"{path}: outpaint baseline must preserve the source region")
        if bindings.get("new_region_strength_video") != 1.0:
            errors.append(f"{path}: outpaint baseline must generate the complete new region")
        if bindings.get("audio_strength") != 0.0:
            errors.append(f"{path}: outpaint baseline must preserve structural audio")
        if set(inputs) != {"source_native_av_latent"}:
            errors.append(f"{path}: outpaint requires exactly one native AV source")
    elif operation == "refine.video":
        if not is_h3_frame_count(bindings.get("target_frames")):
            errors.append(f"{path}: refinement target must satisfy 17k+5")
        if bindings.get("video_denoise_strength") is not None:
            errors.append(f"{path}: refinement strength must remain unbound before live characterization")
        values = bindings.get("characterization_values")
        if (
            not isinstance(values, list)
            or not values
            or values != sorted(set(values))
            or any(not isinstance(item, (int, float)) or not 0 < item <= 1 for item in values)
        ):
            errors.append(f"{path}: refinement characterization values must be unique ordered strengths in (0,1]")
        if bindings.get("audio_strength") != 0.0:
            errors.append(f"{path}: refinement baseline must preserve structural audio")
        expected_inputs = {
            "full-frame": {"source_native_av_latent"},
            "masked": {"source_native_av_latent", "video_mask"},
        }.get(variant)
        if expected_inputs is not None and set(inputs) != expected_inputs:
            errors.append(f"{path}: refinement inputs do not match {variant}")
        if variant == "masked":
            errors.extend(_validate_video_mask_bindings(bindings.get("video_mask"), path))
            if isinstance(bindings.get("video_mask"), dict) and bindings["video_mask"].get(
                "combine"
            ) != "multiply":
                errors.append(f"{path}: masked refinement must multiply its video mask")
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
    elif operation == "densify.temporal":
        source_frames = bindings.get("source_frame_count")
        factor = bindings.get("factor")
        if not is_h3_frame_count(source_frames):
            errors.append(f"{path}: temporal densification source must use a legal H3 length")
        if not isinstance(factor, int) or isinstance(factor, bool) or factor not in {2, 3, 4}:
            errors.append(f"{path}: temporal densification factor must be 2, 3, or 4")
        if is_h3_frame_count(source_frames) and isinstance(factor, int):
            delivery = (source_frames - 1) * factor + 1
            target = ceil_h3_frame_count(delivery)
            if bindings.get("delivery_frame_count") != delivery:
                errors.append(f"{path}: delivery_frame_count does not match native token dilation")
            if bindings.get("h3_target_frame_count") != target:
                errors.append(f"{path}: H3 target must be the legal ceiling of delivery frames")
            if bindings.get("delivery_fps") != 24 * factor:
                errors.append(f"{path}: delivery_fps must equal 24*factor")
            if not 124 <= target <= 362:
                errors.append(f"{path}: first densification baseline must stay in H3's trained range")
        if bindings.get("anchor_denoise") != 0.0 or bindings.get("gap_denoise") != 1.0:
            errors.append(f"{path}: first densification baseline must preserve anchors and fully generate gaps")
        if bindings.get("audio_denoise") != 1.0:
            errors.append(f"{path}: structural audio must be regenerated for the joint target state")
        if set(inputs) != {"source_native_av_latent"}:
            errors.append(f"{path}: temporal densification requires one native AV source")
    elif operation == "regenerate.spatial":
        source_resolution = bindings.get("source_resolution")
        target_resolution = bindings.get("target_resolution")
        valid_resolutions = (
            isinstance(source_resolution, list)
            and isinstance(target_resolution, list)
            and len(source_resolution) == len(target_resolution) == 2
            and all(isinstance(item, int) and item > 0 for item in source_resolution + target_resolution)
            and all(item % 32 == 0 for item in target_resolution)
            and all(target >= source for target, source in zip(target_resolution, source_resolution))
        )
        if not valid_resolutions:
            errors.append(f"{path}: spatial regeneration resolutions must enlarge on a 32-pixel target grid")
        if not is_h3_frame_count(bindings.get("target_frames")):
            errors.append(f"{path}: spatial regeneration must preserve a legal H3 duration")
        values = bindings.get("characterization_values")
        if (
            not isinstance(values, list)
            or not values
            or values != sorted(set(values))
            or any(not isinstance(value, (int, float)) or not 0 < value <= 1 for value in values)
        ):
            errors.append(f"{path}: spatial denoise ladder must be unique, ordered, and inside (0,1]")
        if bindings.get("video_denoise") is not None:
            errors.append(f"{path}: spatial denoise must remain unbound before characterization")
        if bindings.get("audio_denoise") != 0.0:
            errors.append(f"{path}: spatial regeneration baseline must pin structural audio")
        if set(inputs) != {"source_native_av_latent"}:
            errors.append(f"{path}: spatial regeneration requires one native AV source")
        if variant == "latent-second-pass" and bindings.get("resize_method") != "bicubic":
            errors.append(f"{path}: latent baseline must start with bicubic spatial resize")
        if variant in {"pixel-vae-second-pass", "tiled-pixel-vae"} and bindings.get(
            "pixel_resize_method"
        ) != "lanczos":
            errors.append(f"{path}: pixel/VAE baseline must use the locked deterministic resize")
        if variant == "tiled-pixel-vae":
            tile = bindings.get("tile_resolution")
            overlap = bindings.get("tile_overlap")
            if (
                not isinstance(tile, list)
                or len(tile) != 2
                or any(not isinstance(item, int) or item <= 0 or item % 32 for item in tile)
                or not isinstance(overlap, int)
                or overlap <= 0
                or overlap >= min(tile)
            ):
                errors.append(f"{path}: tiled regeneration needs aligned tiles and bounded overlap")
            if bindings.get("fusion_curve") != "smootherstep":
                errors.append(f"{path}: tiled baseline must use smootherstep overlap fusion")
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


def _validate_video_mask_bindings(value: Any, path: Path) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path}: spatial native operation requires a video_mask object"]
    required = {
        "cardinality",
        "inside_strength",
        "outside_strength",
        "audio_strength",
        "combine",
    }
    if set(value) != required:
        return [f"{path}: video_mask fields are incomplete or unexpected"]
    errors: list[str] = []
    if value["cardinality"] not in {
        "static",
        "per-selected-frame",
        "static-or-per-selected-frame",
    }:
        errors.append(f"{path}: invalid video-mask cardinality")
    for name in ("inside_strength", "outside_strength", "audio_strength"):
        strength = value[name]
        if not isinstance(strength, (int, float)) or not 0 <= strength <= 1:
            errors.append(f"{path}: video-mask {name} must lie in [0,1]")
    if value["combine"] not in {"replace", "maximum", "minimum", "multiply"}:
        errors.append(f"{path}: invalid video-mask combine mode")
    return errors


def _is_aligned_resolution(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) and item >= 32 and item % 32 == 0 for item in value)
    )


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
        if entry["state"] not in {"offline-ready", "schema-validated-draft"}:
            errors.append(f"{path}: invalid materialization lifecycle state")
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


def _unique_strings(value: Any, path: Path, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        return [f"{path}: {label} must be a list of non-empty strings"]
    if len(value) != len(set(value)):
        return [f"{path}: {label} must not contain duplicates"]
    return []


def validate_runtime_requirements(value: Any, path: Path) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "comfy.runtime-requirements/1":
        return [f"{path}: invalid runtime requirements"]
    required = {
        "schema", "id", "required_endpoints", "required_node_types", "node_type_groups",
        "required_models", "hardware", "require_queue_idle", "manual_checks",
    }
    if set(value) != required:
        return [f"{path}: runtime requirements fields are incomplete or unexpected"]
    errors: list[str] = []
    if not isinstance(value.get("id"), str) or not value["id"]:
        errors.append(f"{path}: runtime requirements id is required")
    for label in ("required_endpoints", "required_node_types", "required_models", "manual_checks"):
        errors.extend(_unique_strings(value.get(label), path, label))
    groups = value.get("node_type_groups")
    if not isinstance(groups, list):
        errors.append(f"{path}: node_type_groups must be a list")
    else:
        group_ids: set[str] = set()
        for group in groups:
            if not isinstance(group, dict) or set(group) != {"id", "any_of"}:
                errors.append(f"{path}: malformed node type group")
                continue
            group_id = group.get("id")
            if not isinstance(group_id, str) or not group_id or group_id in group_ids:
                errors.append(f"{path}: node type group ids must be unique")
            else:
                group_ids.add(group_id)
            errors.extend(_unique_strings(group.get("any_of"), path, f"node group {group_id!r}"))
            if group.get("any_of") == []:
                errors.append(f"{path}: node type groups cannot be empty")
    hardware = value.get("hardware")
    if not isinstance(hardware, dict) or set(hardware) != {
        "minimum_total_ram_bytes", "minimum_total_vram_bytes", "device_name_contains"
    }:
        errors.append(f"{path}: invalid hardware requirements")
    else:
        for name in ("minimum_total_ram_bytes", "minimum_total_vram_bytes"):
            amount = hardware[name]
            if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
                errors.append(f"{path}: {name} must be a non-negative integer")
        if not isinstance(hardware["device_name_contains"], str):
            errors.append(f"{path}: device_name_contains must be a string")
    if not isinstance(value.get("require_queue_idle"), bool):
        errors.append(f"{path}: require_queue_idle must be boolean")
    return errors


def validate_runtime_requirements_catalog(value: Any, path: Path, root: Path) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.runtime-requirements-catalog/1":
        return [f"{path}: invalid runtime requirements catalog"]
    profiles = value.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        return [f"{path}: runtime requirements catalog needs profiles"]
    errors: list[str] = []
    ids: set[str] = set()
    loaded: dict[str, dict[str, Any]] = {}
    paths: set[Path] = set()
    for entry in profiles:
        if not isinstance(entry, dict) or set(entry) != {"id", "path", "purpose"}:
            errors.append(f"{path}: malformed runtime requirements entry {entry!r}")
            continue
        profile_id = entry["id"]
        if not isinstance(profile_id, str) or not profile_id or profile_id in ids:
            errors.append(f"{path}: duplicate or invalid runtime profile id {profile_id!r}")
        ids.add(profile_id)
        if not isinstance(entry["purpose"], str) or not entry["purpose"]:
            errors.append(f"{path}: runtime profile purpose is required")
        profile_path, path_errors = _safe_project_path(
            entry["path"], path, root, ("runtime", "requirements")
        )
        errors.extend(path_errors)
        if profile_path is None:
            continue
        try:
            profile = load_json(profile_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{profile_path}: invalid JSON: {exc}")
            continue
        paths.add(profile_path.resolve())
        errors.extend(validate_runtime_requirements(profile, profile_path))
        loaded[profile_id] = profile
    expected_paths = {item.resolve() for item in (root / "runtime" / "requirements").glob("*.json")}
    if paths != expected_paths:
        errors.append(f"{path}: runtime requirements catalog and directory differ")
    expected_profiles = {
        "h3-core",
        "h3-full",
    }
    if set(loaded) != expected_profiles:
        errors.append(f"{path}: runtime profile set is incomplete")
        return errors
    core = loaded["h3-core"]
    full = loaded["h3-full"]
    for field in ("required_endpoints", "required_node_types", "required_models"):
        if not set(core.get(field, [])).issubset(set(full.get(field, []))):
            errors.append(f"{path}: h3-full must include every h3-core {field}")
    cauce_nodes = {name for name in core.get("required_node_types", []) if name.startswith("Cauce")}
    if len(cauce_nodes) != 24:
        errors.append(f"{path}: h3-core must require all 24 locked CAUCE nodes")
    return errors


def validate_live_gate(
    value: Any,
    path: Path,
    root: Path,
    materialization_catalog: dict[str, Any],
    cauce_commit: str,
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.live-materialization-gate/1":
        return [f"{path}: invalid live materialization gate"]
    if set(value) != {"schema", "source_locks", "runtime_profiles", "workspace_gate", "stop_conditions", "phases"}:
        return [f"{path}: live gate fields are incomplete or unexpected"]
    errors: list[str] = []
    source_locks = value.get("source_locks")
    if not isinstance(source_locks, dict) or set(source_locks) != {
        "cauce_commit", "runtime_commit", "workspace_commit", "repository_control_commit"
    }:
        errors.append(f"{path}: live gate source locks are incomplete")
    else:
        if source_locks["cauce_commit"] != cauce_commit:
            errors.append(f"{path}: live gate CAUCE commit does not match operation lock")
        for name in ("runtime_commit", "workspace_commit", "repository_control_commit"):
            if not isinstance(source_locks[name], str) or not GIT_SHA.fullmatch(source_locks[name]):
                errors.append(f"{path}: {name} must be a full Git SHA")
    runtime_profiles = value.get("runtime_profiles")
    expected_runtime_profiles = {
        "core": "runtime/requirements/h3-core.json",
        "full": "runtime/requirements/h3-full.json",
    }
    if not isinstance(runtime_profiles, dict) or set(runtime_profiles) != set(
        expected_runtime_profiles
    ):
        errors.append(f"{path}: live gate runtime profile set is incomplete")
    else:
        for name, expected in expected_runtime_profiles.items():
            if runtime_profiles.get(name) != expected:
                errors.append(f"{path}: {name} runtime profile path is not canonical")
    workspace = value.get("workspace_gate")
    if workspace != {
        "required_diagnostic_schema": "comfy.workspace-diagnostic/1",
        "required_export_schema": "comfy.workspace-export/2",
        "required_workspace_control_version": "0.4.2",
        "required_methods": [
            "inventory",
            "planOpenExact",
            "openExact",
            "planCloseOwned",
            "closeExact",
            "loadUiGraph",
            "loadApiGraph",
            "exportActive",
        ],
        "required_ready": True,
        "maximum_active_agent_graphs": 1,
    }:
        errors.append(f"{path}: workspace gate must require the locked browser contract")
    errors.extend(_unique_strings(value.get("stop_conditions"), path, "stop_conditions"))
    phases = value.get("phases")
    if not isinstance(phases, list) or not phases:
        return errors + [f"{path}: live gate requires phases"]
    phase_ids: set[str] = set()
    ordered_keys: list[str] = []
    expected_phase_profiles = {
        "official-keyframed-baselines": "core",
        "official-reference-and-guide-baselines": "full",
        "native-state-and-assembly-baselines": "full",
        "dependent-variants": "full",
        "native-masked-editing-and-outpaint": "full",
        "bounded-refinement-characterization": "full",
        "native-temporal-densification": "full",
        "native-spatial-regeneration": "full",
    }
    for phase in phases:
        if not isinstance(phase, dict) or set(phase) != {"id", "runtime_profile", "topology_keys"}:
            errors.append(f"{path}: malformed live gate phase {phase!r}")
            continue
        phase_id = phase["id"]
        if not isinstance(phase_id, str) or not phase_id or phase_id in phase_ids:
            errors.append(f"{path}: duplicate or invalid phase id {phase_id!r}")
        phase_ids.add(phase_id)
        if phase["runtime_profile"] not in set(expected_runtime_profiles):
            errors.append(f"{path}: invalid runtime profile in phase {phase_id!r}")
        if expected_phase_profiles.get(phase_id) != phase["runtime_profile"]:
            errors.append(f"{path}: phase {phase_id!r} has the wrong runtime profile")
        errors.extend(_unique_strings(phase["topology_keys"], path, f"phase {phase_id!r} topology_keys"))
        ordered_keys.extend(phase["topology_keys"])
    expected_keys = [entry["topology_key"] for entry in materialization_catalog.get("plans", [])]
    if len(ordered_keys) != len(set(ordered_keys)):
        errors.append(f"{path}: topology keys may occur only once across live phases")
    if set(ordered_keys) != set(expected_keys):
        errors.append(f"{path}: live phases must cover every materialization topology exactly once")
    if phase_ids != set(expected_phase_profiles):
        errors.append(f"{path}: live gate must use the eight canonical evidence phases")
    return errors


def validate_acceptance_catalog(
    value: Any,
    path: Path,
    registry: dict[str, dict[str, Any]],
    materialization_catalog: dict[str, Any],
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.acceptance-catalog/1":
        return [f"{path}: invalid acceptance catalog"]
    profiles = value.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        return [f"{path}: acceptance catalog needs profiles"]
    errors: list[str] = []
    operations: set[str] = set()
    topology_keys: set[str] = set()
    for profile in profiles:
        required = {
            "operation", "operation_version", "variants", "technical_checks",
            "visual_checks", "promotion",
        }
        if not isinstance(profile, dict) or set(profile) != required:
            errors.append(f"{path}: malformed acceptance profile {profile!r}")
            continue
        operation = profile["operation"]
        if operation in operations:
            errors.append(f"{path}: duplicate acceptance operation {operation!r}")
        operations.add(operation)
        errors.extend(
            _validate_operation_reference(
                {"operation": operation, "operation_version": profile["operation_version"]},
                path,
                registry,
                require_hash=False,
            )
        )
        errors.extend(_unique_strings(profile["variants"], path, f"{operation} variants"))
        for variant in profile["variants"]:
            topology_keys.add(f"{operation}@{variant}")
        for label in ("technical_checks", "visual_checks"):
            checks = profile[label]
            if not isinstance(checks, list) or not checks:
                errors.append(f"{path}: {operation} needs {label}")
                continue
            ids: set[str] = set()
            for check in checks:
                if not isinstance(check, dict) or set(check) != {"id", "description"}:
                    errors.append(f"{path}: malformed {label} entry for {operation}")
                    continue
                if not isinstance(check["id"], str) or not check["id"] or check["id"] in ids:
                    errors.append(f"{path}: duplicate or invalid {label} id for {operation}")
                ids.add(check["id"])
                if not isinstance(check["description"], str) or not check["description"]:
                    errors.append(f"{path}: {label} descriptions are required")
        promotion = profile["promotion"]
        if not isinstance(promotion, dict) or set(promotion) != {
            "minimum_successful_runs", "require_all_technical_checks", "require_explicit_visual_verdict"
        }:
            errors.append(f"{path}: malformed promotion rule for {operation}")
        elif (
            not isinstance(promotion["minimum_successful_runs"], int)
            or promotion["minimum_successful_runs"] < 1
            or promotion["require_all_technical_checks"] is not True
            or promotion["require_explicit_visual_verdict"] is not True
        ):
            errors.append(f"{path}: promotion rules must fail closed for {operation}")
    expected_operations = set(registry)
    if operations != expected_operations:
        errors.append(f"{path}: acceptance profiles must cover every locked operation")
    expected_keys = {entry["topology_key"] for entry in materialization_catalog.get("plans", [])}
    if topology_keys != expected_keys:
        errors.append(f"{path}: acceptance variants must cover every materialization topology")
    return errors


def validate_visual_assessment(
    value: Any,
    path: Path,
    registry: dict[str, dict[str, Any]],
    invocation_ids: set[str],
    acceptance_profiles: dict[str, dict[str, Any]],
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.visual-assessment/1":
        return [f"{path}: invalid visual assessment"]
    required = {
        "schema", "id", "invocation", "operation", "operation_version", "variant",
        "run_receipt", "artifact", "reviewer", "reviewed_at", "technical_checks",
        "visual_checks", "verdict", "notes",
    }
    if set(value) != required:
        return [f"{path}: visual assessment fields are incomplete or unexpected"]
    errors = _validate_operation_reference(value, path, registry, require_hash=False)
    if not isinstance(value.get("id"), str) or not value["id"]:
        errors.append(f"{path}: assessment id is required")
    if value.get("invocation") not in invocation_ids:
        errors.append(f"{path}: assessment references an unknown invocation")
    topology_key = f"{value.get('operation')}@{value.get('variant')}"
    profile = acceptance_profiles.get(topology_key)
    if profile is None:
        errors.append(f"{path}: assessment has no acceptance profile for {topology_key}")
        return errors
    for field in ("run_receipt", "reviewer", "reviewed_at"):
        if not isinstance(value.get(field), str) or not value[field]:
            errors.append(f"{path}: {field} is required")
    artifact = value.get("artifact")
    if (
        not isinstance(artifact, dict)
        or set(artifact) != {"filename", "subfolder", "type"}
        or not isinstance(artifact.get("filename"), str)
        or not artifact.get("filename")
        or not isinstance(artifact.get("subfolder"), str)
        or artifact.get("type") not in {"output", "temp"}
    ):
        errors.append(f"{path}: artifact identity is invalid")

    check_results: dict[str, dict[str, str]] = {}
    for label, allowed in (
        ("technical_checks", {"pass", "fail"}),
        ("visual_checks", {"pass", "fail", "not-applicable"}),
    ):
        checks = value.get(label)
        if not isinstance(checks, list) or not checks:
            errors.append(f"{path}: {label} are required")
            continue
        results: dict[str, str] = {}
        for check in checks:
            if not isinstance(check, dict) or set(check) != {"id", "result", "notes"}:
                errors.append(f"{path}: malformed {label} result")
                continue
            check_id = check.get("id")
            if not isinstance(check_id, str) or not check_id or check_id in results:
                errors.append(f"{path}: duplicate or invalid {label} id")
                continue
            if check.get("result") not in allowed or not isinstance(check.get("notes"), str):
                errors.append(f"{path}: invalid {label} result for {check_id!r}")
            results[check_id] = check.get("result")
        expected_ids = {check["id"] for check in profile[label]}
        if set(results) != expected_ids:
            errors.append(f"{path}: {label} must match the acceptance profile exactly")
        check_results[label] = results

    verdict = value.get("verdict")
    if verdict not in {"visually-accepted", "rejected", "mixed"}:
        errors.append(f"{path}: invalid visual verdict")
    technical_values = check_results.get("technical_checks", {}).values()
    visual_values = check_results.get("visual_checks", {}).values()
    if verdict == "visually-accepted" and (
        any(result != "pass" for result in technical_values)
        or any(result != "pass" for result in visual_values)
    ):
        errors.append(f"{path}: visually-accepted requires every check to pass")
    if verdict == "rejected" and not any(result == "fail" for result in visual_values):
        errors.append(f"{path}: rejected requires at least one failed visual check")
    if not isinstance(value.get("notes"), str):
        errors.append(f"{path}: notes must be a string")
    return errors


def validate_visual_assessment_catalog(
    value: Any,
    path: Path,
    root: Path,
    registry: dict[str, dict[str, Any]],
    invocation_ids: set[str],
    acceptance_catalog: dict[str, Any],
) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.visual-assessment-catalog/1":
        return [f"{path}: invalid visual assessment catalog"]
    entries = value.get("assessments")
    if not isinstance(entries, list):
        return [f"{path}: assessments must be a list"]
    profiles = {
        f"{profile['operation']}@{variant}": profile
        for profile in acceptance_catalog.get("profiles", [])
        for variant in profile.get("variants", [])
    }
    errors: list[str] = []
    ids: set[str] = set()
    paths: set[Path] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"id", "path"}:
            errors.append(f"{path}: malformed assessment catalog entry {entry!r}")
            continue
        if not isinstance(entry["id"], str) or not entry["id"] or entry["id"] in ids:
            errors.append(f"{path}: duplicate or invalid assessment id {entry['id']!r}")
        ids.add(entry["id"])
        record_path, path_errors = _safe_project_path(
            entry["path"], path, root, ("assessments", "records")
        )
        errors.extend(path_errors)
        if record_path is None:
            continue
        try:
            record = load_json(record_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{record_path}: invalid JSON: {exc}")
            continue
        paths.add(record_path.resolve())
        errors.extend(
            validate_visual_assessment(
                record, record_path, registry, invocation_ids, profiles
            )
        )
        if record.get("id") != entry["id"]:
            errors.append(f"{record_path}: assessment id does not match catalog")
    records_dir = root / "assessments" / "records"
    expected_paths = {item.resolve() for item in records_dir.glob("*.json")}
    if paths != expected_paths:
        errors.append(f"{path}: assessment catalog and record directory differ")
    return errors


def validate_storage_policy(value: Any, path: Path) -> list[str]:
    if not isinstance(value, dict) or value.get("schema") != "inside-valdivia.storage-policy/1":
        return [f"{path}: invalid storage policy"]
    required = {
        "schema", "minimum_free_bytes", "warning_free_bytes",
        "allow_automatic_model_deletion", "allow_unindexed_output_deletion",
        "native_checkpoint_policy", "accepted_output_policy", "temporary_output_policy",
        "preflight",
    }
    if set(value) != required:
        return [f"{path}: storage policy fields are incomplete or unexpected"]
    errors: list[str] = []
    minimum = value["minimum_free_bytes"]
    warning = value["warning_free_bytes"]
    if (
        isinstance(minimum, bool) or not isinstance(minimum, int) or minimum <= 0
        or isinstance(warning, bool) or not isinstance(warning, int) or warning <= minimum
    ):
        errors.append(f"{path}: storage warning must exceed one positive minimum reserve")
    if value["allow_automatic_model_deletion"] is not False:
        errors.append(f"{path}: automatic model deletion must remain disabled")
    if value["allow_unindexed_output_deletion"] is not False:
        errors.append(f"{path}: unindexed output deletion must remain disabled")
    for field in ("native_checkpoint_policy", "accepted_output_policy", "temporary_output_policy"):
        if not isinstance(value[field], str) or not value[field]:
            errors.append(f"{path}: {field} is required")
    errors.extend(_unique_strings(value["preflight"], path, "storage preflight"))
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
    runtime_commit: str | None = None,
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
        elif runtime_commit is not None and locks["runtime_commit"] != runtime_commit:
            errors.append(f"{path}: rolling Runtime commit does not match live gate")
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
    runtime_commit: str | None = None,
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
        errors.extend(
            validate_rolling_plan(
                plan, plan_path, registry, root, cauce_commit, runtime_commit
            )
        )
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
    training_path = root / "training" / "catalog.json"
    errors.extend(validate_training_catalog(load_json(training_path), training_path, root))
    materialization_path = root / "materialization" / "catalog.json"
    materialization_catalog = load_json(materialization_path)
    errors.extend(
        validate_materialization_catalog(
            materialization_catalog, materialization_path, registry, root
        )
    )
    archetype_lock_path = root / "archetypes.lock.json"
    errors.extend(
        validate_archetype_lock(
            load_json(archetype_lock_path),
            archetype_lock_path,
            materialization_catalog,
            lock.get("source", {}).get("commit"),
        )
    )
    runtime_requirements_path = root / "runtime" / "catalog.json"
    errors.extend(
        validate_runtime_requirements_catalog(
            load_json(runtime_requirements_path), runtime_requirements_path, root
        )
    )
    live_gate_path = root / "materialization" / "live-gate.json"
    live_gate = load_json(live_gate_path)
    errors.extend(
        validate_live_gate(
            live_gate,
            live_gate_path,
            root,
            materialization_catalog,
            lock.get("source", {}).get("commit"),
        )
    )
    compatibility_path = root / "runtime" / "compatibility-lock.json"
    errors.extend(
        validate_compatibility_lock(
            load_json(compatibility_path),
            compatibility_path,
            cauce_commit=lock.get("source", {}).get("commit"),
            runtime_commit=live_gate.get("source_locks", {}).get("runtime_commit"),
            workspace_commit=live_gate.get("source_locks", {}).get("workspace_commit"),
            repository_control_commit=live_gate.get("source_locks", {}).get(
                "repository_control_commit"
            ),
        )
    )
    acceptance_path = root / "acceptance" / "catalog.json"
    acceptance_catalog = load_json(acceptance_path)
    errors.extend(
        validate_acceptance_catalog(
            acceptance_catalog, acceptance_path, registry, materialization_catalog
        )
    )
    assessment_path = root / "assessments" / "catalog.json"
    errors.extend(
        validate_visual_assessment_catalog(
            load_json(assessment_path),
            assessment_path,
            root,
            registry,
            invocation_ids,
            acceptance_catalog,
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
            live_gate.get("source_locks", {}).get("runtime_commit"),
        )
    )
    media_path = root / "media" / "catalog.json"
    errors.extend(validate_media_catalog(load_json(media_path), media_path))
    storage_path = root / "storage" / "policy.json"
    errors.extend(validate_storage_policy(load_json(storage_path), storage_path))
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
        "validated: operation/archetype/compatibility locks, project invocations, "
        "materialization plans, runtime gates, acceptance evidence, storage, rolling "
        "plans, media, experiments, H3 training recipes, fixtures, and schemas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
