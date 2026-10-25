"""Resource IDs, registration and multi-agent stale-write guards."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import create_resource as create
import update_resource as update


class CreationTests(unittest.TestCase):
    def test_generated_document_requires_explicit_source_and_build(self):
        with self.assertRaises(create.ResourceError):
            create.registration("ccc-q01-example", "Example", "teacher_companion", "generated_pdf",
                                None, "example.pdf")
        with self.assertRaises(create.ResourceError):
            create.registration("ccc-q01-example", "Example", "teacher_companion", "generated_pdf",
                                "content/source.json")
        record = create.registration("ccc-q01-example", "Example", "teacher_companion",
                                     "generated_pdf", "content/example.json", "example.pdf")
        self.assertEqual(record["production_type"], "generated_pdf")
        self.assertEqual(record["build"], {"output": "example.pdf"})
        self.assertEqual(record["status"], "unpublished")
        self.assertNotIn("url", record)

    def test_external_resource_has_no_pdf_mapping(self):
        item = create.registration("ccc-q01-image", "Image", "visual_asset",
                                   "external", None)
        self.assertNotIn("build", item)
        with self.assertRaises(create.ResourceError):
            create.registration("ccc-q01-image", "Image", "visual_asset",
                                "external", None, "image.pdf")

    def test_existing_identity_is_reused_without_changing_live_status(self):
        item = create.registration("ccc-q01-image", "Image", "visual_asset", "external", None)
        old = dict(item, status="published", url="https://drive.google.com/file/d/aaa/view")
        registry, added = create.reconcile({"ccc-q01-image": old}, "ccc-q01-image", item)
        self.assertFalse(added)
        self.assertEqual(registry["ccc-q01-image"]["status"], "published")

    def test_duplicate_display_name_is_rejected(self):
        item = create.registration("ccc-q01-other", "Image", "visual_asset", "external", None)
        with self.assertRaises(create.ResourceError):
            create.reconcile({"ccc-q01-image": {"title": "image"}}, "ccc-q01-other", item)

    def test_paths_must_not_escape_editable_sources(self):
        for path in ["../secrets.txt", "/tmp/outside", "exports/generated.pdf", "content/../../out"]:
            with self.subTest(path=path):
                with self.assertRaises(create.ResourceError):
                    create.valid_repo_path(path)

    def test_stale_source_is_rejected_before_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            current = root / "existing.json"
            prototype = root / "prototype.json"
            catalogue = root / "resources.json"
            current.write_text('{"newer":"teammate"}')
            prototype.write_text('{"mine":"old"}')
            catalogue.write_text(json.dumps({"ccc-q01-example": {"title": "Example"}}))
            original = current.read_bytes()
            with patch.object(update, "switch_to_resource_branch",
                              return_value=("edit/ccc-q01-example", "a"*40)), \
                 patch.object(update, "REGISTRY", catalogue), \
                 patch.object(update, "valid_repo_path", return_value=current):
                with self.assertRaisesRegex(create.ResourceError, "changed since"):
                    update.update("ccc-q01-example", prototype, "content/existing.json", "b"*64)
            self.assertEqual(current.read_bytes(), original)

    def test_noop_update_does_not_commit_or_push(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            current = root / "current.json"
            catalogue = root / "resources.json"
            current.write_text('{"x":1}')
            catalogue.write_text(json.dumps({"ccc-q01-example": {"title": "Example"}}))
            expected = hashlib.sha256(current.read_bytes()).hexdigest()
            with patch.object(update, "switch_to_resource_branch",
                              return_value=("edit/ccc-q01-example", "a"*40)), \
                 patch.object(update, "REGISTRY", catalogue), \
                 patch.object(update, "valid_repo_path", return_value=current), \
                 patch.object(update, "cmd", side_effect=AssertionError("Should not call git")):
                result = update.update("ccc-q01-example", current, "content/current.json", expected)
            self.assertEqual(result["result"], "no content change")


if __name__ == "__main__":
    unittest.main()
