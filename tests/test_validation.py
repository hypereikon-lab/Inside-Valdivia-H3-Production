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

    def test_validator_rejects_legacy_mechanism_language(self):
        path = Path("synthetic.json")
        value = load_json(ROOT / "workflow_specs" / "W1-keyframed-generation.json")
        value["operation"] = "A confluence seam fix"
        errors = validate_workflow_spec(value, path)
        self.assertTrue(any("legacy phrase" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
