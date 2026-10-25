"""Checks for in-place Drive publishing, using a fake Drive service."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_to_drive as pub

FILE_ID = "1w-es-VamWXMfCrr34pRbq59a3ASngEbL"
PDF = b"%PDF-1.4 test document"


class FakeRequest:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


class FakeFiles:
    def __init__(self, meta, store_md5=True):
        self.meta = meta
        self.store_md5 = store_md5
        self.updates = []

    def get(self, fileId, fields, supportsAllDrives):
        assert fileId == self.meta["id"]
        return FakeRequest(dict(self.meta))

    def update(self, fileId, media_body, fields, supportsAllDrives):
        data = Path(media_body._filename).read_bytes()
        self.updates.append(fileId)
        self.meta["version"] = str(int(self.meta["version"]) + 1)
        self.meta["md5Checksum"] = hashlib.md5(data).hexdigest() if self.store_md5 else "bad"
        return FakeRequest(dict(self.meta))


class FakeService:
    def __init__(self, **meta):
        base = {"id": FILE_ID, "name": "Quest_Overview.pdf", "mimeType": "application/pdf",
                "md5Checksum": "old", "version": "7", "capabilities": {"canEdit": True}}
        base.update(meta)
        self._files = FakeFiles(base)

    def files(self):
        return self._files


class FakeMedia:
    def __init__(self, filename, mimetype, resumable):
        self._filename = filename


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.registry = self.tmp / "resources.json"
        self.pdf = self.tmp / "out.pdf"
        self.pdf.write_bytes(PDF)
        self.entry = {"title": "Quest Overview", "url": f"https://drive.google.com/file/d/{FILE_ID}/view",
                      "type": "published_export", "production_type": "generated_pdf",
                      "published_url": f"https://drive.google.com/file/d/{FILE_ID}/view",
                      "holding_url": None, "status": "pending_publish",
                      "build": {"renderer": "claude", "source": "x.json"}}
        self.write({"ccc-q01-welcome": self.entry})
        self.patches = [patch.object(pub, "REGISTRY", self.registry)]
        try:
            import googleapiclient.http  # noqa: F401
            self.patches.append(patch("googleapiclient.http.MediaFileUpload", FakeMedia))
        except ImportError:
            fake = type(sys)("googleapiclient.http")
            fake.MediaFileUpload = FakeMedia
            pkg = type(sys)("googleapiclient")
            pkg.http = fake
            self.patches.append(patch.dict(sys.modules, {"googleapiclient": pkg, "googleapiclient.http": fake}))
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.tmp)

    def write(self, data):
        self.registry.write_text(json.dumps(data, indent=2) + "\n")

    def status(self):
        return json.loads(self.registry.read_text())["ccc-q01-welcome"]["status"]

    def run_publish(self, service, dry_run=False):
        return pub.publish("ccc-q01-welcome", dry_run=dry_run, service=service, builder=lambda *_: self.pdf)

    def test_replaces_in_place_and_marks_published(self):
        service = FakeService()
        report = self.run_publish(service)
        self.assertEqual(service._files.updates, [FILE_ID])
        self.assertEqual(report["result"], "replaced in place")
        self.assertEqual(report["new_version"], "8")
        self.assertEqual(self.status(), "published")

    def test_dry_run_changes_nothing(self):
        service = FakeService()
        report = self.run_publish(service, dry_run=True)
        self.assertEqual(service._files.updates, [])
        self.assertEqual(self.status(), "pending_publish")
        self.assertIn("dry run", report["result"])

    def test_unpublished_entry_is_refused(self):
        self.entry["status"] = "unpublished"
        self.write({"ccc-q01-welcome": self.entry})
        with self.assertRaises(pub.PublishError):
            self.run_publish(FakeService())

    def test_checksum_mismatch_fails_without_publishing(self):
        service = FakeService()
        service._files.store_md5 = False
        with self.assertRaises(pub.PublishError):
            self.run_publish(service)
        self.assertEqual(self.status(), "pending_publish")

    def test_read_only_destination_is_refused(self):
        with self.assertRaises(pub.PublishError):
            self.run_publish(FakeService(capabilities={"canEdit": False}))

    def test_non_pdf_destination_is_refused(self):
        with self.assertRaises(pub.PublishError):
            self.run_publish(FakeService(mimeType="application/vnd.google-apps.document"))

    def test_identical_bytes_skip_upload(self):
        service = FakeService(md5Checksum=hashlib.md5(PDF).hexdigest())
        report = self.run_publish(service)
        self.assertEqual(service._files.updates, [])
        self.assertIn("unchanged", report["result"])

    def test_persists_verified_digest_and_revision(self):
        revision = "a" * 40
        with patch.object(pub, "current_revision", return_value=revision):
            report = self.run_publish(FakeService())
        record = json.loads(self.registry.read_text())["ccc-q01-welcome"]["publication"]
        self.assertEqual(record["verification"], "verified")
        self.assertEqual(record["method"], "generated_pdf")
        self.assertEqual(record["drive_file_id"], FILE_ID)
        self.assertEqual(record["release_revision"], revision)
        self.assertEqual(record["artifact_md5"], hashlib.md5(PDF).hexdigest())
        self.assertEqual(record["drive_version"], "8")
        self.assertEqual(report["publication"], record)

    def test_completed_retry_does_not_update_or_duplicate(self):
        service = FakeService()
        with patch.object(pub, "current_revision", return_value="a" * 40):
            self.run_publish(service)
            first = self.registry.read_text()
            self.run_publish(service)
        self.assertEqual(self.registry.read_text(), first)
        self.assertEqual(service._files.updates, [FILE_ID])

    def test_external_resources_must_not_enter_pdf_publisher(self):
        self.entry["production_type"] = "external"
        self.write({"ccc-q01-welcome": self.entry})
        with self.assertRaisesRegex(pub.PublishError, "external"):
            self.run_publish(FakeService())

    def test_stale_accepted_revision_is_rejected_before_drive_upload(self):
        service = FakeService()
        with patch.object(pub, "current_revision", return_value="a" * 40):
            with self.assertRaisesRegex(pub.PublishError, "revision changed"):
                pub.publish("ccc-q01-welcome", expected_revision="b" * 40,
                            service=service, builder=lambda *_: self.pdf)
        self.assertEqual(service._files.updates, [])
        self.assertEqual(self.status(), "pending_publish")

    def test_readback_mismatch_keeps_pending(self):
        service = FakeService()
        good = dict(service._files.meta)
        bad = dict(good, md5Checksum="different")
        with patch.object(pub, "current_revision", return_value="a" * 40):
            with patch.object(pub, "check_destination", side_effect=[good, bad]):
                with self.assertRaisesRegex(pub.PublishError, "read-back"):
                    self.run_publish(service)
        self.assertEqual(self.status(), "pending_publish")
        self.assertNotIn("publication", json.loads(self.registry.read_text())["ccc-q01-welcome"])

    def test_drive_file_id_parsing(self):
        self.assertEqual(pub.drive_file_id(f"https://drive.google.com/file/d/{FILE_ID}/view?usp=x"), FILE_ID)
        with self.assertRaises(pub.PublishError):
            pub.drive_file_id("https://example.com/nothing")

    def test_build_names_match_preview_outputs(self):
        self.assertEqual(pub.output_name("ccc-q01-welcome", {"renderer": "claude", "source": "x.json"}),
                         "ccc-q01-welcome.pdf")
        self.assertEqual(pub.output_name("x", {"output": "00-activate-teacher-guide.pdf"}),
                         "00-activate-teacher-guide.pdf")
        with self.assertRaises(pub.PublishError):
            pub.output_name("x", {})

    def test_registry_welcome_entry_is_publishable(self):
        registry = json.loads((pub.ROOT / "catalog/resources.json").read_text())
        file_id, build = pub.check_entry("ccc-q01-welcome", registry.get("ccc-q01-welcome"))
        self.assertEqual(file_id, FILE_ID)
        self.assertTrue((pub.ROOT / build["source"]).is_file())


if __name__ == "__main__":
    unittest.main()
