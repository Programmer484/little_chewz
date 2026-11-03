"""Derive each resource's publication state from its publication evidence.

Only generated PDFs use source/approved MD5 comparisons. Every other resource
uses its current official and genuinely distinct holding destinations.
Missing checksums are not evidence of equality: auditing reports them separately.
"""
from __future__ import annotations

from urllib.parse import urlsplit


def identity(url: str | None) -> str | None:
    if not url:
        return None
    p = urlsplit(url)
    if p.hostname in {"drive.google.com", "docs.google.com"}:
        parts = p.path.split("/")
        for marker in ("d", "folders"):
            if marker in parts:
                i = parts.index(marker) + 1
                if i < len(parts) and parts[i]:
                    return "drive:" + parts[i]
    # For external sites a changed query can actually identify a new media file.
    return (p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), p.query)


def has_official_version(resource: dict | None) -> bool:
    return bool(resource and resource.get("published_url"))


def publication_status(resource: dict | None, current_md5: str | None = None) -> str:
    if not has_official_version(resource):
        return "unpublished"
    if resource.get("production_type") == "generated_pdf":
        approved = (resource.get("publication") or {}).get("artifact_md5")
        if approved and current_md5 and current_md5 != approved:
            return "pending_publish"
    else:
        holding = identity(resource.get("holding_url"))
        published = identity(resource.get("published_url"))
        if holding is not None and holding != published:
            return "pending_publish"
    return "published"
