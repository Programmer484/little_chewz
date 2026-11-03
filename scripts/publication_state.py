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



def status_report(registry: dict, *, only: str | None = None, builder=None) -> list[dict]:
    """Build generated PDFs on demand to calculate current source-vs-approved parity.

    Never writes to the catalogue or Drive. An unavailable checksum is a
    verification limitation, not proof of a pending change.
    """
    from hashlib import md5
    from pathlib import Path
    if only and only not in registry:
        raise ValueError("Unknown resource: " + only)
    result = []
    for rid, resource in registry.items():
        if only and rid != only:
            continue
        status = publication_status(resource)
        item = {"resource_id": rid, "status": status}
        if resource.get("production_type") == "generated_pdf" and has_official_version(resource):
            approved = (resource.get("publication") or {}).get("artifact_md5")
            if not approved:
                item["checksum_evidence"] = "NEEDS REVIEW: approved MD5 unavailable"
            else:
                try:
                    if builder is None:
                        from publish_to_drive import build_pdf
                        source = build_pdf(rid, resource["build"])
                    else:
                        source = builder(rid, resource["build"])
                    actual = md5(Path(source).read_bytes()).hexdigest()
                    item["status"] = publication_status(resource, actual)
                    item["checksum_evidence"] = "match" if actual == approved else "changed"
                except Exception as exc:
                    item["checksum_evidence"] = "NEEDS REVIEW: " + str(exc)
        result.append(item)
    return result


if __name__ == "__main__":
    import argparse
    import json
    from publish_to_drive import load_registry

    parser = argparse.ArgumentParser(description="Derived publication status; read-only")
    parser.add_argument("--resource-id")
    args = parser.parse_args()
    print(json.dumps(status_report(load_registry(), only=args.resource_id), indent=2))
