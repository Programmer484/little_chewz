"""Choose Drive URLs for review PDFs versus approved release PDFs.

Drive file IDs and links remain stable when moving the same file from holding to
its official folder. Status—not URL string inequality—is the release boundary.
"""


def resolve_url(record: dict, release: bool = False) -> str | None:
    if release:
        return record.get("published_url") if record.get("status") == "published" else None
    return record.get("holding_url") or record.get("published_url") or record.get("url")


def resolved_registry(registry: dict, release: bool = False) -> dict:
    return {rid: {**record, "url": resolve_url(record, release)}
            for rid, record in registry.items()}
