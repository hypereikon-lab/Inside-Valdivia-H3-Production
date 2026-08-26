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
    materialized = [
        plan
        for plan in plans
        if plan.get("outputs", {}).get("ui_graph")
        and plan.get("outputs", {}).get("api_template")
    ]
    schema_validated = [
        plan for plan in plans if plan.get("validation", {}).get("schema_status") == "validated"
    ]
    return {
        "schema": "inside-valdivia.readiness-report/1",
        "offline_valid": not errors,
        "validation_errors": errors,
        "source_locks": live_gate.get("source_locks"),
        "counts": {
            "materialization_plans": len(plans),
            "paired_workflows": len(materialized),
            "schema_validated_workflows": len(schema_validated),
            "invocations": len(invocations),
            "media_records": len(media),
            "experiment_definitions": len(experiments),
            "visual_assessments": len(assessments),
            "live_gate_phases": len(live_gate.get("phases", [])),
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
        },
        "next_gate": "capture-runtime-manifest-and-evaluate-h3-core",
        "production_ready": bool(
            not errors
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
