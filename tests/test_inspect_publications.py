"""One test suite for publication audit: Exists, Accessible, Correct."""
import hashlib
import fitz
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inspect_publications as audit

PPTX = "1PQnFI3ryAvTj70NNKmlWqfbdkOcDUPkd"
PDF = "1r5w-EWU3N47iz5p02NSOsmN-P7Kv7QJt"
KWLS = "1O6VRLTguA3Cb76k3U5refPd4Hiz7sBoK"
GUIDE = "17Rre95B3gMZqY02rgmxYO23uo_PRQ3x5"
DIGEST = hashlib.md5(b"original version").hexdigest()


def letter_pdf():
    document = fitz.open()
    document.new_page(width=612, height=792)
    data = document.tobytes()
    document.close()
    return data

LETTER_PDF = letter_pdf()


def url(fid):
    return "https://drive.google.com/file/d/" + fid + "/view"


def item(fid, *, status="published", typ="student_worksheet", checksum=DIGEST,
         other=None):
    obj = {"status": status, "type": typ, "production_type": "external",
           "published_url": url(fid) if status == "published" else None,
           "publication": {"drive_file_id": fid, "approved_md5": checksum}}
    obj.update(other or {})
    return obj


def meta(fid, *, mime="application/pdf", folder="official", trashed=False,
         digest=DIGEST):
    return {"id": fid, "name": "sample", "mimeType": mime, "parents": [folder],
            "trashed": trashed, "md5Checksum": digest}


class Request:
    def __init__(self, value=None, error=None):
        self.value, self.error = value, error

    def execute(self):
        if self.error:
            raise self.error
        return self.value


class Drive:
    def __init__(self, metadata, *, public=True, error=None, pdf=None):
        self.metadata, self.public = metadata, public
        self.error, self.pdf = error, pdf
        self.requests = []

    def files(self):
        return self

    def get(self, fileId, **kwargs):
        self.requests.append(fileId)
        if fileId not in self.metadata:
            return Request(error=FileNotFoundError(fileId))
        return Request(self.metadata[fileId])

    def get_media(self, fileId, **kwargs):
        return Request(self.pdf if self.pdf is not None else LETTER_PDF)

    def permissions(self):
        return self

    def list(self, **kwargs):
        if self.error:
            return Request(error=self.error)
        return Request({"permissions": [
            {"type": "anyone" if self.public else "user",
             "role": "reader"}]})


def run(entries, files, folders=None, public=True, source_targets=None, pdf=None):
    config = {"published": {"by_resource_id": folders or {}}}
    service = Drive(files, public=public, pdf=pdf)
    report = audit.audit(entries, config, service=service,
                         source_targets=source_targets or {})
    return report, service


