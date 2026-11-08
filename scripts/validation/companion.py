"""Base contract shared by companion, activity-guide and option-overview sources."""
from publication_state import has_official_version


def validate(ctx, source, doc):
    resource_id = doc.get("resource_id")
    if not resource_id or resource_id not in ctx.registry:
        ctx.error(source, "companion missing registered resource ID")
    if "review_status" in doc or "preview_enabled" in doc:
        ctx.error(source, "resource status is derived from publication evidence")
    if not has_official_version(ctx.registry.get(resource_id)):
        ctx.warnings.append(f"{source.name}: unpublished companion; preview only")
