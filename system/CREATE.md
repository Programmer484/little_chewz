# Create a NEW resource

**Use only when a resource does not yet exist.** Check `catalog/resources.json`, the lesson source and Google Drive first. If its stable ID or intended file already exists, stop creation and use [UPDATE.md](UPDATE.md)—do not create duplicates or overwrite an existing resource. Use [WORKFLOW.md](WORKFLOW.md) for common validation, review and saving.

## Branch ownership

- Default to the **existing lesson branch**, `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` (for example `lesson/ccc-q01-02-secret-ingredients`). Create it from current `main` only if it does not exist. All new Teacher Guides, companions and lesson-associated sources for that lesson share the branch.
- Do **not** create separate task branches, nested-looking feature branches or PRs for individual resources unless the user explicitly requests one. Git branches do not nest. Non-lesson-wide items (for example Welcome) use their existing ownership branch; if none exists, use a dedicated resource branch.
- Reconcile the lesson branch with latest remote changes and `main` before editing; never force-push or override another agent.

## New Python-generated PDF

1. Confirm school, lesson, resource type, **unused stable ID**, source path, and supported build renderer/output.
2. Author editable JSON and required separate versioned assets on the lesson branch; use the repository renderer, validate, test, and inspect pages and working hyperlinks.
3. Upload the first review PDF to the verified holding folder under `01_TEACHER_GUIDES` (or the matching category for its resource type). Read back its Drive ID and URL.
4. Register `production_type: generated_pdf`, source/build mapping, `holding_url`, and `status: unpublished` in `catalog/resources.json`. Review PDFs can link to unpublished resources using their existing permanent Drive IDs.
5. Push the lesson branch, open/update its review PR and share the Actions review and holding link. **Stop without publication.**

## New external worksheet, artwork, slide or media

1. Create the new resource with the original authoring tool (not the repository PDF renderer); register `production_type: external`.
2. Upload to the matching verified holding category in `catalog/drive_folders.json`, and read back its ID, MIME and URL. Existing legacy Slide PDF originals retain their separate approved review folder until explicitly moved.
3. Add only catalogue bookkeeping on the lesson branch: `holding_url`, resource identity, source provenance and `status: unpublished`. If no source branch is needed, save the catalogue change through the lesson's ordinary GitHub PR; do not create a resource-specific branch by default.
4. Preserve the verified Drive URL for links in review PDFs. Once published by **moving the same file**, the ID and URL remain unchanged.

## End of creation

Creation ends with a verified new resource staged in holding, registered and ready for review. **Never publish, change live resource status or promote Drive files** during Create. A subsequent revision follows [UPDATE.md](UPDATE.md); an explicitly authorized release follows [PUBLISH.md](PUBLISH.md). Status and URL semantics belong to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).
