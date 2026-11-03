"""Inspector tests: Drive permissions and URL-specific human approval."""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

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

    def test_published_slides_use_same_drive_check_as_other_resources(self):
        drive = Drive(public=False)
        slides_url = f"https://docs.google.com/presentation/d/{A}/edit"
        slide = item(slides_url, type="slides", pdf_url=V, holding_url=V,
                     human_review={slides_url: "reviewed"})
        report = audit.audit({"slide": slide}, service=drive)
        self.assertEqual(report["result"], audit.FAIL)
        self.assertEqual(len(report["resources"]), 1)
        self.assertEqual(drive.requests, [A])  # Only the published presentation; not its source PDF.

    def test_unpublished_slides_still_skipped(self):
        drive = Drive()
        slide = {"type": "slide_deck", "published_url": None, "pdf_url": V}
        report = audit.audit({"slide": slide, "second": item()}, service=drive)
        self.assertEqual(report["result"], audit.PASS)
        self.assertEqual(drive.requests, [A])
        self.assertEqual(len(report["resources"]), 1)

    def test_drive_api_exception_logged_separately_without_raw_error_body(self):
        drive = Drive(permissions_error=PermissionError("sensitive details should not leak"))
        report = audit.audit({"worksheet": item()}, service=drive)
        self.assertEqual(report["result"], audit.REVIEW)
        self.assertEqual(len(report["diagnostics"]), 1)
        self.assertIn("operation=permissions.list", report["diagnostics"][0])
        self.assertIn("exception=PermissionError", report["diagnostics"][0])
        self.assertNotIn("sensitive details", str(report))
        self.assertNotIn("exception=", audit.summary_table(report))

    def test_diagnostic_retains_safe_http_status_and_reason(self):
        class GoogleError(Exception):
            resp = type("Response", (), {"status": 403})()
            content = b'{"error":{"errors":[{"reason":"insufficientPermissions"}]}}'
        report = audit.audit({"worksheet": item()}, service=Drive(permissions_error=GoogleError()))
        self.assertEqual(report["result"], audit.REVIEW)
        self.assertIn("http_status=403", report["diagnostics"][0])
        self.assertIn("api_reason=insufficientPermissions", report["diagnostics"][0])

    def test_cli_writes_diagnostic_artifact_without_echoing_exception(self):
        drive = Drive(permissions_error=PermissionError("PRIVATE-TOKEN"))
        with tempfile.TemporaryDirectory() as temp:
            report_path = Path(temp) / "inspection-report.json"
            output = io.StringIO()
            with (patch.object(audit, "load_registry", return_value={"x": item()}),
                  patch.object(audit, "drive_service", return_value=drive),
                  patch.object(sys, "argv", ["inspector", "--report", str(report_path)]),
                  redirect_stdout(output)):
                with self.assertRaises(SystemExit) as stopped:
                    audit.main()
            self.assertEqual(stopped.exception.code, 0)  # NEEDS REVIEW is not a confirmed FAIL.
            diagnostics = report_path.with_suffix(".txt").read_text()
            self.assertIn("operation=permissions.list", diagnostics)
            self.assertNotIn("PRIVATE-TOKEN", diagnostics)
            self.assertNotIn("operation=permissions.list", output.getvalue())

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
