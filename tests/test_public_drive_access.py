"""Anonymous Drive proof must recognize actual bytes, not a login page."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from public_drive_access import anonymous_media_access

FILE_ID = "1wE3AovdpzAc5g_JtJhzkvw7Wa_DI1xFk"


class FakeResponse:
    def __init__(self, data=b"ID3\x04\x00\x00", content_type="audio/mpeg",
                 status=206, url="https://drive.usercontent.google.com/download"):
        self.body = data
        self.headers = {"Content-Type": content_type}
        self.status = status
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def geturl(self):
        return self.url

    def read(self, count):
        return self.body[:count]


class AccessProofTests(unittest.TestCase):
    def test_public_mp3_bytes_prove_anonymous_access(self):
        opened = Mock(return_value=FakeResponse())
        verified, message = anonymous_media_access(FILE_ID, "audio/mpeg", opener=opened)
        self.assertTrue(verified)
        self.assertIn("verified", message)
        request = opened.call_args.args[0]
        self.assertIn(FILE_ID, request.full_url)
        self.assertNotIn("Authorization", request.headers)

    def test_login_page_is_not_a_pass_even_with_http_200(self):
        opened = lambda *_args, **_kwargs: FakeResponse(
            b"<html>Sign in</html>", "text/html", status=200
        )
        self.assertFalse(anonymous_media_access(FILE_ID, "audio/mpeg", opener=opened)[0])

    def test_unknown_host_is_not_a_pass(self):
        opened = lambda *_args, **_kwargs: FakeResponse(
            url="https://unknown.example.com/content"
        )
        self.assertFalse(anonymous_media_access(FILE_ID, "audio/mpeg", opener=opened)[0])

    def test_unhandled_native_docs_are_inconclusive_not_private(self):
        opened = Mock()
        verified, _ = anonymous_media_access(
            FILE_ID, "application/vnd.google-apps.document", opener=opened
        )
        self.assertFalse(verified)
        opened.assert_not_called()

    def test_pdf_magic_must_match(self):
        opened = lambda *_args, **_kwargs: FakeResponse(
            b"%PDF-1.7", "application/pdf"
        )
        self.assertTrue(anonymous_media_access(FILE_ID, "application/pdf", opener=opened)[0])
        opened2 = lambda *_args, **_kwargs: FakeResponse(
            b"Not a PDF", "application/pdf"
        )
        self.assertFalse(anonymous_media_access(FILE_ID, "application/pdf", opener=opened2)[0])


if __name__ == "__main__":
    unittest.main()
