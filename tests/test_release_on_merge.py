"""Risk-focused authorization and release-routing tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import release_on_merge as rel


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".github/resource-releases").mkdir(parents=True)
        root_patch = patch.object(rel, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def marker(self, ids=None, number=77, signal="authorized-resource-merge"):
        path = self.root / f".github/resource-releases/{number}.json"
        path.write_text(json.dumps({
            "signal": signal,
            "pr_number": number,
            "resource_ids": ["ccc-q01-welcome"] if ids is None else ids,
        }))
        return path.relative_to(self.root).as_posix()

    def test_authorization_requires_matching_marker_and_safe_unique_ids(self):
        self.assertEqual(rel.release_request(77, {"README.md"}), [])
        marker = self.marker()
        self.assertEqual(rel.release_request(77, {marker}), ["ccc-q01-welcome"])
        self.assertEqual(rel.release_request(78, {marker}), [])
        for ids in ([], ["a", "a"], ["../unsafe"], ["A-B"]):
            with self.subTest(ids=ids):
                marker = self.marker(ids=ids)
                with self.assertRaises(rel.ReleaseError):
                    rel.release_request(77, {marker})
        with self.subTest(reason="wrong signal"):
            marker = self.marker(signal="incorrect")
            with self.assertRaises(rel.ReleaseError):
                rel.release_request(77, {marker})

    def test_multiple_owned_resources_can_release_together(self):
        guide = "ccc-q01-secret-ingredients-teacher-guide"
        companion = "ccc-q01-secret-ingredients-questions"
        ids = [guide, companion]
        marker = self.marker(ids=ids)
        entries = {
            guide: {"production_type": "generated_pdf", "published_url": "https://drive.google.com/file/d/example/view",
                    "build": {"output": "02-secret-ingredients-teacher-guide.pdf"}},
            companion: {"production_type": "generated_pdf", "published_url": "https://drive.google.com/file/d/example/view",
                        "build": {"output": "questions.pdf"}},
        }
        selected = ["02-secret-ingredients-teacher-guide.pdf", "questions.pdf"]
        targets = {
            selected[0]: {"kind": "teacher_guide", "resource_id": guide,
                          "source": "content/ccc/quest/lessons/02-secret-ingredients/lesson.json",
                          "data": {}},
            selected[1]: {"kind": "teacher_companion", "resource_id": companion, "data": {}},
        }
        def git(*args):
            return "a" * 40 if args[0] == "rev-parse" else ""

        with (patch.object(rel, "load_registry", return_value=entries),
              patch.object(rel, "targets", return_value=targets),
              patch.object(rel, "select", return_value=selected),
              patch.object(rel, "git", side_effect=git),
              patch.object(rel.subprocess, "run",
                           return_value=type("Result", (), {"returncode": 0})())):
            plan = rel.plan(77, {marker, "lesson.json", "questions.json"},
                            "a" * 40, "b" * 40,
                            head_branch="lesson/ccc-q01-02-secret-ingredients")
            self.assertEqual(plan["generated"], ids)
            self.assertEqual(plan["blocked"], [])
            with self.assertRaisesRegex(rel.ReleaseError, "does not own"):
                rel.plan(77, {marker}, "a" * 40, "b" * 40,
                         head_branch="lesson/ccc-q01-01-set-the-table")

    def test_external_resources_never_enter_auto_publisher(self):
        marker = self.marker(ids=["ccc-q01-slides"])
        with (patch.object(rel, "load_registry", return_value={
                    "ccc-q01-slides": {"production_type": "external", "published_url": "https://example.org/live"}}),
              patch.object(rel, "targets", return_value={}),
              patch.object(rel, "select", return_value=[]),
              patch.object(rel, "git", return_value="a" * 40),
              patch.object(rel.subprocess, "run",
                           return_value=type("Result", (), {"returncode": 0})())):
            result = rel.plan(77, {marker}, "a" * 40, "b" * 40)
        self.assertFalse(result["generated"])
        self.assertIn("External resources", result["blocked"][0]["reason"])

    def test_failed_release_leaves_registry_evidence_untouched(self):
        registry = {"ccc-q01-welcome": {
            "published_url": "https://drive.google.com/file/d/existing/view",
            "publication": {"artifact_md5": "a" * 32},
        }}
        plan = {"generated": [],
                "blocked": [{"resource_id": "ccc-q01-welcome", "reason": "superseded"}]}
        with (patch.object(rel, "load_registry", return_value=registry),
              patch.object(rel, "publish") as publish):
            result = rel.run_release(plan)
        self.assertEqual(result, plan)
        self.assertEqual(registry["ccc-q01-welcome"]["publication"]["artifact_md5"], "a" * 32)
        publish.assert_not_called()


if __name__ == "__main__":
    unittest.main()
