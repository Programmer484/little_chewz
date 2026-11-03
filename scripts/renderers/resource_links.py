"""Select official URLs for any released resource; draft links are preview-only."""
from publication_state import has_official_version


def resolve_url(record: dict, release: bool = False) -> str | None:
    if has_official_version(record):
        return record["published_url"]
    if release:
        return None
    # Legacy url preserves old draft pointers without making them "published".
    return record.get("holding_url") or record.get("url")


def resolved_registry(registry: dict, release: bool = False) -> dict:
    return {rid: {**record, "url": resolve_url(record, release)}
            for rid, record in registry.items()}
