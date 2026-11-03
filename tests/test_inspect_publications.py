"""Inspector tests: Drive permissions and URL-specific human approval."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inspect_publications as audit

A = "1O6VRLTguA3Cb76k3U5refPd4Hiz7sBoK"
B = "1r5w-EWU3N47iz5p02NSOsmN-P7Kv7QJt"
U = f"https://drive.google.com/file/d/{A}/view"
V = f"https://drive.google.com/file/d/{B}/view"
VIDEO = "https://youtu.be/abc123"


class Request:
    def __init__(self, value):
        self.value = value

    def execute(self):
        if isinstance(self.value, Exception):
            raise self.value
        return self.value


class Drive:
    def __init__(self, public=True, missing=False, trashed=False, permissions_error=None):
        self.public, self.missing, self.trashed = public, missing, trashed
        self.permissions_error = permissions_error
        self.requests = []

    def files(self):
        return self

    def get(self, fileId, **kwargs):
        self.requests.append(fileId)
        return Request(FileNotFoundError(fileId) if self.missing else
                       {"id": fileId, "trashed": self.trashed})

    def permissions(self):
        return self

    def list(self, **kwargs):
        if self.permissions_error:
            return Request(self.permissions_error)
        return Request({"permissions": [{"type": "anyone" if self.public else "user",
                                         "role": "reader"}]})


def item(url=U, **kwargs):
    return {"published_url": url, **kwargs}


class InspectionTests(unittest.TestCase):
    def test_drive_public_passes_without_folder_or_checksum(self):
        drive = Drive()
        result = audit.audit({"guide": item(production_type="generated_pdf")}, service=drive)
        self.assertEqual(result["result"], audit.PASS)
        self.assertEqual(drive.requests, [A])

    def test_nonpublic_drive_fails(self):
        result = audit.audit({"x": item()}, service=Drive(public=False))
        self.assertEqual(result["result"], audit.FAIL)
        self.assertIn("permission", result["resources"][0]["issues"][0]["reason"])

    def test_inaccessible_drive_is_review_not_false_missing(self):
        result = audit.audit({"x": item()}, service=Drive(missing=True))
        self.assertEqual(result["result"], audit.REVIEW)

    def test_trashed_drive_fails(self):
        result = audit.audit({"x": item()}, service=Drive(trashed=True))
        self.assertEqual(result["result"], audit.FAIL)

    def test_permission_api_unavailable_requires_review(self):
        result = audit.audit({"x": item()}, service=Drive(permissions_error=PermissionError()))
        self.assertEqual(result["result"], audit.REVIEW)

    def test_external_urls_get_human_review_without_network(self):
        result = audit.audit({"video": item(VIDEO, human_review={VIDEO: "pending"})})
        self.assertEqual(result["result"], audit.REVIEW)
        self.assertIn(f"[Open resource]({VIDEO})", audit.summary_table(result))

    def test_approval_is_bound_to_exact_url(self):
        external = item(VIDEO, human_review={VIDEO: "reviewed"})
        self.assertEqual(audit.audit({"x": external})["result"], audit.PASS)
        external["published_url"] = VIDEO + "?changed=1"
        self.assertEqual(audit.audit({"x": external})["result"], audit.REVIEW)

    def test_external_drive_skips_permission_check(self):
        story = item(review_mode="human", human_review={U: "pending"})
        self.assertEqual(audit.audit({"story": story})["result"], audit.REVIEW)
        story["human_review"][U] = "reviewed"
        self.assertEqual(audit.audit({"story": story})["result"], audit.PASS)

    def test_human_review_does_not_hide_private_regular_drive_file(self):
        drive = Drive(public=False)
        record = item(human_review={U: "reviewed"})
        self.assertEqual(audit.audit({"worksheet": record}, service=drive)["result"], audit.FAIL)
        self.assertEqual(drive.requests, [A])

    def test_slide_holding_pdfs_are_never_inspected(self):
        drive = Drive(public=False)
        slide = item(type="slide_deck", pdf_url=V, holding_url=V,
                     human_review={U: "reviewed", V: "reviewed"})
        report = audit.audit({"slide": slide}, service=drive)
        self.assertEqual(report["resources"], [])
        self.assertEqual(drive.requests, [])

    def test_slide_exemption_does_not_skip_other_resources(self):
        slide = item("http://invalid", type="slide_deck", pdf_url=V)
        drive = Drive()
        report = audit.audit({"slide": slide, "second": item()}, service=drive)
        self.assertEqual(report["result"], audit.PASS)
        self.assertEqual(drive.requests, [A])
        self.assertEqual(len(report["resources"]), 1)

    def test_summary_only_issues(self):
        report = audit.audit({"pass": item(), "review": item(VIDEO)}, service=Drive())
        summary = audit.summary_table(report)
        self.assertNotIn("`pass`", summary)
        self.assertIn("`review`", summary)

    def test_pending_external_release_still_inspected(self):
        item_with_draft = item(holding_url=V, production_type="external")
        report = audit.audit({"x": item_with_draft}, service=Drive())
        self.assertEqual(len(report["resources"]), 1)
        self.assertEqual(report["result"], audit.PASS)

    def test_unpublished_skipped(self):
        self.assertEqual(audit.audit({"x": {"published_url": None, "url": VIDEO}})["resources"], [])


if __name__ == "__main__":
    unittest.main()
