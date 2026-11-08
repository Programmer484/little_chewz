"""Shared Teacher Guide structure; Celebrate composes this with its own validator."""
from .common import validate_quantity

REQUIRED = ("key", "goal", "steps", "outcomes", "cover")
OBSOLETE = {"review_status", "preview_enabled", "status", "holding_url", "published_url"}
OPTION_LABELS = {"A", "B", "C", "D"}


def validate(ctx, source, doc):
    if set(doc) & OBSOLETE:
        ctx.error(source, "obsolete lesson publication/preview fields")
    if "output" in doc:
        ctx.error(source, "lesson output is obsolete; use catalog/resources.json pdf.output")
    for key in REQUIRED:
        if key not in doc:
            ctx.error(source, f"missing {key}")
    cover = source.parent / doc.get("cover", "")
    if not cover.is_file():
        ctx.error(source, f"missing visual cover {cover.name}")

    for section in ("core", "optional_prep", "bonuses"):
        for item in doc.get(section, []):
            validate_quantity(ctx, source, item)

    # Bonuses can expose student printouts that differ from the linked companion.
    for bonus in doc.get("bonuses", []):
        materials = bonus.get("print_materials", [])
        if not isinstance(materials, list):
            ctx.error(source, "bonus print_materials must be a list")
            continue
        seen = set()
        for material in materials:
            if not isinstance(material, dict) or not isinstance(material.get("ref"), str):
                ctx.error(source, "bonus print_materials needs resource objects with ref")
                continue
            ref = material["ref"]
            if set(material) - {"ref", "quantity", "description"}:
                ctx.error(source, f"bonus print_materials has unsupported metadata for {ref}")
            if ref in seen:
                ctx.error(source, f"duplicate bonus print material {ref}")
            seen.add(ref)
            record = ctx.registry.get(ref)
            if isinstance(record, dict) and record.get("type") != "student_material":
                ctx.error(source, f"bonus print material {ref} must be student_material")
            validate_quantity(ctx, source, material)

    ids = []
    for step in doc.get("steps", []):
        ids.append(step.get("id"))
        options = step.get("options", [])
        if options and doc.get("flow_style") != "compact":
            ctx.error(source, "structured options require flow_style: compact")
        labels = [option.get("label") for option in options]
        if (any(not isinstance(label, str) or label not in OPTION_LABELS for label in labels)
                or len(labels) != len(set(labels))):
            ctx.error(source, "option labels must be unique A/B/C/D")
        for option in options:
            if not option.get("title") or not option.get("rows"):
                ctx.error(source, "option must have a title and rows")
            size = option.get("group_size")
            if size is not None and (type(size) is not int or not 1 <= size <= 200):
                ctx.error(source, "option group_size must be a whole number of students from 1 to 200")

        for unit in [step, *options]:
            rows = unit.get("rows", [])
            kinds = [row.get("kind", "").upper() for row in rows]
            if "MORE" in kinds and any(kind != "MORE" for kind in kinds[kinds.index("MORE"):]):
                ctx.error(source, f'step {step.get("id")}: MORE rows must come last')
            for row in rows:
                validate_quantity(ctx, source, row)
                for link in row.get("links", []):
                    validate_quantity(ctx, source, link)
                kind = row.get("kind", "").upper()
                if kind not in ctx.allowed_actions:
                    ctx.error(source, f"unsupported action label {kind}")

    if doc.get("bonus_rows") and doc.get("bonuses"):
        ctx.error(source, "choose bonus_rows or bonuses, not both")
    for row in doc.get("bonus_rows", []):
        validate_quantity(ctx, source, row)
        for link in row.get("links", []):
            validate_quantity(ctx, source, link)
        kind = row.get("kind", "").upper()
        if kind not in ctx.allowed_actions:
            ctx.error(source, f"unsupported bonus action label {kind}")

    if ids != list(range(1, len(ids) + 1)):
        ctx.error(source, "step IDs not consecutive")
    if len(doc.get("outcomes", [])) != 3:
        ctx.warn(source, "guide convention normally uses three outcomes")
