"""Checks for in-place Drive publishing, using a fake Drive service."""
import hashlib
import fitz
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
def make_pdf(width=612, height=792):
    pdf = fitz.open()
    pdf.new_page(width=width, height=height)
    data = pdf.tobytes()
    pdf.close()
    return data


PDF = make_pdf()


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
                      "build": {"renderer": "welcome", "source": "x.json"}}
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

    def test_verified_in_place_publish_and_retry_do_not_duplicate(self):
        service = FakeService()
        revision = "a" * 40
        with patch.object(pub, "current_revision", return_value=revision):
            report = self.run_publish(service)
            saved = self.registry.read_text()
            self.run_publish(service)
        self.assertEqual(service._files.updates, [FILE_ID])
        self.assertEqual(report["result"], "replaced in place")
        self.assertEqual(report["new_version"], "8")
        self.assertEqual(self.status(), "published")
        self.assertEqual(self.registry.read_text(), saved)
        publication = json.loads(saved)["ccc-q01-welcome"]["publication"]
        self.assertEqual(publication["verification"], "verified")
        self.assertEqual(publication["drive_file_id"], FILE_ID)
        self.assertEqual(publication["release_revision"], revision)
        self.assertEqual(publication["artifact_md5"], hashlib.md5(PDF).hexdigest())
        self.assertEqual(publication["drive_version"], "8")
        self.assertEqual(report["publication"], publication)

    def test_a4_pdf_is_blocked_before_upload(self):
        self.pdf.write_bytes(make_pdf(595, 842))
        service = FakeService()
        with patch.object(pub, "current_revision", return_value="a" * 40):
            with self.assertRaisesRegex(pub.PublishError, "US Letter"):
                self.run_publish(service)
        self.assertEqual(service._files.updates, [])
        self.assertEqual(self.status(), "pending_publish")

    def test_dry_run_changes_nothing(self):
        service = FakeService()
        report = self.run_publish(service, dry_run=True)
        self.assertEqual(service._files.updates, [])
        self.assertEqual(self.status(), "pending_publish")
        self.assertIn("dry run", report["result"])

    def test_unpublished_or_external_items_cannot_auto_publish(self):
        for status, production in [
            ("unpublished", "generated_pdf"),
            ("pending_publish", "external"),
        ]:
            with self.subTest(status=status, production=production):
                self.entry["status"] = status
                self.entry["production_type"] = production
                self.write({"ccc-q01-welcome": self.entry})
                with self.assertRaises(pub.PublishError):
                    self.run_publish(FakeService())

    def test_checksum_mismatch_fails_without_publishing(self):
        service = FakeService()
        service._files.store_md5 = False
        with self.assertRaises(pub.PublishError):
            self.run_publish(service)
        self.assertEqual(self.status(), "pending_publish")

    def test_unsafe_drive_destination_is_refused(self):
        for metadata in [
            {"capabilities": {"canEdit": False}},
            {"mimeType": "application/vnd.google-apps.document"},
        ]:
            with self.subTest(metadata=metadata):
                with self.assertRaises(pub.PublishError):
                    self.run_publish(FakeService(**metadata))






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






if __name__ == "__main__":
    unittest.main()
