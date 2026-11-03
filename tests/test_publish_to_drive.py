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
        self.entry = {"title": "Quest Overview", "type": "welcome",
                      "published_url": f"https://drive.google.com/file/d/{FILE_ID}/view",
                      "holding_url": None,
                      "pdf": {"renderer": "welcome", "source": "x.json",
                              "approved_md5": "0" * 32, "revision": "b" * 40}}
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
        return pub.publication_status(json.loads(self.registry.read_text())["ccc-q01-welcome"],
                                      hashlib.md5(self.pdf.read_bytes()).hexdigest())

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
        pdf = json.loads(saved)["ccc-q01-welcome"]["pdf"]
        self.assertEqual(pdf["renderer"], "welcome")
        self.assertEqual(pdf["source"], "x.json")
        self.assertEqual(pdf["revision"], revision)
        self.assertEqual(pdf["approved_md5"], hashlib.md5(PDF).hexdigest())
        self.assertEqual(report["drive_version"], "8")
        self.assertEqual(report["pdf"], pdf)

    def test_first_verified_replacement_records_missing_baseline(self):
        entry = {**self.entry, "pdf": {"renderer": "welcome", "source": "x.json"}}
        self.write({"ccc-q01-welcome": entry})
        with patch.object(pub, "current_revision", return_value="a" * 40):
            report = self.run_publish(FakeService(md5Checksum=hashlib.md5(PDF).hexdigest()))
        details = json.loads(self.registry.read_text())["ccc-q01-welcome"]["pdf"]
        self.assertEqual(details["approved_md5"], hashlib.md5(PDF).hexdigest())
        self.assertEqual(details["revision"], "a" * 40)
        self.assertEqual(report["result"], "unchanged: Drive already has these exact bytes")

    def test_a4_generated_teacher_guide_is_allowed(self):
        self.pdf.write_bytes(make_pdf(595.28, 841.89))
        service = FakeService()
        with patch.object(pub, "current_revision", return_value="a" * 40):
            result = self.run_publish(service)
        self.assertEqual(result["result"], "replaced in place")
        self.assertEqual(service._files.updates, [FILE_ID])

    def test_dry_run_changes_nothing(self):
        service = FakeService()
        report = self.run_publish(service, dry_run=True)
        self.assertEqual(service._files.updates, [])
        self.assertEqual(self.status(), "pending_publish")
        self.assertIn("dry run", report["result"])

    def test_initial_publication_and_external_items_cannot_auto_publish(self):
        for official, generated in [(None, True), (self.entry["published_url"], False)]:
            with self.subTest(official=official, generated=generated):
                entry = {**self.entry, "published_url": official}
                if not generated:
                    entry.pop("pdf")
                self.write({"ccc-q01-welcome": entry})
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
        self.assertEqual(json.loads(self.registry.read_text())["ccc-q01-welcome"]["pdf"],
                         self.entry["pdf"])






if __name__ == "__main__":
    unittest.main()
