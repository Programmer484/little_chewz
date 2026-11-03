"""Select official URLs for any released resource; draft links are preview-only."""
def resolve_url(record: dict, release: bool = False) -> str | None:
    if record.get("published_url"):
        return record["published_url"]
    if release:
        return None
    # Legacy url preserves old draft pointers without making them "published".
    return record.get("holding_url")


def resolved_registry(registry: dict, release: bool = False) -> dict:
    return {rid: {**record, "url": resolve_url(record, release)}
            for rid, record in registry.items()}
