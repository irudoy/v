import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_MODEL = "claude-opus-4-8"


class CallerWorkflowSourceTest(unittest.TestCase):
    def assert_linkage_helper_is_not_parser_local(self, relative_path: str) -> None:
        source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        helper = re.search(r"(?m)^const requireValue\s*=", source)
        self.assertIsNotNone(helper)
        self.assertLess(helper.start(), source.index("const parseInput = value =>"))
        self.assertNotRegex(source, r"(?m)^[ \t]+const requireValue\s*=")
        self.assertIn("}).then(verdict => {\n    requireValue(", source)

    def test_prep_verify_linkage_helper_is_not_parser_local(self):
        self.assert_linkage_helper_is_not_parser_local(
            ".claude/workflows/vq-caller-prep.js"
        )

    def test_run_verify_linkage_helper_is_not_parser_local(self):
        self.assert_linkage_helper_is_not_parser_local(
            ".claude/workflows/vq-caller-run.js"
        )

    def test_saved_workflows_pin_exact_resolved_model(self):
        expected_counts = {
            ".claude/workflows/vq-caller-prep.js": 4,
            ".claude/workflows/vq-caller-run.js": 4,
            ".claude/workflows/vq-caller-score.js": 2,
        }
        for relative_path, expected_count in expected_counts.items():
            with self.subTest(workflow=relative_path):
                source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                models = re.findall(r"\bmodel:\s*'([^']+)'", source)
                self.assertEqual(models, [EXPECTED_MODEL] * expected_count)

    def test_control_plane_pins_same_exact_resolved_model(self):
        source = (REPO_ROOT / "tools/sweep/caller_ab_experiment.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(f'MODEL_ID = "{EXPECTED_MODEL}"', source)
        self.assertIn('config.get("model") != MODEL_ID', source)
        self.assertNotRegex(source, r'(?m)^MODEL_ID\s*=\s*[\"\']opus[\"\']')


if __name__ == "__main__":
    unittest.main()
