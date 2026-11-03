"""Release gate: published guide dependencies must have an official destination."""
from select_builds import resource_refs
from publication_state import publication_status, has_official_version


def unpublished_references(target: dict, registry: dict) -> list[str]:
    if target.get("kind") not in {"teacher_guide", "teacher_companion"}:
        return []
    blocked = []
    for rid in sorted(resource_refs(target.get("data", {}))):
        record = registry.get(rid)
        if not has_official_version(record):
            blocked.append(f"{rid} ({publication_status(record) if record else 'missing'})")
    return blocked