class AuditTests(unittest.TestCase):
    def test_unpublished_skipped(self):
        result, service = run(
            {"published": item(PDF),
             "draft": item(KWLS, status="unpublished", other={"url": url(KWLS)})},
            {PDF: meta(PDF)}, {"published": "official"})
        self.assertEqual(result["result"], audit.PASS)
        self.assertEqual(service.requests, [PDF])

    def test_deleted_slides_detected_in_both_formats(self):
        deck = item(PPTX, typ="slide_deck", other={
            "pdf_url": url(PDF),
            "publication": {"drive_file_id": PPTX, "approved_md5": DIGEST,
                            "pdf_md5": DIGEST}})
        files = {
            PPTX: meta(PPTX, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                       trashed=True),
            PDF: meta(PDF)}
        result, service = run({"deck": deck}, files, {
            "deck": {"main": "official", "pdf": "official"}})
        self.assertEqual(result["resources"][0]["checks"]["exists"]["result"], audit.FAIL)
        self.assertCountEqual(service.requests, [PPTX, PDF])

    def test_missing_and_wrong_folder(self):
        for files, reason in [({}, "Missing"), ({KWLS: meta(KWLS, folder="wrong")}, "folder")]:
            with self.subTest(reason=reason):
                result, _ = run({"kwls": item(KWLS)}, files, {"kwls": "official"})
                self.assertEqual(result["resources"][0]["checks"]["exists"]["result"], audit.FAIL)

    def test_public_access(self):
        for public, expected in [(True, audit.PASS), (False, audit.FAIL)]:
            with self.subTest(public=public):
                result, _ = run({"kwls": item(KWLS)}, {KWLS: meta(KWLS)},
                                {"kwls": "official"}, public=public)
                self.assertEqual(result["resources"][0]["checks"]["accessible"]["result"],
                                 expected)

    def test_printable_pdf_paper_size(self):
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        a4 = doc.tobytes()
        doc.close()
        for payload, expected in [(LETTER_PDF, audit.PASS), (a4, audit.FAIL)]:
            with self.subTest(expected=expected):
                report, _ = run({"sheet": item(KWLS)},
                                {KWLS: meta(KWLS)}, {"sheet": "official"},
                                pdf=payload)
                self.assertEqual(report["resources"][0]["checks"]["correct"]["result"],
                                 expected)

    def test_teacher_guide_and_companion_are_exempt_from_letter_size(self):
        doc = fitz.open()
        doc.new_page(width=595.28, height=841.89)
        a4 = doc.tobytes()
        doc.close()
        for resource_type in ("published_export", "teacher_companion", "teacher_reference"):
            with self.subTest(resource_type=resource_type):
                result, _ = run({"example": item(KWLS, typ=resource_type)},
                                {KWLS: meta(KWLS)}, {"example": "official"}, pdf=a4)
                self.assertEqual(result["resources"][0]["checks"]["correct"]["result"],
                                 audit.PASS)

    def test_slide_pdf_is_not_forced_to_letter(self):
        deck = item(PPTX, typ="slide_deck", other={
            "pdf_url": url(PDF),
            "publication": {"drive_file_id": PPTX, "approved_md5": DIGEST,
                            "pdf_md5": DIGEST}})
        doc = fitz.open()
        doc.new_page(width=960, height=540)
        widescreen = doc.tobytes()
        doc.close()
        files = {PPTX: meta(PPTX, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"),
                 PDF: meta(PDF)}
        report, _ = run({"slides": deck}, files,
                        {"slides": {"main": "official", "pdf": "official"}},
                        pdf=widescreen)
        self.assertEqual(report["result"], audit.PASS)

    def test_checksum_matching(self):
        for digest, expected in [(DIGEST, audit.PASS), ("b" * 32, audit.FAIL)]:
            with self.subTest(digest=digest):
                result, _ = run({"kwls": item(KWLS)},
                                {KWLS: meta(KWLS, digest=digest)},
                                {"kwls": "official"})
                self.assertEqual(result["resources"][0]["checks"]["correct"]["result"],
                                 expected)

    def test_missing_approval_cannot_pass(self):
        result, _ = run({"kwls": item(KWLS, checksum=None)},
                        {KWLS: meta(KWLS)})
        self.assertEqual(result["result"], audit.REVIEW)

    def test_generated_pdf_compares_approved_source(self):
        with tempfile.TemporaryDirectory() as path:
            output = Path(path) / "built.pdf"
            output.write_bytes(b"changed GitHub source")
            record = item(GUIDE, other={"production_type": "generated_pdf",
                                        "build": {"renderer": "welcome", "source": "x"}})
            result = audit.audit(
                {"overview": record},
                {"published": {"by_resource_id": {"overview": "official"}}},
                service=Drive({GUIDE: meta(GUIDE)}),
                builder=lambda *_: output, source_targets={})
            self.assertEqual(result["resources"][0]["checks"]["correct"]["result"],
                             audit.FAIL)

    def test_published_guide_cannot_link_to_draft(self):
        import fitz
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_link({"kind": fitz.LINK_URI,
                          "from": fitz.Rect(10, 10, 100, 25), "uri": url(KWLS)})
        data = doc.tobytes()
        doc.close()
        guide = item(GUIDE, other={"production_type": "generated_pdf",
                                   "build": {"output": "02-secret-ingredients-teacher-guide.pdf"}})
        draft = item(KWLS, status="unpublished", other={"url": url(KWLS)})
        t = {"02-secret-ingredients-teacher-guide.pdf": {
            "resource_id": "guide", "kind": "teacher_guide",
            "data": {"core": [{"ref": "draft"}]}}}
        result, _ = run({"guide": guide, "draft": draft},
                        {GUIDE: meta(GUIDE)}, {"guide": "official"},
                        source_targets=t, pdf=data)
        self.assertEqual(result["resources"][0]["checks"]["correct"]["result"],
                         audit.FAIL)
        self.assertIn("unpublished", result["resources"][0]["checks"]["correct"]["details"]["guide_links"])

    def test_published_guide_unregistered_link_requires_review(self):
        import fitz
        doc = fitz.open()
        doc.new_page().insert_link({
            "kind": fitz.LINK_URI, "from": fitz.Rect(10, 10, 100, 25),
            "uri": "https://example.org/not-registered"})
        data = doc.tobytes()
        doc.close()
        guide = item(GUIDE, checksum=None, other={"production_type": "generated_pdf",
                                   "build": {"output": "02-secret-ingredients-teacher-guide.pdf"}})
        t = {"02-secret-ingredients-teacher-guide.pdf": {
            "resource_id": "guide", "kind": "teacher_guide", "data": {}}}
        result, _ = run({"guide": guide}, {GUIDE: meta(GUIDE)},
                        {"guide": "official"}, source_targets=t, pdf=data)
        self.assertEqual(result["resources"][0]["checks"]["correct"]["result"],
                         audit.REVIEW)

    def test_no_fake_pass_on_ambiguous_drive_link(self):
        bad = item(KWLS, other={"published_url": "https://drive.google.com/"})
        result, _ = run({"bad": bad}, {}, {"bad": "official"})
        self.assertEqual(result["result"], audit.FAIL)


if __name__ == "__main__":
    unittest.main()
