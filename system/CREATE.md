# Create a NEW resource

**Use only when a resource does not yet exist.** Check `catalog/resources.json`, the lesson source and Google Drive first. If its stable ID or intended file already exists, stop creation and use [UPDATE.md](UPDATE.md)—do not create duplicates or overwrite an existing resource. Use [WORKFLOW.md](WORKFLOW.md) for common validation, review and saving.

## Branch ownership

- Default to the **existing lesson branch**, `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` (for example `lesson/ccc-q01-02-secret-ingredients`). Create it from current `main` only if it does not exist. All new Teacher Guides, companions and lesson-associated sources for that lesson share the branch.
- Do **not** create separate task branches, nested-looking feature branches or PRs for individual resources unless the user explicitly requests one. Git branches do not nest. Non-lesson-wide items (for example Welcome) use their existing ownership branch; if none exists, use a dedicated resource branch.
- Reconcile the lesson branch with latest remote changes and `main` before editing; never force-push or override another agent.

## New Python-generated PDF

1. Confirm school, lesson, resource type, **unused stable ID**, source path, and supported build renderer/output.
2. Author editable JSON and required separate versioned assets on the lesson branch; use the repository renderer, validate, test, and inspect pages and working hyperlinks.
3. Upload a new **Teacher Guide** PDF under `01_TEACHER_GUIDES/PDF-generated resources`; a generated **companion** belongs under `04_TEACHER_RESOURCES/Other resources`. Use the configured existing holding folder ID, then read back the Drive ID and URL. The special Welcome material retains its established folder routing.
4. Register `production_type: generated_pdf`, source/build mapping, `holding_url`, and `published_url: null` in `catalog/resources.json`. Review PDFs can link to unpublished resources using their existing permanent Drive IDs.
5. Push the lesson branch, open/update its review PR and share the Actions review and holding link. **Stop without publication.**

## New external worksheet, artwork, slide or media

## Student-facing worksheet PDFs — US Letter

- When creating a resource registered as `student_material`, make **every PDF page US Letter (8.5 × 11 in / 612 × 792 pt)**, portrait or landscape.
- Before uploading the worksheet to Drive holding, run `python scripts/pdf_page_size.py path/to/worksheet.pdf` and fix any failed pages. Inspect the printed layout; do not stretch A4 content to fit.
- **Only** student-facing worksheets have this paper-size rule. Do not resize Teacher Guides, companions, references, artwork or classroom slide PDFs.

1. Create the new resource with the original authoring tool (not the repository PDF renderer); register `production_type: external`.
2. Upload to the matching verified holding category in `catalog/drive_folders.json`, and read back its ID, MIME and URL. Existing legacy Slide PDF originals retain their separate approved review folder until explicitly moved.
3. Add only catalogue bookkeeping on the lesson branch: `holding_url`, resource identity, source provenance and `published_url: null`. If no source branch is needed, save the catalogue change through the lesson's ordinary GitHub PR; do not create a resource-specific branch by default.
4. Preserve the verified Drive URL for links in review PDFs. Once published by **moving the same file**, the ID and URL remain unchanged.

## End of creation

Creation ends with a verified new resource staged in holding, registered and ready for review. **Never publish, change the official `published_url` or promote Drive files** during Create. A subsequent revision follows [UPDATE.md](UPDATE.md); an explicitly authorized release follows [PUBLISH.md](PUBLISH.md). Status and URL semantics belong to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).
