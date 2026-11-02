"""Read-only inspection detects Trash and sharing gaps without false assurance."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inspect_publications as inspect

ID = "1w-es-VamWXMfCrr34pRbq59a3ASngEbL"
PUBLIC = [{"type": "anyone", "role": "reader"}]
PRIVATE = [{"type": "user", "role": "reader"}]


class Request:
    def __init__(self, response=None, error=None):
        self.response, self.error = response, error

    def execute(self):
        if self.error:
            raise self.error
        return self.response


class Service:
    def __init__(self, md5="0" * 32, version="5", trashed=False,
                 permissions=None, permission_error=None, omit_trashed=False,
                 permission_pages=None):
        self.meta = {"id": ID, "name": "Example.pdf", "mimeType": "application/pdf",
                     "md5Checksum": md5, "version": version}
        if not omit_trashed:
            self.meta["trashed"] = trashed
        self.permission_pages = permission_pages
        self.permission_records = PUBLIC if permissions is None else permissions
        self.permission_error = permission_error
        self.request_fields = []
        self.permission_list_calls = []

    def files(self):
        return self

    def get(self, **kwargs):
        self.request_fields.append(kwargs.get("fields", ""))
        return Request(self.meta)

    def permissions(self):
        return self

    def list(self, **kwargs):
        self.permission_list_calls.append(kwargs)
        if self.permission_error:
            return Request(error=self.permission_error)
        if self.permission_pages is not None:
            page = 0 if not kwargs.get("pageToken") else int(kwargs["pageToken"])
            result = {"permissions": self.permission_pages[page]}
            if page + 1 < len(self.permission_pages):
                result["nextPageToken"] = str(page + 1)
            return Request(result)
        return Request({"permissions": self.permission_records})


def external(verification="verified"):
    return {"production_type": "external", "status": "published",
            "published_url": "https://drive.google.com/file/d/" + ID + "/view",
            "publication": {"verification": verification, "drive_file_id": ID,
                            "drive_version": "5"}}


def generated():
    return {"production_type": "generated_pdf", "status": "published",
            "published_url": "https://drive.google.com/file/d/" + ID + "/view",
            "publication": {"verification": "verified", "drive_file_id": ID,
                            "artifact_md5": "a" * 32}}


class InspectTests(unittest.TestCase):
    def test_external_is_metadata_only_even_after_agent_confirmation(self):
        service = Service()
        result = inspect.inspect_one("demo", external(), service=service)
        self.assertEqual(result["result"], "verified_metadata_only")
        self.assertEqual(result["content_parity"], "unverified")
        self.assertEqual(result["trash_status"], "not_trashed")
        self.assertEqual(result["sharing_status"], "anyone_reader")
        self.assertIn("trashed", service.request_fields[0])
        self.assertTrue(service.permission_list_calls[0]["supportsAllDrives"])

    def test_generated_drive_digest_mismatch(self):
        result = inspect.inspect_one("demo", generated(), service=Service(md5="b" * 32))
        self.assertEqual(result["result"], "discrepancy")

    def test_trashed_external_file_is_a_discrepancy(self):
        result = inspect.inspect_one("demo", external(), service=Service(trashed=True))
        self.assertEqual(result["result"], "discrepancy")
        self.assertEqual(result["trash_status"], "trashed")
        self.assertIn("Trash", " ".join(result["observations"]))

    def test_trashed_generated_file_is_a_discrepancy(self):
        result = inspect.inspect_one("demo", generated(),
                                     service=Service(md5="b" * 32, trashed=True))
        self.assertEqual(result["result"], "discrepancy")
        self.assertEqual(result["trash_status"], "trashed")

    def test_private_sharing_is_flagged_not_counted_as_public(self):
        result = inspect.inspect_one("demo", external(),
                                     service=Service(permissions=PRIVATE))
        self.assertEqual(result["result"], "discrepancy")
        self.assertEqual(result["sharing_status"], "restricted")

    def test_anonymous_commenter_access_counts_as_reader(self):
        result = inspect.inspect_one("demo", external(),
                                     service=Service(permissions=[{"type": "anyone",
                                                                    "role": "commenter"}]))
        self.assertEqual(result["result"], "verified_metadata_only")
        self.assertEqual(result["sharing_status"], "anyone_reader")

    def test_inherited_anyone_reader_permission_is_recognized(self):
        inherited = [{"type": "anyone", "role": "reader",
                      "permissionDetails": [{"inherited": True}]}]
        result = inspect.inspect_one("demo", external(),
                                     service=Service(permissions=inherited))
        self.assertEqual(result["sharing_status"], "anyone_reader")

    def test_permissions_pagination_checks_later_pages(self):
        service = Service(permission_pages=[PRIVATE, PUBLIC])
        result = inspect.inspect_one("demo", external(), service=service)
        self.assertEqual(result["sharing_status"], "anyone_reader")
        self.assertEqual(len(service.permission_list_calls), 2)

    def test_permission_lookup_failure_is_unverified_not_restricted(self):
        result = inspect.inspect_one("demo", external(),
                                     service=Service(permission_error=PermissionError("403")))
        self.assertEqual(result["result"], "unverified")
        self.assertEqual(result["sharing_status"], "unverified")
        self.assertEqual(result["trash_status"], "not_trashed")

    def test_missing_trash_status_is_unverified_not_safe(self):
        result = inspect.inspect_one("demo", external(),
                                     service=Service(omit_trashed=True))
        self.assertEqual(result["result"], "unverified")
        self.assertEqual(result["trash_status"], "unverified")

    def test_empty_permission_response_is_unverified_not_restricted(self):
        class NoPermissions(Service):
            def list(self, **kwargs):
                return Request({})
        result = inspect.inspect_one("demo", external(), service=NoPermissions())
        self.assertEqual(result["result"], "unverified")
        self.assertEqual(result["sharing_status"], "unverified")

    def test_existing_digest_discrepancy_survives_permission_failure(self):
        result = inspect.inspect_one("demo", generated(),
                                     service=Service(md5="b" * 32,
                                                     permission_error=PermissionError("403")))
        self.assertEqual(result["result"], "discrepancy")
        self.assertEqual(result["sharing_status"], "unverified")

    def test_external_non_drive_provider_cannot_be_checked(self):
        item = external()
        item["published_url"] = "https://example.org/resource"
        result = inspect.inspect_one("demo", item, service=Service())
        self.assertEqual(result["result"], "unverified")
        self.assertEqual(result["trash_status"], "not_checked")
        self.assertEqual(result["sharing_status"], "not_checked")


if __name__ == "__main__":
    unittest.main()
