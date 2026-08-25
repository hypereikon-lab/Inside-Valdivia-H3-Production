from pathlib import Path
import unittest

from tools.validate import ROOT, is_h3_frame_count, load_json, validate_repository, validate_workflow_spec


class RepositoryValidationTests(unittest.TestCase):
    def test_repository_is_consistent(self):
        self.assertEqual(validate_repository(), [])

    def test_h3_frame_grid(self):
        self.assertTrue(is_h3_frame_count(5))
        self.assertTrue(is_h3_frame_count(124))
        self.assertTrue(is_h3_frame_count(362))
        self.assertFalse(is_h3_frame_count(123))

    def test_workflow_ids_are_unique_and_complete(self):
        ids = {
            load_json(path)["id"]
            for path in (ROOT / "workflow_specs").glob("*.json")
        }
        self.assertEqual(ids, {"W1", "W2", "W3", "W4", "W5", "W6", "W7"})

    def test_implementation_classes_match_graph_owners(self):
        specs = {
            load_json(path)["id"]: load_json(path)
            for path in (ROOT / "workflow_specs").glob("*.json")
        }
        self.assertEqual(
            {specs[key]["implementation_class"] for key in ("W1", "W2", "W3")},
            {"official-h3"},
        )
        for key in ("W1", "W2", "W3"):
            self.assertNotIn("cauce", {stage["owner"] for stage in specs[key]["graph_contract"]})
        self.assertEqual(specs["W4"]["implementation_class"], "official-h3-with-cauce-primitives")
        self.assertEqual(specs["W5"]["implementation_class"], "official-h3-with-cauce-primitives")
        self.assertEqual(specs["W6"]["implementation_class"], "cauce-preprocess-to-official-h3")
        self.assertEqual(specs["W7"]["implementation_class"], "cauce-and-vanilla-deterministic")

    def test_validator_rejects_noncanonical_mechanism_language(self):
        path = Path("synthetic.json")
        value = load_json(ROOT / "workflow_specs" / "W1-keyframed-generation.json")
        value["operation"] = "A confluence seam fix"
        errors = validate_workflow_spec(value, path)
        self.assertTrue(any("non-canonical mechanism phrase" in error for error in errors))

    def test_native_continuation_is_composed_without_external_owner(self):
        value = load_json(ROOT / "workflow_specs" / "W4-native-tail-continuation.json")
        self.assertEqual(value["version"], 3)
        self.assertNotIn("external-pack", {stage["owner"] for stage in value["graph_contract"]})
        node_types = {stage.get("node_type") for stage in value["graph_contract"]}
        self.assertTrue(
            {
                "CauceH3PlanAVWindow",
                "CauceH3AllocateAVWindow",
                "CauceH3ExtractAVSpan",
                "CauceH3AddAVSpanGuide",
                "CauceH3AppendAVSpan",
            }
            <= node_types
        )

    def test_two_sided_graph_uses_primitives_not_a_preset(self):
        value = load_json(ROOT / "workflow_specs" / "W5-two-sided-guide-window.json")
        node_types = [stage.get("node_type") for stage in value["graph_contract"]]
        self.assertEqual(node_types.count("CauceAcceptDecodedRange"), 3)
        self.assertNotIn("CaucePrepareH3TwoSidedGuideWindow", node_types)
        self.assertNotIn("CauceAssembleH3TwoSidedGuideWindow", node_types)


if __name__ == "__main__":
    unittest.main()
