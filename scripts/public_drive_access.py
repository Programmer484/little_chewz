"""Strict positive proof of anonymous access to raw Google Drive media.

The check never uses Google credentials, sends cookies, or trusts an HTTP 200
alone. It is intentionally limited to supported binary formats; an
inconclusive result must NOT be treated as evidence that a file is private.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from urllib.parse import urlencode, urlsplit

FILE_ID = re.compile(r"^[A-Za-z0-9_-]{20,}$")
GOOGLE_HOSTS = {"drive.usercontent.google.com", "drive.google.com"}
MIME_SIGNATURES = {
    "application/pdf": lambda b: b.startswith(b"%PDF"),
    "audio/mpeg": lambda b: b.startswith(b"ID3") or (
        len(b) >= 2 and b[0] == 0xff and b[1] & 0xe0 == 0xe0
    ),
    "image/png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
    "image/jpeg": lambda b: b.startswith(b"\xff\xd8\xff"),
    "image/gif": lambda b: b.startswith((b"GIF87a", b"GIF89a")),
    "image/webp": lambda b: b.startswith(b"RIFF") and b[8:12] == b"WEBP",
    "audio/wav": lambda b: b.startswith(b"RIFF") and b[8:12] == b"WAVE",
    "application/zip": lambda b: b.startswith(b"PK\x03\x04"),
    "video/mp4": lambda b: len(b) >= 12 and b[4:8] == b"ftyp",
}


def anonymous_media_access(file_id: str, mime_type: str | None,
                           opener=None) -> tuple[bool, str]:
    """Prove a known file's real bytes are available without authorization.

    Only a positive response with a recognized signature counts. Unsupported
    MIME types, permission prompts, throttling, errors and login pages are
    inconclusive and must go through the existing manual-review fallback.
    """
    mime = (mime_type or "").lower().split(";", 1)[0].strip()
    if not FILE_ID.fullmatch(file_id):
        return False, "Invalid file ID"
    if mime not in MIME_SIGNATURES:
        return False, "No safe public-media check for this file type"
    url = "https://drive.usercontent.google.com/download?" + urlencode(
        {"id": file_id, "export": "download"}
    )
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-4095"}
    )
    try:
        op = opener or urllib.request.urlopen
        with op(request, timeout=12) as response:
            code = response.status
            final_url = response.geturl()
            final_host = urlsplit(final_url).hostname
            if code not in (200, 206) or final_host not in GOOGLE_HOSTS:
                return False, "No confirmed response from an approved Google host"
            content_type = response.headers.get("Content-Type", "").lower().split(";", 1)[0]
            if content_type not in {mime, "application/octet-stream"}:
                return False, "Response did not contain the expected media type"
            prefix = response.read(4096)
            if not MIME_SIGNATURES[mime](prefix):
                return False, "Media bytes did not match the expected file type"
            return True, "Anonymous media bytes verified"
    except (OSError, ValueError, urllib.error.URLError) as exc:
        # Do not include the URL, cookies, raw body or request headers.
        return False, f"Anonymous media check inconclusive ({type(exc).__name__})"
