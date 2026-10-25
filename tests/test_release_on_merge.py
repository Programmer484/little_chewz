"""Authorized merged-PR release routing and safety regression tests."""
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
        self.root = Path(self.temp.name)
        (self.root / ".github/resource-releases").mkdir(parents=True)
        self.patch = patch.object(rel, "ROOT", self.root)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def marker(self, number=77, ids=None, signal="authorized-resource-merge"):
        path = self.root / ".github/resource-releases" / f"{number}.json"
        path.write_text(json.dumps({"signal": signal, "pr_number": number,
                                    "resource_ids": ids or ["ccc-q01-welcome"]}))
        return path.relative_to(self.root).as_posix()

    def test_unmarked_merge_never_publishes(self):
        self.assertEqual(rel.release_request(77, {"README.md"}), [])

    def test_request_requires_matching_pr_and_signal(self):
        marker = self.marker()
        self.assertEqual(rel.release_request(77, {marker}), ["ccc-q01-welcome"])
        self.assertEqual(rel.release_request(78, {marker}), [])
        self.marker(signal="not-authorized")
        with self.assertRaises(rel.ReleaseError):
            rel.release_request(77, {marker})

    def test_duplicate_or_unsafe_resource_ids_rejected(self):
        for ids in [["a", "a"], ["../escape"], ["A-B"]]:
            with self.subTest(ids=ids):
                marker = self.marker(ids=ids)
                with self.assertRaises(rel.ReleaseError):
                    rel.release_request(77, {marker})

    def test_generated_with_verified_destination_is_selected(self):
        marker = self.marker()
        registry = {"ccc-q01-welcome": {"production_type": "generated_pdf",
                                        "status": "pending_publish",
                                        "url": "https://drive.google.com/file/d/12345678901234567890/view",
                                        "build": {"renderer": "claude", "source": "welcome.json"}}}
        def git(*args):
            if args[0] == "rev-parse":
                return "b" * 40
            if args[0] == "diff":
                return ""
            raise AssertionError(args)
        with patch.object(rel, "git", side_effect=git), \
             patch.object(rel.subprocess, "run", return_value=type("P", (), {"returncode": 0})()), \
             patch.object(rel, "load_registry", return_value=registry), \
             patch.object(rel, "targets", return_value={"ccc-q01-welcome.pdf": {}}), \
             patch.object(rel, "select", return_value=["ccc-q01-welcome.pdf"]):
            result = rel.plan(77, {marker, "welcome.json"}, "a" * 40, "9" * 40)
        self.assertEqual(result["generated"], ["ccc-q01-welcome"])
        self.assertEqual(result["blocked"], [])

    def test_only_one_resource_per_release(self):
        marker=self.marker(ids=["resource-a", "resource-b"])
        with self.assertRaises(rel.ReleaseError):
            rel.release_request(77, {marker})

    def test_release_branch_must_match_resource(self):
        marker=self.marker()
        with self.assertRaisesRegex(rel.ReleaseError, "single matching"):
            rel.plan(77, {marker}, "a"*40, "b"*40, "edit/different-resource")

    def test_failed_verified_release_keeps_pending_for_old_live_version(self):
        record = {"ccc-q01-welcome": {"production_type": "generated_pdf",
                   "status": "published", "url": "https://drive.google.com/file/d/12345678901234567890/view",
                   "build": {"renderer": "claude", "source": "welcome.json"}}}
        report = {"generated": [], "pending": ["ccc-q01-welcome"],
                  "blocked": [{"resource_id": "ccc-q01-welcome", "reason": "superseded"}]}
        with patch.object(rel, "load_registry", return_value=record), \\
             patch.object(rel, "save_registry") as save:
            rel.run_release(report)
        self.assertEqual(record["ccc-q01-welcome"]["status"], "pending_publish")
        save.assert_called_once()

    def test_external_never_enters_auto_pdf_publisher(self):
        marker = self.marker(ids=["ccc-q01-slides"])
        registry = {"ccc-q01-slides": {"production_type": "external", "status": "published"}}
        with patch.object(rel, "git", return_value="a" * 40), \
             patch.object(rel.subprocess, "run", return_value=type("P", (), {"returncode": 0})()), \
             patch.object(rel, "load_registry", return_value=registry), \
             patch.object(rel, "targets", return_value={}), \
             patch.object(rel, "select", return_value=[]):
            result = rel.plan(77, {marker}, "a" * 40, "9" * 40)
        self.assertEqual(result["generated"], [])
        self.assertEqual(result["external"], [])
        self.assertIn("External resources", result["blocked"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
