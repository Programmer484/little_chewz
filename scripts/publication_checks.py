"""Release gate: every referenced resource needs a verified official destination."""
from select_builds import nav_refs, resource_refs
from publication_state import publication_status, has_official_version


def referenced_resources(target: dict | None) -> set[str]:
    """Registry IDs linked by a PDF source, including Welcome navigation rows."""
    if not target:
        return set()
    data = target.get("data", {})
    return resource_refs(data) | nav_refs(data)


def unpublished_references(target: dict, registry: dict) -> list[str]:
    if target.get("kind") not in {"teacher_guide", "teacher_companion", "welcome"}:
        return []
    blocked = []
    for rid in sorted(referenced_resources(target)):
        record = registry.get(rid)
        if not has_official_version(record):
            blocked.append(f"{rid} ({publication_status(record) if record is not None else 'missing'})")
    return blocked
