"""Resolve stable catalogue dependencies for publication and audit.

Generated PDF references come from their authoritative JSON sources; external
files may declare catalogue `dependencies` because PDF hyperlink parsing is
not a reliable semantic source of truth.
"""
from select_builds import nav_refs, resource_refs
from publication_state import publication_status, has_official_version


def referenced_resources(target: dict | None) -> set[str]:
    if not target:
        return set()
    data = target.get("data", {})
    return resource_refs(data) | nav_refs(data)


def dependency_ids(resource_id: str, registry: dict, source_targets=None) -> set[str]:
    record = registry.get(resource_id)
    if record is None:
        raise ValueError(f"Unknown resource: {resource_id}")
    explicit = record.get("dependencies") or []
    if not isinstance(explicit, list):
        raise ValueError(f"{resource_id}: dependencies must be a list")
    refs = set(explicit)
    if len(refs) != len(explicit) or not all(isinstance(x, str) for x in explicit):
        raise ValueError(f"{resource_id}: invalid or duplicate dependencies")
    pdf = record.get("pdf") or {}
    output = pdf.get("output") or (f"{resource_id}.pdf" if pdf.get("source") else None)
    if output:
        if source_targets is None:
            from select_builds import targets
            source_targets = targets()
        target = source_targets.get(output)
        if target is None:
            raise ValueError(f"{resource_id}: generated source mapping missing: {output}")
        refs |= referenced_resources(target)
    if resource_id in refs:
        raise ValueError(f"{resource_id}: cannot depend on itself")
    return refs


def unpublished_dependencies(resource_id: str, registry: dict, source_targets=None) -> list[str]:
    """Full resource IDs that must become published before this parent can publish."""
    return sorted(ref for ref in dependency_ids(resource_id, registry, source_targets)
                  if not has_official_version(registry.get(ref)))


def unpublished_references(target: dict, registry: dict) -> list[str]:
    """Backwards-compatible generated-source check with human-friendly details."""
    if target.get("kind") not in {"teacher_guide", "teacher_companion", "welcome"}:
        return []
    return [f"{rid} ({publication_status(registry.get(rid)) if rid in registry else 'missing'})"
            for rid in sorted(referenced_resources(target))
            if not has_official_version(registry.get(rid))]
