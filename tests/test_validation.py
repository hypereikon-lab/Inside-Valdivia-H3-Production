import copy
import unittest

from tools.validate import (
    ROOT,
    is_h3_frame_count,
    load_json,
    validate_materialization_plan,
    validate_operation_lock,
    validate_repository,
    validate_invocation,
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

    def test_operation_lock_is_semantic_and_content_addressed(self):
        lock_path = ROOT / "operations.lock.json"
        errors, registry = validate_operation_lock(load_json(lock_path), lock_path)
        self.assertEqual(errors, [])
        self.assertEqual(
            set(registry),
            {
                "connect.two_sided_guides",
                "continue.native_av",
                "frames.assemble",
                "generate.from_references",
                "generate.keyframed",
                "generate.with_guides",
                "reference.transform",
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
        motion = next(
            value for value in catalog["experiments"] if value["id"] == "motion-reference-map"
        )
        self.assertEqual(
            [value["id"] for value in motion["operations"]],
            ["reference.transform", "generate.from_references"],
        )

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


if __name__ == "__main__":
    unittest.main()
