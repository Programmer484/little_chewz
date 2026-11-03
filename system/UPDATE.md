# Update an existing resource

Use this workflow when asked to **revise, fix, or replace an existing resource**, whether draft or published. Resolve its stable ID, exact GitHub source and Drive IDs from current records. If the resource does not exist, use [CREATE.md](CREATE.md) instead. This is a **review operation, not publication**. See [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) for status/URL semantics and [WORKFLOW.md](WORKFLOW.md) for shared checks.

## Python-generated PDFs

1. Use the existing shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch; only create it from `main` if absent. Reconcile its latest head with `main`. Do not create a separate task branch unless explicitly requested; preserve concurrent edits and never force-push.
2. Edit authorized JSON/text source and separate required assets; keep the current official file ID, live URL and publication evidence unchanged.
3. Validate, test, render through the existing repository PDF renderer and inspect the pages and clickable links.
4. Upload or replace the **review PDF in holding**, keeping its existing category: Teacher Guides under `01_TEACHER_GUIDES`, companions under `04_TEACHER_RESOURCES`. Preserve the file ID when possible and update `holding_url` only if needed.
5. Save source to GitHub, open/update the PR and share the actual Actions run and review copy. A passing build or ordinary merge is not publication.

## External resources

## Student-facing worksheet PDFs — preserve US Letter

- When updating a resource registered as `student_material`, keep **every PDF page US Letter (8.5 × 11 in / 612 × 792 pt)**, portrait or landscape.
- After revising and **before uploading** the replacement review copy, run `python scripts/pdf_page_size.py path/to/worksheet.pdf`. Fix any page-size failures without distorting content.
- This requirement does **not** apply to Teacher Guides, companions, references, artwork or classroom slide PDFs.

1. Edit using the original creation tool; do not invent a Python renderer or separate per-resource branch.
2. Replace the same holding Drive file in place where possible; otherwise stage a new review copy in the verified appropriate holding folder.
3. Verify ID, MIME, size, URL, visuals, text and links. Slide-specific PDF/PPTX review checks are in [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md).
4. Save catalogue bookkeeping on the shared lesson branch through its existing PR when available. Preserve the published file, verified `published_url`, any existing `pdf.approved_md5` and `pdf.revision`; a new holding URL distinct from the official URL derives a pending update; do not replace the official link.

## Finish

Report the review copy, GitHub PR/record, checks and blockers. **Do not replace or move the official Drive file as part of an update.** When the user later approves publication of that exact version, follow [PUBLISH.md](PUBLISH.md).
