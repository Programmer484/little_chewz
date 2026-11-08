"""Shared validation primitives; no resource-specific rules live here."""
from dataclasses import dataclass, field
from pathlib import Path
import json

from select_builds import resource_refs


@dataclass
class Context:
    root: Path
    registry: dict
    allowed_actions: set[str]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, source, message):
        self.errors.append(f"{source}: {message}")

    def warn(self, source, message):
        self.warnings.append(f"{source}: {message}")


def read_registry(root):
    """Read the catalogue, rejecting duplicate JSON keys at any depth."""
    duplicates = []

    def unique_pairs(pairs):
        seen = set()
        for key, _ in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        return dict(pairs)

    records = json.loads((root / "catalog/resources.json").read_text(),
                         object_pairs_hook=unique_pairs)
    if duplicates:
        raise ValueError(f"duplicate resource JSON keys: {sorted(set(duplicates))}")
    return records


def validate_references(ctx, source, data):
    """Check each nested resource ref once, regardless of source format."""
    for ref in sorted(resource_refs(data)):
        if ref not in ctx.registry:
            ctx.error(source, f"missing catalog resource ref {ref}")


def validate_quantity(ctx, source, link):
    """Teacher Guide print quantities have one shared definition."""
    if not isinstance(link, dict) or not link.get("ref"):
        return
    ref = link["ref"]
    quantity = link.get("quantity")
    record = ctx.registry.get(ref)
    if not isinstance(record, dict):
        return  # Missing refs are reported by validate_references.
    if record.get("type") == "student_material":
        if quantity not in ("per_student", "per_group"):
            ctx.error(source, f"worksheet {ref} must set quantity to per_student or per_group")
    elif quantity is not None:
        ctx.error(source, f"non-worksheet {ref} must not set quantity")
