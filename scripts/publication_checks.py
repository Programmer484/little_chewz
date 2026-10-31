"""Deterministic gate for generated PDFs that link to catalogue resources.

The unpublished link is fine in a review PDF. Publishing requires every linked
resource to be recorded as published with an official URL. No Drive API needed.
"""
from select_builds import resource_refs


def unpublished_references(target: dict, registry: dict) -> list[str]:
    if target.get("kind") not in {"teacher_guide", "teacher_companion"}:
        return []  # Navigation renders unpublished references as Coming Soon.
    blocked = []
    for rid in sorted(resource_refs(target.get("data", {}))):
        record = registry.get(rid)
        if not record or record.get("status") != "published" or not record.get("published_url"):
            status = (record or {}).get("status", "missing")
            blocked.append(f"{rid} ({status})")
    return blocked
