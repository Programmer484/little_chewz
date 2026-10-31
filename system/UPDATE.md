# Update an existing resource

Use this workflow when asked to **revise, fix, or replace an existing resource**, whether draft or published. Resolve its stable ID, exact GitHub source and Drive IDs from current records. This is a **review operation, not publication**. See [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md) for status/URL semantics and [WORKFLOW.md](WORKFLOW.md) for shared checks.

## Python-generated PDFs

1. Fetch and reuse the existing remote `edit/<resource-id>` branch; reconcile its latest head with `main`. Preserve concurrent edits and never force-push.
2. Edit authorized JSON/text source and separate required assets; keep the current official file ID, live URL and publication evidence unchanged.
3. Validate, test, render through the existing repository PDF renderer and inspect the pages and clickable links.
4. Upload or replace the **review PDF in holding**; verify its Drive ID and update the recorded `holding_url` if needed.
5. Save source to GitHub, open/update the PR and share the actual Actions run and review copy. A passing build or ordinary merge is not publication.

## External resources

1. Edit using the original creation tool; do not invent a Python renderer or generated-PDF source branch.
2. Replace the same holding Drive file in place where possible; otherwise stage a new review copy in the verified appropriate holding folder.
3. Verify ID, MIME, size, URL, visuals, text and links. Slide-specific PDF/PPTX review checks are in [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md).
4. Save catalogue bookkeeping through an ordinary GitHub change. Preserve the published file, verified `published_url`, compatibility `url` and current publication evidence; do not mark the new draft published.

## Finish

Report the review copy, GitHub PR/record, checks and blockers. **Do not replace or move the official Drive file as part of an update.** When the user later approves publication of that exact version, follow [PUBLISH.md](PUBLISH.md).
