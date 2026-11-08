"""Orchestrate repository checks and dispatch per-source validation by template.

The routing table is authoritative: a Celebrate lesson runs Teacher Guide +
Celebrate only, while Welcome and companion types never inherit guide checks.
"""
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
import json

from select_builds import targets, generated_outputs, resource_refs
from publication_state import has_official_version
from . import catalog
from .common import Context, read_registry, validate_references


@dataclass(frozen=True)
class Rule:
    owner: str
    renderer: str
    checks: tuple


RULES = {
    "teacher_guide": Rule("lesson", "teacher_guide", ("teacher_guide",)),
    "celebrate": Rule("lesson", "celebrate", ("teacher_guide", "celebrate")),
    "teacher_companion": Rule("companion", "teacher_companion", ("companion",)),
    "activity_guide": Rule("companion", "teacher_companion", ("companion", "activity_guide")),
    "option_overview": Rule("companion", "teacher_companion", ("companion",)),
    "welcome": Rule("standalone", "welcome", ("welcome",)),
}
BASE_CHECKS = {
    "lesson": ("teacher_guide",),
    "companion": ("companion",),
    "standalone": ("welcome",),
}


def validate_source(ctx, source, doc, owner):
    """One recursive ref pass + only the validators relevant to this resource."""
    validate_references(ctx, source, doc)
    template = doc.get("template")
    rule = RULES.get(template)
    if rule is None or not (ctx.root / "templates" / str(template) / "TEMPLATE.json").is_file():
        ctx.error(source, f'must declare "template" naming a folder in templates/ (one of {sorted(RULES)})')
        checks = BASE_CHECKS[owner]
    elif rule.owner != owner:
        ctx.error(source, f"template {template!r} cannot be used for {owner} sources")
        checks = BASE_CHECKS[owner]
    else:
        checks = rule.checks
    for module_name in checks:
        import_module(f"validation.{module_name}").validate(ctx, source, doc)


def validate_quest_manifests(ctx, guide_outputs):
    quest_index = json.loads((ctx.root / "catalog/quests.json").read_text())
    for school in quest_index["school_index"]:
        quest_path = ctx.root / school["quest_manifest"]
        quest = json.loads(quest_path.read_text())
        for lesson in quest["learning_sequence"]:
            extra = set(lesson) - {"folder", "title"}
            if extra:
                ctx.error(quest_path, f'lesson {lesson["folder"]} has unexpected metadata fields {sorted(extra)}')
            folder = quest_path.parent / "lessons" / lesson["folder"]
            guide_id = guide_outputs.get(f'{lesson["folder"]}-teacher-guide.pdf')
            if (guide_id and has_official_version(ctx.registry.get(guide_id))
                    and not (folder / "lesson.json").is_file()):
                ctx.error(folder, "published Teacher Guide has no lesson.json")


def validate_templates(ctx):
    """Validate starter structures without applying live-resource registration rules."""
    for folder in sorted(p for p in (ctx.root / "templates").glob("*")
                         if (p / "TEMPLATE.json").is_file()):
        path = folder.relative_to(ctx.root) / "TEMPLATE.json"
        doc = json.loads((ctx.root / path).read_text())
        if folder.name not in RULES:
            ctx.error(path, f"template folder {folder.name!r} has no validator in RULES")
            continue
        if doc.get("template") != folder.name:
            ctx.error(path, f'must declare "template": "{folder.name}"')
        if folder.name == "activity_guide":
            "activity_guide"(ctx, path, doc)


def validate_pdf_targets(ctx):
    """Validate registered build targets, not source structure a second time."""
    try:
        registered = targets()
        for name, target in registered.items():
            template = target["data"].get("template")
            rule = RULES.get(template)
            record = ctx.registry.get(target.get("resource_id")) or {}
            renderer = (record.get("pdf") or {}).get("renderer")
            if rule and rule.renderer != renderer:
                ctx.error(target["source"],
                          f"template {template!r} is built by {rule.renderer!r}, but the catalogue says pdf.renderer {renderer!r}")
            for ref in sorted(resource_refs(target["data"])):
                record = ctx.registry.get(ref)
                if not isinstance(record, dict):
                    continue  # The single shared ref pass reports missing IDs.
                url = record.get("published_url") or record.get("holding_url") or ""
                if not str(url).startswith("https://"):
                    if has_official_version(record):
                        ctx.error(name, f"invalid published HTTPS destination for {ref}")
                    else:
                        ctx.warn(name, f"{ref} has no published/staged link; draft preview is unlinked")
                elif not has_official_version(record):
                    ctx.warn(name, f"{ref} has no official URL; preview only")
    except (ValueError, KeyError, OSError) as exc:
        ctx.errors.append(f"PDF registration/eligibility: {exc}")


def run(root):
    """Collect messages without writing files or touching external services."""
    root = Path(root).resolve()
    registry = read_registry(root)
    actions = json.loads((root / "system/action_labels.json").read_text())
    ctx = Context(root, registry, set(actions["teacher_guide_actions"] + actions["internal_row_types"]))
    catalog.validate_resources(ctx)
    catalog.validate_drive_folders(ctx)

    try:
        guide_outputs = generated_outputs(registry)
        validate_quest_manifests(ctx, guide_outputs)
    except (ValueError, KeyError, OSError) as exc:
        ctx.errors.append(f"Quest/guide registration: {exc}")

    lesson_paths = sorted(root.glob("content/**/lessons/**/lesson.json"))
    companion_paths = sorted(root.glob("content/**/resources/**/*.json"))
    checked = set()
    for owner, paths in (("lesson", lesson_paths), ("companion", companion_paths)):
        for source in paths:
            validate_source(ctx, source, json.loads(source.read_text()), owner)
            checked.add(source.resolve())

    for source in root.glob("content/**/story/*.md"):
        if not source.read_text().startswith("---\n"):
            ctx.error(source, "missing story frontmatter")

    # Standalone generated sources (normally Welcome) are not lesson or companion files.
    for ref, resource in registry.items():
        if not isinstance(resource, dict):
            continue
        build = resource.get("pdf") or {}
        if not isinstance(build, dict) or not build.get("source"):
            continue
        renderer = build.get("renderer")
        if (renderer not in catalog.PDF_RENDERERS
                or not (root / f"scripts/renderers/{renderer}.py").is_file()):
            ctx.error(ref, f"unknown PDF renderer {renderer}")
            continue
        if not isinstance(build["source"], str):
            continue  # Invalid source type is reported by catalogue validation.
        source = root / build["source"]
        if not source.is_file():
            continue  # Reported by catalogue source-path validation.
        if source.resolve() not in checked:
            validate_source(ctx, source, json.loads(source.read_text()), "standalone")
            checked.add(source.resolve())

    validate_templates(ctx)
    validate_pdf_targets(ctx)
    return ctx, len(lesson_paths), len(companion_paths)
