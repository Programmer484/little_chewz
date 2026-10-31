# Editing and review workflow

This file owns edits, previews, tests, source saving and reporting, **not publication**. Route user intent through [COMMANDS.md](COMMANDS.md); draft creation is in [CREATE.md](CREATE.md), status definitions in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md), and all release procedures in [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md).

## Python-generated PDFs — edit and review

1. **Identify.** Read stable ID, editable GitHub source, build mapping, holding file, official file and current delivery status. Read the source's instructions.
2. **Edit.** Reuse the remote `edit/<resource-id>` branch across chats. Reconcile with latest remote head and `main`; preserve concurrent edits, save separate required assets and never force-push.
3. **Preview.** Validate, test, render with the repository renderer and inspect layout and links. Upload or replace a review copy in the verified generated-PDF holding folder. Holding is never publication.
4. **Save/report.** Push the branch, open/update its PR, verify remote files, give the actual Actions preview and holding copy, and report blockers. A preview or normal PR merge does not authorize release.

## External resources — edit and review

Create/edit with the original authoring tool. Verify the holding Drive file and replace the **same holding file ID** where possible; update catalogue bookkeeping through an ordinary GitHub change. Do not create a generated-PDF renderer or resource-specific `edit/` branch for an external file. Preserve any live official file and status. For initial staging use [CREATE.md](CREATE.md); for authorized publication use [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md).

## Previews and cleanup

- `scripts/select_builds.py` and `scripts/build_selected.py` are the supported Python preview path. Every existing valid authored source is previewable regardless of delivery status; missing lesson source files create no placeholders. Manual selection accepts an exact output filename or `all`.
- PR updates and `main` pushes validate and rebuild affected PDFs. A changed source, asset, renderer, resource link or shared dependency rebuilds its consumers; unrelated docs and status-only bookkeeping do not rebuild content.
- Prefer the successful **post-merge `main` Actions run URL** for PDF review. Previews stay in `pdf-preview-history/previews/<run-id>/`; workflow artifacts have short retention. Never merge or automatically delete historical preview branches.
- Preserve unmerged work and report errors; generated-resource branch cleanup rules are in [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md).

## Release boundary

For first-time official Drive placement, approved `/merge`, agent-managed external publication, release-verification checks, `pending_publish` handling, and read-only inspection, **follow [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md)**. This workflow is only for drafts and review. Status and URL field semantics remain in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).
