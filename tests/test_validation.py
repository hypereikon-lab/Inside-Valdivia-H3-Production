import copy
import unittest

from tools.readiness import build_readiness_report
from tools.validate import (
    ROOT,
    is_h3_frame_count,
    is_h3_visual_boundary,
    load_json,
    validate_acceptance_catalog,
    validate_archetype_lock,
    validate_compatibility_lock,
    validate_invocation,
    validate_live_gate,
    validate_materialization_catalog,
    validate_materialization_plan,
    validate_media_catalog,
    validate_operation_history_lock,
    validate_operation_lock,
    validate_repository,
    validate_rolling_catalog,
    validate_rolling_plan,
    validate_runtime_requirements,
    validate_runtime_requirements_catalog,
    validate_segment,
    validate_storage_policy,
    validate_training_catalog,
    validate_visual_assessment,
    validate_visual_assessment_catalog,
)


class RepositoryValidationTests(unittest.TestCase):
    def test_repository_is_consistent(self):
        self.assertEqual(validate_repository(), [])

    def test_h3_frame_grid(self):
        self.assertTrue(is_h3_frame_count(5))
        self.assertTrue(is_h3_frame_count(124))
        self.assertTrue(is_h3_frame_count(362))
        self.assertFalse(is_h3_frame_count(123))
        self.assertTrue(is_h3_visual_boundary(39))
        self.assertTrue(is_h3_visual_boundary(90))
        self.assertFalse(is_h3_visual_boundary(40))

    def test_operation_lock_is_semantic_and_content_addressed(self):
        lock_path = ROOT / "operations.lock.json"
        errors, registry = validate_operation_lock(load_json(lock_path), lock_path)
        self.assertEqual(errors, [])
        self.assertEqual(
            set(registry),
            {
                "complete.native_av",
                "continue.native_av",
                "edit.masked_video",
                "frames.assemble",
                "generate.from_references",
                "generate.keyframed",
                "generate.with_control",
                "generate.with_guides",
                "densify.temporal",
                "reframe.outpaint_video",
                "refine.video",
                "regenerate.spatial",
                "rollback.native_av",
            },
        )
        self.assertTrue(all(not operation_id.startswith("W") for operation_id in registry))

    def test_invocation_must_match_locked_version_and_hash(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        invocation_path = ROOT / "invocations" / "example.json"
        invocation = load_json(invocation_path)
        self.assertEqual(validate_invocation(invocation, invocation_path, registry), [])
        wrong = copy.deepcopy(invocation)
        wrong["operation_contract_hash"] = "0" * 64
        self.assertIn(
            f"{invocation_path}: operation contract hash does not match lock",
            validate_invocation(wrong, invocation_path, registry),
        )

    def test_executed_historical_invocation_remains_immutable(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        history_path = ROOT / "operations.history.lock.json"
        history_errors, history = validate_operation_history_lock(
            load_json(history_path),
            history_path,
            registry,
            load_json(lock_path)["source"]["commit"],
        )
        self.assertEqual(history_errors, [])
        invocation_path = (
            ROOT / "invocations" / "2026-08-31-07-spatial-regenerate-1792x1024.json"
        )
        invocation = load_json(invocation_path)
        self.assertLess(
            invocation["operation_version"],
            registry[invocation["operation"]]["version"],
        )
        self.assertEqual(
            validate_invocation(invocation, invocation_path, registry, history),
            [],
        )
        tampered = copy.deepcopy(invocation)
        tampered["operation_contract_hash"] = "0" * 64
        self.assertIn(
            f"{invocation_path}: historical operation contract hash does not match archive",
            validate_invocation(tampered, invocation_path, registry, history),
        )

    def test_segment_references_invocation_output(self):
        segment_path = ROOT / "segments" / "example.json"
        segment = load_json(segment_path)
        invocation = load_json(ROOT / "invocations" / "example.json")
        self.assertEqual(validate_segment(segment, segment_path, {invocation["id"]}), [])

    def test_experiments_reference_named_operations(self):
        catalog = load_json(ROOT / "experiments" / "catalog.json")
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        for experiment in catalog["experiments"]:
            self.assertTrue(experiment["operations"])
            for operation in experiment["operations"]:
                self.assertIn("id", operation)
                self.assertIn("version", operation)
                self.assertLessEqual(
                    operation["version"], registry[operation["id"]]["version"]
                )

    def test_training_recipes_are_explicitly_gated(self):
        catalog_path = ROOT / "training" / "catalog.json"
        catalog = load_json(catalog_path)
        self.assertEqual(validate_training_catalog(catalog, catalog_path, ROOT), [])
        self.assertEqual(
            [recipe["id"] for recipe in catalog["recipes"]],
            ["h3-spatial-regeneration-lora", "h3-temporal-completion-lora"],
        )
        self.assertEqual(
            [recipe["status"] for recipe in catalog["recipes"]],
            ["lab-gated", "requires-task-adapter"],
        )
        for entry in catalog["recipes"]:
            recipe = load_json(ROOT / entry["path"])
            self.assertFalse(recipe["model"]["full_finetune"])
            self.assertFalse(recipe["hardware_gate"]["full_finetune_allowed"])
            self.assertEqual(recipe["adapter"]["method"], "LoRA")

    def test_reference_duration_baseline_stays_on_documented_h3_lengths(self):
        catalog = load_json(ROOT / "experiments" / "catalog.json")
        experiment = next(
            value
            for value in catalog["experiments"]
            if value["id"] == "reference-clip-duration"
        )
        frame_counts = experiment["variable"]["reference_clip_frames"]
        self.assertTrue(frame_counts)
        self.assertTrue(all(is_h3_frame_count(value) for value in frame_counts))
        self.assertTrue(all(2 * 24 <= value <= 15 * 24 for value in frame_counts))

    def test_runtime_operation_reference_matches_lock(self):
        reference = load_json(ROOT / "fixtures" / "operation-ref.json")
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        locked = registry[reference["id"]]
        self.assertEqual(reference["version"], locked["version"])
        self.assertEqual(reference["contract_hash"], locked["contract_hash"])

    def test_materialization_plan_selects_one_variant(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        plan_path = ROOT / "fixtures" / "materialization-plan.json"
        plan = load_json(plan_path)
        self.assertEqual(validate_materialization_plan(plan, plan_path, registry), [])
        self.assertEqual(
            set(plan["outputs"]),
            {
                "ui_graph",
                "api_template",
                "bindings",
                "materialization_manifest",
                "ui_graph_hash",
                "api_template_hash",
                "bindings_hash",
            },
        )
        plan.pop("variant")
        self.assertIn(
            f"{plan_path}: variant must be a non-empty string",
            validate_materialization_plan(plan, plan_path, registry),
        )

    def test_materialization_catalog_uses_exact_canonical_variants(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        catalog_path = ROOT / "materialization" / "catalog.json"
        catalog = load_json(catalog_path)
        self.assertEqual(
            validate_materialization_catalog(catalog, catalog_path, registry, ROOT), []
        )
        self.assertEqual(
            [entry["topology_key"] for entry in catalog["plans"]],
            [
                "generate.keyframed@first-frame",
                "generate.keyframed@first-last",
                "generate.from_references@image-reference-match",
                "generate.from_references@video-reference",
                "generate.with_guides@single-anchor",
                "generate.with_guides@multi-anchor",
                "continue.native_av@keyframe-overlap",
                "complete.native_av@two-sided-infill",
                "frames.assemble@ordered-concatenation",
                "generate.keyframed@last-frame",
                "generate.keyframed@text-only",
                "generate.from_references@image-reference-max",
                "generate.with_guides@guide-clip",
                "continue.native_av@masked-overlap",
                "continue.native_av@masked-overlap-future-guide",
                "complete.native_av@local-replacement",
                "complete.native_av@backward-prefix",
                "complete.native_av@two-source-connection",
                "rollback.native_av@branch-suffix",
                "generate.from_references@video-reference-with-guide",
                "generate.with_guides@first-last-interior",
                "edit.masked_video@static-spatial",
                "edit.masked_video@animated-spatiotemporal",
                "edit.masked_video@local-retake",
                "reframe.outpaint_video@centered",
                "reframe.outpaint_video@offset",
                "refine.video@full-frame",
                "refine.video@masked",
                "densify.temporal@token-inpaint",
                "regenerate.spatial@latent-second-pass",
                "regenerate.spatial@pixel-vae-second-pass",
                "regenerate.spatial@tiled-pixel-vae",
                "generate.with_control@structural-video",
                "generate.with_control@masked-inpaint",
                "regenerate.spatial@learned-latent-second-pass",
            ],
        )
        for entry in catalog["plans"]:
            self.assertEqual(entry["topology_key"], f"{entry['operation']}@{entry['variant']}")

    def test_archetype_lock_resolves_every_binding_profile_once(self):
        path = ROOT / "archetypes.lock.json"
        lock = load_json(path)
        operations = load_json(ROOT / "operations.lock.json")
        materialization = load_json(ROOT / "materialization" / "catalog.json")
        self.assertEqual(
            validate_archetype_lock(
                lock,
                path,
                materialization,
                operations["source"]["commit"],
            ),
            [],
        )
        self.assertEqual(len(lock["archetypes"]), 32)
        covered = [
            key
            for archetype in lock["archetypes"]
            for key in archetype["topology_keys"]
        ]
        self.assertEqual(len(covered), 35)
        references = next(value for value in lock["archetypes"] if value["id"] == "references-image")
        self.assertEqual(len(references["topology_keys"]), 2)

    def test_compatibility_lock_pins_all_control_layers(self):
        path = ROOT / "runtime" / "compatibility-lock.json"
        lock = load_json(path)
        operation_lock = load_json(ROOT / "operations.lock.json")
        live_gate = load_json(ROOT / "materialization" / "live-gate.json")
        self.assertEqual(
            validate_compatibility_lock(
                lock,
                path,
                cauce_commit=operation_lock["source"]["commit"],
                runtime_commit=live_gate["source_locks"]["runtime_commit"],
                workspace_commit=live_gate["source_locks"]["workspace_commit"],
                repository_control_commit=live_gate["source_locks"][
                    "repository_control_commit"
                ],
                model_control_commit=live_gate["source_locks"]["model_control_commit"],
            ),
            [],
        )
        self.assertEqual(lock["platform"]["full_profile"]["minimum_comfyui"], "0.34.0")
        self.assertEqual(
            set(lock["components"]),
            {
                "cauce", "runtime_control", "workspace_control",
                "repository_control", "model_control"
            },
        )
        self.assertEqual(
            lock["components"]["workspace_control"]["distribution"],
            "registry-prepared-unpublished",
        )

    def test_offline_baselines_obey_h3_temporal_rules(self):
        reference = load_json(
            ROOT / "materialization" / "plans" / "04-references-video.json"
        )["bindings"]
        self.assertEqual(reference["reference_fps"], 24)
        self.assertTrue(is_h3_frame_count(reference["reference_frames"]))
        self.assertGreaterEqual(reference["reference_frames"], 2 * 24)

        continuation = load_json(
            ROOT / "materialization" / "plans" / "07-native-continuation.json"
        )["bindings"]
        self.assertEqual(
            continuation["overlap_frames"] + continuation["extension_frames"],
            continuation["window_frames"],
        )
        self.assertTrue(is_h3_frame_count(continuation["overlap_frames"]))
        self.assertEqual(continuation["extension_frames"] % 17, 0)
        self.assertTrue(is_h3_frame_count(continuation["window_frames"]))

    def test_every_plan_has_a_fail_closed_artifact_contract(self):
        catalog = load_json(ROOT / "materialization" / "catalog.json")
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        for entry in catalog["plans"]:
            plan_path = ROOT / entry["plan"]
            plan = load_json(plan_path)
            artifact = plan["bindings"]["artifact"]
            expected_frame_rate = 24
            if plan["operation"] == "densify.temporal":
                expected_frame_rate = plan["bindings"]["delivery_fps"]
            self.assertEqual(artifact["frame_rate"], expected_frame_rate)
            self.assertIsNone(artifact["filename_prefix"])
            self.assertEqual(artifact["format"], "auto")
            self.assertEqual(artifact["codec"], "auto")
            self.assertTrue(artifact["history_resolvable"])
            self.assertEqual(
                artifact["retain_native_state"],
                plan["operation"]
                != "frames.assemble",
            )

            broken = copy.deepcopy(plan)
            broken["bindings"]["artifact"]["frame_rate"] = 30
            self.assertIn(
                f"{plan_path}: materialized artifact frame_rate must be "
                f"{expected_frame_rate} for {plan['operation']}",
                validate_materialization_plan(broken, plan_path, registry),
            )

    def test_h3_native_enhancement_plans_use_no_auxiliary_models(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        cases = [
            "29-densify-temporal-token-inpaint.json",
            "30-regenerate-spatial-latent.json",
            "31-regenerate-spatial-pixel-vae.json",
            "32-regenerate-spatial-tiled.json",
        ]
        for filename in cases:
            plan_path = ROOT / "materialization" / "plans" / filename
            plan = load_json(plan_path)
            self.assertEqual(validate_materialization_plan(plan, plan_path, registry), [])
            files = set(plan["bindings"]["model_files"].values())
            self.assertTrue(all("minimax_h3" in value for value in files))
            self.assertNotIn("model_source", plan["bindings"])

    def test_native_completion_plans_have_exact_token_aligned_ranges(self):
        plans = [
            "08-complete-two-sided-infill.json",
            "16-complete-local-replacement.json",
            "17-complete-backward-prefix.json",
            "18-complete-two-source-connection.json",
        ]
        for name in plans:
            bindings = load_json(ROOT / "materialization" / "plans" / name)["bindings"]
            start = bindings["unknown_start_frame"]
            end = start + bindings["unknown_frame_count"]
            self.assertTrue(is_h3_frame_count(bindings["target_frames"]))
            self.assertTrue(is_h3_visual_boundary(start))
            self.assertTrue(is_h3_visual_boundary(end))
            mask = bindings["mask"]
            self.assertIn(mask["curve"], {"linear", "smoothstep", "smootherstep"})
            for key in (
                "inside_strength_video",
                "outside_strength_video",
                "inside_strength_audio",
                "outside_strength_audio",
            ):
                self.assertGreaterEqual(mask[key], 0)
                self.assertLessEqual(mask[key], 1)

    def test_masked_edit_outpaint_and_refine_plans_are_fail_closed(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)

        edit_path = ROOT / "materialization" / "plans" / "24-edit-masked-local-retake.json"
        edit = load_json(edit_path)
        self.assertEqual(validate_materialization_plan(edit, edit_path, registry), [])
        broken_edit = copy.deepcopy(edit)
        broken_edit["bindings"]["video_mask"]["combine"] = "replace"
        self.assertIn(
            f"{edit_path}: local retake must intersect temporal and video masks",
            validate_materialization_plan(broken_edit, edit_path, registry),
        )

        outpaint_path = ROOT / "materialization" / "plans" / "25-outpaint-centered.json"
        outpaint = load_json(outpaint_path)
        self.assertEqual(validate_materialization_plan(outpaint, outpaint_path, registry), [])
        broken_outpaint = copy.deepcopy(outpaint)
        broken_outpaint["bindings"]["offset_x"] = 0
        self.assertIn(
            f"{outpaint_path}: centered outpaint requires equal margins",
            validate_materialization_plan(broken_outpaint, outpaint_path, registry),
        )

        refine_path = ROOT / "materialization" / "plans" / "27-refine-full-frame.json"
        refine = load_json(refine_path)
        self.assertEqual(validate_materialization_plan(refine, refine_path, registry), [])
        broken_refine = copy.deepcopy(refine)
        broken_refine["bindings"]["video_denoise_strength"] = 0.2
        self.assertIn(
            f"{refine_path}: refinement strength must remain unbound before live characterization",
            validate_materialization_plan(broken_refine, refine_path, registry),
        )
    def test_backward_prefix_preserves_visual_and_audio_phase(self):
        bindings = load_json(
            ROOT / "materialization" / "plans" / "17-complete-backward-prefix.json"
        )["bindings"]
        boundary = bindings["unknown_start_frame"] + bindings["unknown_frame_count"]
        self.assertEqual(bindings["known_right_target_frame"], boundary)
        self.assertEqual(
            bindings["known_right_frames"], bindings["target_frames"] - boundary
        )
        self.assertEqual(boundary * 40 % 24, 0)

    def test_rolling_plan_is_strict_content_addressed_and_non_autowiring(self):
        lock_path = ROOT / "operations.lock.json"
        lock = load_json(lock_path)
        _, registry = validate_operation_lock(lock, lock_path)
        catalog_path = ROOT / "rolling" / "catalog.json"
        catalog = load_json(catalog_path)
        self.assertEqual(
            validate_rolling_catalog(
                catalog, catalog_path, registry, ROOT, lock["source"]["commit"]
            ),
            [],
        )
        plan_path = ROOT / "rolling" / "plans" / "native-continuation-chain.json"
        plan = load_json(plan_path)
        self.assertFalse(plan["execution"]["auto_wire_outputs"])
        self.assertEqual(plan["checkpoint_policy"]["frequency"], "after-each-step")
        self.assertEqual(plan["branch_policy"]["mode"], "new-plan-from-checkpoint")
        self.assertEqual(
            [step["depends_on"] for step in plan["steps"]],
            [None, "seed", "extend-01"],
        )
        live_gate = load_json(ROOT / "materialization" / "live-gate.json")
        self.assertEqual(
            plan["source_locks"]["runtime_commit"],
            live_gate["source_locks"]["runtime_commit"],
        )
        broken = copy.deepcopy(plan)
        broken["steps"][2]["depends_on"] = "seed"
        self.assertIn(
            f"{plan_path}: rolling steps must form one exact serial chain",
            validate_rolling_plan(
                broken, plan_path, registry, ROOT, lock["source"]["commit"]
            ),
        )

    def test_media_catalog_is_empty_until_real_assets_are_hashed(self):
        catalog_path = ROOT / "media" / "catalog.json"
        catalog = load_json(catalog_path)
        self.assertEqual(validate_media_catalog(catalog, catalog_path), [])
        self.assertEqual(catalog["media"], [])

    def test_runtime_profiles_fail_closed_and_full_is_a_core_superset(self):
        catalog_path = ROOT / "runtime" / "catalog.json"
        catalog = load_json(catalog_path)
        self.assertEqual(validate_runtime_requirements_catalog(catalog, catalog_path, ROOT), [])
        core_path = ROOT / "runtime" / "requirements" / "h3-core.json"
        full_path = ROOT / "runtime" / "requirements" / "h3-full.json"
        core = load_json(core_path)
        full = load_json(full_path)
        self.assertEqual(validate_runtime_requirements(core, core_path), [])
        self.assertEqual(validate_runtime_requirements(full, full_path), [])
        self.assertTrue(set(core["required_node_types"]) <= set(full["required_node_types"]))
        self.assertTrue(set(core["required_models"]) <= set(full["required_models"]))
        self.assertEqual(
            len([name for name in core["required_node_types"] if name.startswith("Cauce")]),
            28,
        )
        self.assertIn("CreateVideo", core["required_node_types"])
        self.assertIn("SaveVideo", core["required_node_types"])

        broken = copy.deepcopy(core)
        broken["required_node_types"].append("CauceSaveAVLatent")
        self.assertIn(
            f"{core_path}: required_node_types must not contain duplicates",
            validate_runtime_requirements(broken, core_path),
        )

    def test_live_gate_orders_every_topology_once_without_redefining_catalog_priority(self):
        gate_path = ROOT / "materialization" / "live-gate.json"
        gate = load_json(gate_path)
        catalog = load_json(ROOT / "materialization" / "catalog.json")
        lock = load_json(ROOT / "operations.lock.json")
        self.assertEqual(
            validate_live_gate(gate, gate_path, ROOT, catalog, lock["source"]["commit"]),
            [],
        )
        ordered = [key for phase in gate["phases"] for key in phase["topology_keys"]]
        self.assertEqual(ordered[0], "generate.keyframed@text-only")
        self.assertEqual(len(ordered), 35)
        self.assertEqual(len(set(ordered)), 35)
        self.assertEqual(len(gate["phases"]), 10)
        self.assertEqual(gate["phases"][0]["runtime_profile"], "core")
        self.assertTrue(
            all(
                key.startswith("generate.keyframed@")
                for key in gate["phases"][0]["topology_keys"]
            )
        )
        self.assertEqual(gate["phases"][-2]["runtime_profile"], "control")
        self.assertEqual(gate["phases"][-1]["runtime_profile"], "learned_upscale")

        broken = copy.deepcopy(gate)
        broken["phases"][2]["topology_keys"][0] = ordered[0]
        self.assertIn(
            f"{gate_path}: topology keys may occur only once across live phases",
            validate_live_gate(broken, gate_path, ROOT, catalog, lock["source"]["commit"]),
        )

    def test_acceptance_profiles_cover_all_operations_and_variants(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        materialization = load_json(ROOT / "materialization" / "catalog.json")
        path = ROOT / "acceptance" / "catalog.json"
        catalog = load_json(path)
        self.assertEqual(
            validate_acceptance_catalog(catalog, path, registry, materialization),
            [],
        )
        covered = {
            f"{profile['operation']}@{variant}"
            for profile in catalog["profiles"]
            for variant in profile["variants"]
        }
        self.assertEqual(
            covered,
            {entry["topology_key"] for entry in materialization["plans"]},
        )
        for profile in catalog["profiles"]:
            self.assertTrue(profile["promotion"]["require_all_technical_checks"])
            self.assertTrue(profile["promotion"]["require_explicit_visual_verdict"])

    def test_storage_policy_preserves_reserve_and_disables_broad_deletion(self):
        path = ROOT / "storage" / "policy.json"
        policy = load_json(path)
        self.assertEqual(validate_storage_policy(policy, path), [])
        self.assertGreater(policy["warning_free_bytes"], policy["minimum_free_bytes"])
        self.assertFalse(policy["allow_automatic_model_deletion"])
        self.assertFalse(policy["allow_unindexed_output_deletion"])

    def test_visual_assessments_validate_and_fail_closed(self):
        lock_path = ROOT / "operations.lock.json"
        _, registry = validate_operation_lock(load_json(lock_path), lock_path)
        acceptance = load_json(ROOT / "acceptance" / "catalog.json")
        catalog_path = ROOT / "assessments" / "catalog.json"
        catalog = load_json(catalog_path)
        invocation = load_json(ROOT / "invocations" / "example.json")
        invocation_ids = {
            load_json(path)["id"]
            for path in sorted((ROOT / "invocations").glob("*.json"))
        }
        self.assertEqual(
            validate_visual_assessment_catalog(
                catalog,
                catalog_path,
                ROOT,
                registry,
                invocation_ids,
                acceptance,
            ),
            [],
        )
        self.assertEqual(
            {entry["id"] for entry in catalog["assessments"]},
            {
                "2026-08-31-temporal-densify-2x-rejected",
                "2026-08-31-interior-still-guide-rejected",
                "2026-08-31-temporal-densify-2x-exact-anchors-rejected",
            },
        )

        profile = next(
            item for item in acceptance["profiles"] if item["operation"] == "generate.keyframed"
        )
        profile_by_topology = {
            f"generate.keyframed@{variant}": profile for variant in profile["variants"]
        }
        assessment = {
            "schema": "inside-valdivia.visual-assessment/1",
            "id": "unit-assessment",
            "invocation": invocation["id"],
            "operation": "generate.keyframed",
            "operation_version": registry["generate.keyframed"]["version"],
            "variant": "first-last",
            "run_receipt": "receipts/prompt-1.json",
            "artifact": {"filename": "result.mp4", "subfolder": "unit", "type": "output"},
            "reviewer": "unit-reviewer",
            "reviewed_at": "2026-08-26T12:00:00Z",
            "technical_checks": [
                {"id": check["id"], "result": "pass", "notes": "verified"}
                for check in profile["technical_checks"]
            ],
            "visual_checks": [
                {"id": check["id"], "result": "pass", "notes": "inspected"}
                for check in profile["visual_checks"]
            ],
            "verdict": "visually-accepted",
            "notes": "unit fixture",
        }
        record_path = ROOT / "assessments" / "records" / "unit.json"
        self.assertEqual(
            validate_visual_assessment(
                assessment,
                record_path,
                registry,
                {invocation["id"]},
                profile_by_topology,
            ),
            [],
        )
        assessment["visual_checks"][0]["result"] = "fail"
        self.assertIn(
            f"{record_path}: visually-accepted requires every check to pass",
            validate_visual_assessment(
                assessment,
                record_path,
                registry,
                {invocation["id"]},
                profile_by_topology,
            ),
        )

    def test_readiness_report_does_not_promote_offline_plans(self):
        report = build_readiness_report()
        self.assertTrue(report["offline_valid"])
        self.assertEqual(report["counts"]["materialization_plans"], 35)
        self.assertEqual(report["counts"]["graph_archetypes"], 32)
        self.assertEqual(report["counts"]["binding_profiles"], 35)
        self.assertEqual(report["counts"]["locked_control_components"], 5)
        self.assertEqual(report["counts"]["runtime_manifests"], 1)
        self.assertEqual(report["counts"]["runtime_readiness_evaluations"], 2)
        self.assertEqual(report["counts"]["runtime_smoke_batches"], 1)
        self.assertEqual(report["counts"]["paired_workflows"], 1)
        self.assertEqual(report["counts"]["schema_validated_workflows"], 1)
        self.assertEqual(report["counts"]["visual_assessments"], 3)
        self.assertEqual(report["evidence"]["accepted_visual_assessments"], 0)
        self.assertEqual(report["evidence"]["rejected_visual_assessments"], 3)
        self.assertEqual(report["evidence"]["offline_ready_topologies"], 34)
        self.assertEqual(
            report["evidence"]["latest_runtime_manifest_hash"],
            "e97aa6c8e6f449e0f3d0f51fd3921e66c51f763de6d64de3ed9f2474019ba9c9",
        )
        self.assertFalse(report["evidence"]["latest_runtime_manifest_is_current"])
        self.assertEqual(report["evidence"]["technical_runtime_smokes"], 11)
        self.assertEqual(report["evidence"]["ready_runtime_profiles"], [])
        self.assertFalse(report["production_ready"])
        self.assertEqual(
            report["next_gate"],
            "capture-content-addressed-runtime-manifest",
        )


if __name__ == "__main__":
    unittest.main()
