# Create or update a resource

**Creating or revising is review work, never publication.** Read [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) for source, asset, status and URL rules; [WORKFLOW.md](WORKFLOW.md) for checks and previews. Official delivery always uses [PUBLISH.md](PUBLISH.md).

## Create or revise the source

1. **Start with the editable file.** For a new Teacher Guide or companion, use the matching GitHub JSON template. For an existing resource, edit its source. Keep any necessary artwork as separate repository assets.
2. Check the relevant `catalog/resources.json` ID and lesson path so a revision reuses its identity rather than creating a duplicate. **No Drive verification is needed to begin editing.**
3. Work on the shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch, creating it from current `main` if absent. For non-lesson work, use its existing owner branch or a dedicated branch. Reconcile remote edits without force-pushing.
4. Commit, inspect the automatically generated GitHub PDF preview, and revise as needed. Share the GitHub Actions link. **Stop before official publication.**

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
