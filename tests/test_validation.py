import copy
import unittest

from tools.validate import (
    ROOT,
    is_h3_frame_count,
    is_h3_visual_boundary,
    load_json,
    validate_materialization_catalog,
    validate_materialization_plan,
    validate_media_catalog,
    validate_operation_lock,
    validate_repository,
    validate_invocation,
    validate_rolling_catalog,
    validate_rolling_plan,
    validate_segment,
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
                "frames.assemble",
                "generate.from_references",
                "generate.keyframed",
                "generate.with_guides",
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
                self.assertEqual(operation["version"], registry[operation["id"]]["version"])

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
            ],
        )
        for entry in catalog["plans"]:
            self.assertEqual(entry["topology_key"], f"{entry['operation']}@{entry['variant']}")

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


if __name__ == "__main__":
    unittest.main()
