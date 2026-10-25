"""External agent publication and manual inspection do not invent parity."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import external_resources as ext
import inspect_publications as inspection

FILE_ID = "1aaaaaaaaaaaaaaaaaaaaaaaa"
FOLDER = "1bbbbbbbbbbbbbbbbbbbbbbbb"


class Request:
    def __init__(self, data):
        self.data = data
    def execute(self):
        return self.data


class Files:
    def __init__(self):
        self.meta = {"id": FILE_ID, "name": "Test.pdf", "mimeType": "application/pdf",
                     "parents": [FOLDER], "version": "3", "md5Checksum": "a" * 32,
                     "capabilities": {"canEdit": True, "canAddChildren": True}}
        self.updates = []
    def get(self, fileId, fields, supportsAllDrives):
        if fileId == FOLDER:
            return Request({"id": FOLDER, "mimeType": ext.FOLDER_MIME,
                            "capabilities": {"canAddChildren": True}})
        return Request(dict(self.meta))
    def update(self, fileId, media_body, fields, supportsAllDrives):
        self.updates.append(fileId)
        self.meta["version"] = "4"
        return Request(dict(self.meta))


class Service:
    def __init__(self):
        self._files = Files()
    def files(self):
        return self._files


class ExternalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.file = Path(self.temp.name) / "Test.pdf"
        self.file.write_bytes(b"%PDF pretend source")
        self.item = {"production_type": "external", "type": "student_worksheet",
                     "status": "pending_publish",
                     "url": f"https://drive.google.com/file/d/{FILE_ID}/view"}
    def tearDown(self):
        self.temp.cleanup()

    def test_unconfigured_staging_folder_fails_closed(self):
        config = Path(self.temp.name) / "folders.json"
        config.write_text('{"staging":{"external":{"folder_id":null}}}')
        with patch.object(ext, "FOLDER_CONFIG", config):
            with patch.object(ext, "drive_service", return_value=Service()):
                with self.assertRaises(ext.PublishError):
                    ext.stage_file(self.file, "application/pdf")

    def test_external_replacement_preserves_existing_id_and_no_digest(self):
        data = {"resource-1": self.item}
        saved = []
        service = Service()
        with patch.object(ext, "confirm_accepted_revision"), \
             patch.object(ext, "source_media", return_value="binary"), \
             patch.object(ext, "load_registry", return_value=data), \
             patch.object(ext, "save_registry", side_effect=lambda registry: saved.append(registry)):
            report = ext.publish_file("resource-1", self.file, "application/pdf", "a"*40,
                                      service=service)
        self.assertEqual(service._files.updates, [FILE_ID])
        self.assertEqual(report["file_id"], FILE_ID)
        self.assertEqual(self.item["status"], "published")
        self.assertEqual(self.item["publication"]["content_parity"], "unverified")
        self.assertNotIn("artifact_md5", self.item["publication"])
        self.assertTrue(saved)

    def test_slide_deck_is_blocked_from_generic_publisher(self):
        self.item["type"] = "slide_deck"
        with patch.object(ext, "confirm_accepted_revision"), \
             patch.object(ext, "load_registry", return_value={"resource-1": self.item}):
            with self.assertRaisesRegex(ext.PublishError, "Slide"):
                ext.publish_file("resource-1", self.file, "application/pdf", "a"*40)

    def test_external_inspection_never_asserts_content_parity(self):
        item = dict(self.item, publication={"verification": "verified",
                    "drive_file_id": FILE_ID, "drive_version": "3"})
        outcome = inspection.inspect_one("resource-1", item, service=Service())
        self.assertEqual(outcome["result"], "verified_metadata_only")
        self.assertEqual(outcome["content_parity"], "unverified")

    def test_generated_checksum_discrepancy_is_reported(self):
        item = {"production_type": "generated_pdf", "type": "published_export",
                "status": "published", "url": self.item["url"],
                "publication": {"verification": "verified", "drive_file_id": FILE_ID,
                                "artifact_md5": "b" * 32}}
        result = inspection.inspect_one("resource-1", item, service=Service())
        self.assertEqual(result["result"], "discrepancy")

    def test_unverified_live_record_is_not_treated_as_proven(self):
        item = {"production_type": "generated_pdf", "status": "published",
                "url": self.item["url"]}
        result = inspection.inspect_one("resource-1", item, service=Service())
        self.assertEqual(result["result"], "unverified")


if __name__ == "__main__":
    unittest.main()
