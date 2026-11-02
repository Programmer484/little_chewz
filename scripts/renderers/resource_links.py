"""Resolve resource links from the catalogue.

Published resources always use their official published_url, in previews and
releases alike. Draft preview links may use a genuine holding file; a release
never links to unpublished resources.
"""


def resolve_url(record: dict, release: bool = False) -> str | None:
    if record.get("status") == "published":
        # Never silently substitute a holding or legacy link for a published one.
        return record.get("published_url")
    if release:
        return None
    return record.get("holding_url") or record.get("published_url") or record.get("url")


def resolved_registry(registry: dict, release: bool = False) -> dict:
    return {rid: {**record, "url": resolve_url(record, release)}
            for rid, record in registry.items()}
