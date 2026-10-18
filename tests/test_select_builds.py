"""Dependency selection tests; no extra runtime dependencies."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import select_builds as sb


class SelectionTests(unittest.TestCase):
    def test_targeted_lesson(self):
        self.assertEqual(sb.select([sb.LESSON]), [sb.GUIDE])

    def test_cover_only(self):
        self.assertEqual(sb.select([sb.COVER]), [sb.GUIDE])

    def test_single_companion(self):
        self.assertEqual(sb.select([sb.MISSION]), ["mission-video-questions.pdf"])

    def test_companion_renderer_rebuilds_companions(self):
        self.assertEqual(set(sb.select(["scripts/renderers/teacher_companion.py"])), sb.COMPANIONS)

    def test_guide_renderer_only(self):
        self.assertEqual(sb.select(["scripts/renderers/teacher_guide.py"]), [sb.GUIDE])

    def test_irrelevant_content_skipped(self):
        self.assertEqual(sb.select(["content/confetti-cake-cottage/quest-01-bake-off-betrayal/story/bakery-log-1958.md"]), [])

    def test_template_edit_alone_does_not_build(self):
        self.assertEqual(sb.select(["templates/student_worksheet/TEMPLATE.json"]), [])

    def test_draft_companion_skipped(self):
        self.assertEqual(sb.select([sb.QUEST + "/resources/teacher_companion/songwriting-extension.json"]), [])

    def test_registry_only_affected_refs(self):
        with patch.object(sb, "changed_registry_ids", return_value={"ccc-q01-mrs-tongsleys-letter"}):
            self.assertEqual(sb.select(["catalog/resources.json"], "origin/main"), [sb.GUIDE])
        with patch.object(sb, "changed_registry_ids", return_value={"ccc-q01-activate-confetti-questions"}):
            self.assertEqual(sb.select(["catalog/resources.json"], "origin/main"), [])

    def test_registry_unknown_rebuilds_all(self):
        self.assertEqual(set(sb.select(["catalog/resources.json"])), sb.ALL)

    def test_shared_script_rebuilds_all(self):
        self.assertEqual(set(sb.select(["scripts/build.py"])), sb.ALL)

    def test_unrecognized_dependencies_are_conservative(self):
        self.assertEqual(set(sb.select(["new-build-input.dat"])), sb.ALL)


if __name__ == "__main__":
    unittest.main()
