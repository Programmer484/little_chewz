"""Select official URLs for any released resource; draft links are preview-only."""
def resolve_url(record: dict, release: bool = False) -> str | None:
    if release:
        return record.get("published_url")
    # Staging previews show the currently proposed resource, not stale live bytes.
    return record.get("holding_url") or record.get("published_url")


def resolved_registry(registry: dict, release: bool = False) -> dict:
    return {rid: {**record, "url": resolve_url(record, release)}
            for rid, record in registry.items()}
