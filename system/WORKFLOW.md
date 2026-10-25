# Editing and delivery workflow

Little Chewz has **two production workflows**. `/create` and `/update` are agent instructions; `/merge` is used **only for Python-generated PDFs**. See [COMMANDS.md](COMMANDS.md) and [CREATE.md](CREATE.md). Never infer resource production type from the file extension.

## Python-generated PDFs

1. **Identify.** Resolve the stable catalogue ID, GitHub source, build mapping, holding copy, published destination and current delivery status. Read the source's instructions.
2. **Edit.** Use one shared `edit/<resource-id>` branch. Fetch its latest remote head; reconcile simultaneous edits without force-pushing or overwriting work. Save editable source and separate required assets in GitHub.
3. **Preview.** Validate, run relevant tests, render with the repository renderer, and inspect the PDF and hyperlinks. The agent uploads/replaces the **holding copy** in the configured PDF-generated review folder. Holding is not publication.
4. **Approve and merge.** After the user approves the exact generated PDF, add the single-resource authorization marker to the existing PR and merge only after checks and reconciliation with current `main`. The merged `main` PDF-preview Actions run is the primary review link.
5. **Publish.** For an established official PDF destination, the guarded GitHub Actions merge workflow builds the accepted PDF, replaces the same Drive file ID, reads back its checksum, writes the revision and publication evidence, and removes the merged edit branch only if it has not advanced. Failed verification retains `pending_publish` for an older live release. The agent must establish and verify a first-time official Drive destination manually before subsequent automated releases.
6. **Report.** Give the real Actions run URL, PR/commit, validation and Drive results, exact file ID and any failure. A merge or upload is not proof of publication.

## All external resources

Author the file with the appropriate tool. Upload to the configured **holding folder** (or the separate Slide PDFs review folder), verify the ID, and record catalogue metadata through a normal GitHub bookkeeping change. Do not create a GitHub source branch or Python renderer just to track an externally generated file. For updates, replace the existing holding copy in place when possible.

Once the agent has been instructed to publish the external resource, manually move or replace the file into the appropriate teacher-facing Drive destination; verify ID, MIME, access and any paired PDF/PPTX deliverables. **Only then** record `published_url`, compatibility `url`, status and agent confirmation in the catalogue. There is no external `/merge`, automatic Drive publishing, content-checksum comparison or scheduled monitoring.

## Previews and cleanup

- `scripts/select_builds.py` and `scripts/build_selected.py` are the supported Python PDF preview path. All existing valid authored sources are previewable irrespective of delivery status; absent lesson source files produce no placeholders. Manual selector accepts an exact output filename or `all`.
- PR updates and pushes to `main` validate and rebuild affected PDFs. A changed source, relevant asset, renderer, resource link or shared dependency rebuilds only its consumers; unrelated documentation and publication-only metadata do not rebuild content.
- Prefer the successful **post-merge `main` Actions run URL** when citing PDF reviews. Preview PDFs remain in `pdf-preview-history/previews/<run-id>/`; workflow attachments have short retention. Never merge or delete historical preview branches automatically.
- GitHub Actions cleans up a generated-resource edit branch only after successful verified publication and only when the remote branch head still matches the merged PR. Agents preserve unmerged work and inspect failures.

## Publication controls

The only statuses are `unpublished`, `pending_publish`, `published`. They are delivery states, not additional human-approval states. Work in progress does not change a verified published version. `catalog/resources.json` records linked-resource status, `quest.json` records lesson-source status. Exact generated-PDF verification uses a stored MD5 and accepted revision; external resources use agent confirmation, never an invented checksum.

A manual [publication inspection](../.github/workflows/inspect-publications.yml) is available; it is **read-only and on demand**. Published links, live IDs and resource privacy must be checked; lack of evidence is reported as unverified. Drive publishing details are in [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md).
