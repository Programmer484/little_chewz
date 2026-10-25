"""Publication inspection never treats holding copies as live destinations."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inspect_publications as inspect

ID = "1w-es-VamWXMfCrr34pRbq59a3ASngEbL"


class Request:
    def __init__(self, meta): self.meta = meta
    def execute(self): return self.meta


class Service:
    def __init__(self, md5="0" * 32, version="5"):
        self.meta = {"id": ID, "name": "Example.pdf", "mimeType": "application/pdf",
                     "md5Checksum": md5, "version": version}
    def files(self): return self
    def get(self, **kwargs): return Request(self.meta)


class InspectTests(unittest.TestCase):
    def test_holding_only_is_not_published(self):
        item = {"production_type": "external", "status": "unpublished",
                "holding_url": "https://drive.google.com/file/d/" + ID + "/view",
                "published_url": None}
        result = inspect.inspect_one("demo", item, service=Service())
        self.assertEqual(result["result"], "unpublished")
        self.assertTrue(result["holding_present"])

    def test_external_is_metadata_only_even_after_agent_confirmation(self):
        item = {"production_type": "external", "status": "published",
                "published_url": "https://drive.google.com/file/d/" + ID + "/view",
                "publication": {"verification": "verified", "drive_file_id": ID,
                                "drive_version": "5"}}
        result = inspect.inspect_one("demo", item, service=Service())
        self.assertEqual(result["result"], "verified_metadata_only")
        self.assertEqual(result["content_parity"], "unverified")

    def test_generated_drive_digest_mismatch(self):
        item = {"production_type": "generated_pdf", "status": "published",
                "published_url": "https://drive.google.com/file/d/" + ID + "/view",
                "publication": {"verification": "verified", "drive_file_id": ID,
                                "artifact_md5": "a" * 32}}
        result = inspect.inspect_one("demo", item, service=Service(md5="b" * 32))
        self.assertEqual(result["result"], "discrepancy")

    def test_unverified_historical_published_entry_does_not_claim_digest(self):
        item = {"production_type": "generated_pdf", "status": "published",
                "published_url": "https://drive.google.com/file/d/" + ID + "/view",
                "publication": {"verification": "unverified"}}
        result = inspect.inspect_one("demo", item, service=Service())
        self.assertEqual(result["result"], "unverified")


if __name__ == "__main__":
    unittest.main()
