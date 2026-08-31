#!/usr/bin/env python3
"""Emit a machine-readable, non-promotional production readiness summary."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate import load_json, validate_repository  # noqa: E402


def _load_directory(directory: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for path in sorted((ROOT / directory).glob("*.json")):
        value = load_json(path)
        if isinstance(value, dict):
            values.append(value)
    return values


def build_readiness_report(root: Path = ROOT) -> dict[str, Any]:
    errors = validate_repository(root)
    materialization = load_json(root / "materialization" / "catalog.json")
    plans = [
        load_json(root / entry["plan"])
        for entry in materialization.get("plans", [])
    ]
    experiments = load_json(root / "experiments" / "catalog.json").get("experiments", [])
    assessments = load_json(root / "assessments" / "catalog.json").get("assessments", [])
    media = load_json(root / "media" / "catalog.json").get("media", [])
    invocations = _load_directory("invocations")
    live_gate = load_json(root / "materialization" / "live-gate.json")
    archetypes = load_json(root / "archetypes.lock.json").get("archetypes", [])
    compatibility = load_json(root / "runtime" / "compatibility-lock.json")
    runtime_manifests = _load_directory("runtime/manifests")
    runtime_evaluations = _load_directory("runtime/evaluations")
    latest_runtime_manifest = max(
        runtime_manifests,
        key=lambda value: str(value.get("captured_at", "")),
        default=None,
    )
    ready_runtime_profiles = sorted(
        value.get("requirements_id")
        for value in runtime_evaluations
        if value.get("schema") == "comfy.runtime-readiness/1"
        and value.get("ready") is True
        and value.get("runtime_manifest_hash")
        == (latest_runtime_manifest or {}).get("manifest_hash")
    )
    materialized = [
        plan
        for plan in plans
        if plan.get("outputs", {}).get("ui_graph")
        and plan.get("outputs", {}).get("api_template")
    ]
    schema_validated = [
        plan for plan in plans if plan.get("validation", {}).get("schema_status") == "validated"
    ]
    required_runtime_profiles = {
        "inside-valdivia-h3-core",
        "inside-valdivia-h3-full",
    }
    runtime_ready = required_runtime_profiles <= set(ready_runtime_profiles)
    if latest_runtime_manifest is None:
        next_gate = "capture-content-addressed-runtime-manifest"
    elif not runtime_ready:
        next_gate = "resolve-runtime-requirements"
    elif not materialized:
        next_gate = "materialize-generate-keyframed-text-only"
    elif not schema_validated:
        next_gate = "schema-validate-first-paired-workflow"
    elif not assessments:
        next_gate = "execute-and-visually-assess-first-workflow"
    else:
        next_gate = "promote-only-accepted-workflows"
    return {
        "schema": "inside-valdivia.readiness-report/1",
        "offline_valid": not errors,
        "validation_errors": errors,
        "source_locks": live_gate.get("source_locks"),
        "counts": {
            "materialization_plans": len(plans),
            "graph_archetypes": len(archetypes),
            "binding_profiles": len(plans),
            "locked_control_components": len(compatibility.get("components", {})),
            "paired_workflows": len(materialized),
            "schema_validated_workflows": len(schema_validated),
            "invocations": len(invocations),
            "media_records": len(media),
            "experiment_definitions": len(experiments),
            "visual_assessments": len(assessments),
            "live_gate_phases": len(live_gate.get("phases", [])),
            "runtime_manifests": len(runtime_manifests),
            "runtime_readiness_evaluations": len(runtime_evaluations),
        },
        "evidence": {
            "offline_ready_topologies": sum(plan.get("status") == "offline-ready" for plan in plans),
            "executed_invocations": sum(
                invocation.get("status") in {"executes", "visually-accepted", "rejected"}
                for invocation in invocations
            ),
            "visually_decided_invocations": sum(
                invocation.get("status") in {"visually-accepted", "rejected"}
                for invocation in invocations
            ),
            "latest_runtime_manifest_hash": (latest_runtime_manifest or {}).get(
                "manifest_hash"
            ),
            "ready_runtime_profiles": ready_runtime_profiles,
        },
        "next_gate": next_gate,
        "production_ready": bool(
            not errors
            and runtime_ready
            and materialized
            and schema_validated
            and assessments
        ),
    }


def main() -> int:
    report = build_readiness_report()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["offline_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
