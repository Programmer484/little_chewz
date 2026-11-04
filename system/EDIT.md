# Create or update a resource

**Creating or revising is review work, never publication.** Read [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) for source, asset, status and URL rules; [WORKFLOW.md](WORKFLOW.md) for checks and previews. Official delivery always uses [PUBLISH.md](PUBLISH.md).

## Identify and save the source

1. Check `catalog/resources.json`, the lesson/quest source, and existing Drive IDs first. If the resource or stable ID already exists, **update it**; never create a duplicate.
2. Reuse the shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch. Create it from current `main` only if absent; reconcile remote edits without force-pushing. For non-lesson resources, reuse their established owner branch or use a dedicated branch.
3. Edit the authoritative JSON, text or original external authoring file; keep necessary artwork as separate repository files. Preserve existing lesson/quest source paths and stable IDs.
4. Validate, run relevant checks, inspect rendered pages/links, and save via the existing review PR. Share the actual GitHub Actions run and any verified holding review copy. **Stop before official publication.**

## Python-generated PDF

- **New:** choose a supported renderer, output/source, and unused stable ID. Copy the appropriate `templates/<type>/TEMPLATE.json` and keep its `template` field. Register `pdf.renderer` and `pdf.output` or `pdf.source` under the resource in `catalog/resources.json`, with `holding_url` and `published_url: null`. No separate dependency registration is needed.
- **Existing:** edit its source/assets and preserve its current official Drive file ID, `published_url`, `pdf.approved_md5`, and `pdf.revision`. Never replace the published PDF as part of an edit.
- Generate with the existing repository renderer. Stage new or revised **review** PDFs in the configured holding folder: Teacher Guides under `01_TEACHER_GUIDES/PDF-generated resources`, companions under `04_TEACHER_RESOURCES/Other resources`; Welcome retains its established routing. Read back the file ID and URL, reusing the holding file ID when possible.
- Review PDFs may link to already staged resources through verified permanent Drive IDs; official release requires all referenced resources to have approved official URLs.

## Externally authored worksheet, slides, artwork or media

- Use the original authoring tool, **not** the Python PDF renderer; catalogue entries omit `pdf`.
- **New:** register an unused stable ID with a verified `holding_url` and `published_url: null`. Upload only to its verified holding category in `catalog/drive_folders.json`, and read back the file ID, MIME type and URL. Existing Slide PDF originals retain their separate review folder.
- **Existing:** revise the holding copy in place where possible; otherwise stage a separate review copy. Keep the current official file and `published_url` unchanged, and record a distinct new `holding_url` only when a revision is pending.
- Before uploading a `student_material` worksheet PDF, run `python scripts/pdf_page_size.py path/to/worksheet.pdf`: **every page must be US Letter (8.5 × 11 in, portrait or landscape)**. Don't stretch A4 to fit. This restriction does not apply to guides, companions, references, artwork or classroom slides.
- For slide PDF/PPTX review and pairing, also follow [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). Verify holding IDs, formats, text, visuals and links.

## Handoff

Report reviewed source, PR/preview, holding location and any blockers. A successful upload, preview or merge **does not** authorize an official Drive move or replacement; wait for explicit authorization, then use [PUBLISH.md](PUBLISH.md).
