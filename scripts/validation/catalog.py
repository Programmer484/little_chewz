"""Catalogue and local Drive-folder configuration checks (no API calls)."""
from pathlib import Path
import json
import re

FOLDERS = {"welcome", "teacher_guide", "classroom_slides",
           "student_material", "teacher_resource"}
PDF_RENDERERS = {"teacher_guide": "teacher_guide",
                 "teacher_companion": "teacher_resource",
                 "welcome": "welcome", "celebrate": "teacher_guide"}
RESOURCE_FIELDS = {"title", "type", "published_url", "holding_url", "pdf",
                   "pdf_url", "human_reviewed_url", "print", "dependencies"}
PDF_FIELDS = {"renderer", "output", "source", "approved_md5", "revision"}


def validate_resources(ctx):
    registry = ctx.registry
    for ref, item in registry.items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ref):
            ctx.error(ref, "resource ID must be stable lowercase kebab-case")
        if not isinstance(item, dict):
            ctx.error(ref, "resource entry must be an object")
            continue
        unknown = set(item) - RESOURCE_FIELDS
        if unknown:
            ctx.error(ref, f"obsolete or unknown metadata fields {sorted(unknown)}")
        if not isinstance(item.get("title"), str) or not item["title"]:
            ctx.error(ref, "title required")
        category = item.get("type")
        if category not in FOLDERS:
            ctx.error(ref, "type must match a published Drive category")
        for role in ("published_url", "holding_url"):
            url = item.get(role)
            if role not in item:
                ctx.error(ref, f"explicit {role} required (null if absent)")
            elif url is not None and (not isinstance(url, str) or not url.startswith("https://")):
                ctx.error(ref, f"{role} must be HTTPS or null")
        if "dependencies" in item:
            dependencies = item["dependencies"]
            if (not isinstance(dependencies, list)
                    or any(not isinstance(dep, str) for dep in dependencies)
                    or len(dependencies) != len(set(dep for dep in dependencies if isinstance(dep, str)))):
                ctx.error(ref, "dependencies must be unique resource-ID strings")
            else:
                for dep in dependencies:
                    if dep == ref:
                        ctx.error(ref, "resource cannot depend on itself")
                    elif dep not in registry:
                        ctx.error(ref, f"unknown dependency {dep}")
        if "pdf" in item:
            _validate_pdf(ctx, ref, item, category)
        reviewed = item.get("human_reviewed_url")
        if reviewed is not None and (not isinstance(reviewed, str) or reviewed != item.get("published_url")):
            ctx.error(ref, "human approval must match current published URL exactly")
        if "pdf_url" in item:
            url = item["pdf_url"]
            if category != "classroom_slides" or not isinstance(url, str) or not url.startswith("https://"):
                ctx.error(ref, "pdf_url is only for classroom-slide source PDFs")
        if "print" in item:
            printing = item["print"] if isinstance(item["print"], dict) else {}
            cards = printing.get("cards_per_sheet")
            if (category != "student_material" or set(printing) != {"cards_per_sheet"}
                    or type(cards) is not int or cards < 2):
                ctx.error(ref, "print requires student_material with cards_per_sheet >= 2")


def _validate_pdf(ctx, ref, item, category):
    pdf = item.get("pdf")
    if pdf is None:
        ctx.error(ref, "omit pdf unless generated")
        return
    if not isinstance(pdf, dict):
        ctx.error(ref, "pdf must be an object")
        return
    renderer = pdf.get("renderer")
    if renderer not in PDF_RENDERERS:
        ctx.error(ref, "unsupported PDF renderer (pdf.renderer)")
    elif PDF_RENDERERS[renderer] != category:
        ctx.error(ref, "PDF renderer does not match delivery folder type")
    extra = set(pdf) - PDF_FIELDS
    if extra:
        ctx.error(ref, f"unknown pdf metadata {sorted(extra)}")
    output, source = pdf.get("output"), pdf.get("source")
    if bool(output) == bool(source):
        ctx.error(ref, "PDF needs exactly one output or source")
    if output is not None and (not isinstance(output, str) or not output.endswith(".pdf") or "/" in output):
        ctx.error(ref, "PDF output must be a filename ending in .pdf")
    if source is not None:
        candidate = Path(source) if isinstance(source, str) else Path("/")
        if (not isinstance(source, str) or candidate.is_absolute() or ".." in candidate.parts
                or not (ctx.root / candidate).is_file()):
            ctx.error(ref, "PDF source must be a valid repository file")
    if renderer == "welcome" and not source:
        ctx.error(ref, "Welcome renderer needs a source")
    if renderer in {"teacher_guide", "teacher_companion", "celebrate"} and not output:
        ctx.error(ref, "guide/companion needs an output mapping")
    approved, revision = pdf.get("approved_md5"), pdf.get("revision")
    if approved is not None and not re.fullmatch(r"[0-9a-f]{32}", str(approved)):
        ctx.error(ref, "approved_md5 must be an exact verified MD5")
    if revision is not None and not re.fullmatch(r"[0-9a-f]{40}", str(revision)):
        ctx.error(ref, "revision must be an accepted Git SHA")
    if bool(approved) != bool(revision):
        ctx.error(ref, "approved PDF checksum and accepted revision must be recorded together")
    if approved and not item.get("published_url"):
        ctx.error(ref, "cannot approve unpublished PDF bytes")


def validate_drive_folders(ctx):
    file = ctx.root / "catalog/drive_folders.json"
    if not file.is_file():
        ctx.errors.append("Missing distinct Drive staging/final-folder registry")
        return
    folders = json.loads(file.read_text())
    staging = folders.get("staging") or {}
    for purpose in ("root", "generated_pdf", "worksheets", "visuals", "other", "slide_pdfs"):
        if not (staging.get(purpose) or {}).get("folder_id"):
            ctx.errors.append(f"Unconfigured holding folder: {purpose}")
    for category in ("01_TEACHER_GUIDES", "02_CLASSROOM_SLIDES",
                     "03_STUDENT_MATERIALS", "04_TEACHER_RESOURCES"):
        if not (staging.get("categories") or {}).get(category, {}).get("folder_id"):
            ctx.errors.append(f"Unconfigured holding category: {category}")
    sections = [*(value for value in staging.values() if isinstance(value, dict)),
                *(value for value in (staging.get("categories") or {}).values() if isinstance(value, dict)),
                (folders.get("published") or {})]
    for section in sections:
        for key in ("folder_id", "default_folder_id"):
            value = section.get(key)
            if value is not None and not re.fullmatch(r"[A-Za-z0-9_-]{15,}", str(value)):
                ctx.error(file.relative_to(ctx.root), f"invalid {key} {value!r}")
    for resource_id, folder in ((folders.get("published") or {}).get("by_resource_id") or {}).items():
        if resource_id not in ctx.registry:
            ctx.errors.append(f"Unknown published folder resource ID: {resource_id}")
        if isinstance(folder, dict):
            if not folder or set(folder) - {"main", "pdf"} or "main" not in folder:
                ctx.errors.append(f"Invalid paired published folder mapping for {resource_id}")
            folder_ids = folder.values()
        else:
            folder_ids = (folder,)
        for folder_id in folder_ids:
            if not isinstance(folder_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{15,}", folder_id):
                ctx.errors.append(f"Invalid published destination folder ID for {resource_id}")
