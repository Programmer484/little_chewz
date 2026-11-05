# Create or update a resource

**Creating or revising is review work, never publication.** Read [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) for source, asset, status and URL rules; [WORKFLOW.md](WORKFLOW.md) for checks and previews. Official delivery always uses [PUBLISH.md](PUBLISH.md).

## Identify and save the source

1. Check `catalog/resources.json`, the lesson/quest source, and existing Drive IDs first. If the resource or stable ID already exists, **update it**; never create a duplicate.
2. Reuse the shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch. Create it from current `main` only if absent; reconcile remote edits without force-pushing. For non-lesson resources, reuse their established owner branch or use a dedicated branch.
3. Edit the authoritative JSON, text or original external authoring file; keep necessary artwork as separate repository files. Preserve existing lesson/quest source paths and stable IDs.
4. Validate, run relevant checks, inspect rendered pages/links, and save via the existing review PR. Share the actual GitHub Actions preview. A generated PDF does not need a Drive holding review copy. **Stop before official publication.**

## Python-generated PDF (Teacher Guides, companions and Welcome)

- **New:** create the editable source from the matching `templates/<type>/TEMPLATE.json`, retaining its `template` field. Add a stable resource ID, `pdf.renderer` and `pdf.output` or `pdf.source` to the catalogue, with `holding_url: null` and `published_url: null`. GitHub renderers can build a **new file**, not just update an existing one.
- **Existing:** revise the authoritative GitHub source; preserve its established published Drive ID, URL and verified checksum/revision. Never modify the live Drive file during editing.
- **Review in GitHub, not Drive holding.** Every PR edit generates a PDF preview. Inspect its content, page layout and resource links; iterate until approved. The GitHub preview is the draft. There is no need to stage a Python-generated PDF in Drive.
- **After approval:** follow [PUBLISH.md](PUBLISH.md) for direct official upload or an in-place update. Ensure the final linked resources have the intended official catalogue destinations.

## Externally authored worksheet, slides, artwork or media

- Use the original authoring tool, **not** the Python PDF renderer; catalogue entries omit `pdf`.
- **New:** register an unused stable ID with a verified `holding_url` and `published_url: null`. Upload only to its verified holding category in `catalog/drive_folders.json`, and read back the file ID, MIME type and URL. Existing Slide PDF originals retain their separate review folder.
- **Existing:** revise the holding copy in place where possible; otherwise stage a separate review copy. Keep the current official file and `published_url` unchanged, and record a distinct new `holding_url` only when a revision is pending.
- Before uploading a `student_material` worksheet PDF, run `python scripts/pdf_page_size.py path/to/worksheet.pdf`: **every page must be US Letter (8.5 × 11 in, portrait or landscape)**. Don't stretch A4 to fit. This restriction does not apply to guides, companions, references, artwork or classroom slides.
- For slide PDF/PPTX review and pairing, also follow [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). Verify holding IDs, formats, text, visuals and links.

## Handoff

Report reviewed source, PR/preview, any external-resource holding location and blockers. A successful upload, preview or merge **does not** authorize an official Drive move or replacement; wait for explicit authorization, then use [PUBLISH.md](PUBLISH.md).
