# Editing and delivery workflow

Applies to all source, instruction, and tooling changes. The three user commands are specified in [COMMANDS.md](COMMANDS.md).

## Routine

1. **Inspect.** Identify the resource from chat context and its stable ID in the catalog. Read its source and `$instructions`, the latest remote branch, and `main`.
2. **Edit.** Use **one active branch per resource**, `edit/<stable-resource-id>`. Reuse it across AI chats and agents. Fetch its latest remote head, commit directly to it, and push non-force. If it changed during editing, reconcile and retry without overwriting another agent. Different resources have separate branches. Use temporary child branches only for genuinely overlapping concurrent edits.
3. **Verify.** Check the diff, run `python scripts/validate.py` and relevant tests; render affected supported documents using the repository's renderer. Inspect content, layout, and hyperlinks. Previews are not Drive publications.
4. **Save.** Push source and required assets and open/reuse the resource PR. Never consider local-only output saved.
5. **Merge.** On `/merge` or equivalent explicit user authorization, reconcile with the latest `main`, rerun checks, merge, verify the combined `main` output, and give its post-merge Actions preview. Delete the resource branch only after verifying no unmerged commits remain.
6. **Publish as part of merge.** Existing resources: replace the same Drive file ID in place and verify bytes. New resources: find the proper Drive folder, create the first file, verify its ID/URL and access, then finish catalogue registration. On failure, preserve `pending_publish` if there is an older live Drive version or `unpublished` otherwise, and state the blocker. Never claim `published` before verification.
7. **Report.** Source changes, checks, PR/merge, combined preview link (Actions URL first), Drive result/ID, and any remaining failure.

**Current implementation boundary:** GitHub has validation, targeted previews and an *internal manual* in-place Drive PDF replacement workflow. Merge-triggered publishing, first-time Drive creation and hash-based sync detection are not yet built. Until implemented, follow these steps with the available tools, disclose missing operations, and never pretend merge auto-published. **There is no independent `/publish` user command.**

## Previews and cleanup

- Prefer the verified post-merge `main` Actions run URL; use a PR run when no `main` PDF preview exists. Never invent run URLs. PDF previews use per-run `previews/<run-id>/` directories on the permanent `pdf-preview-history` branch. Workflow artifacts expire after seven days; browser previews remain.
- Delete completed resource branches after verifying merged commits. Preserve review history and any unmerged work. Never merge preview-history branches into `main`, nor delete earlier `pdf-preview-run-*` / `pdf-preview-pr-*` history as a side effect.

## Publishing

Drive delivery is the final phase of `/merge`, not a second user operation. See [DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md) for the existing internal PDF replacement path, and [CREATE.md](CREATE.md) for the first-time registration flow. Keep file IDs and sharing unchanged on replacements. Confirm paired slide PDF and PPTX under [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). Unverified links block release.

## PDF build selection

PR updates and `main` pushes validate, run tests and rebuild only affected registered PDFs. All existing valid lesson, companion, and registry-rendered sources are previewable regardless of delivery state. Missing `lesson.json` creates no placeholder. Manual preview selection is one exact PDF filename or `all` (all registered outputs); there is no approval-filtered build mode.

A changed source, cover, template asset, renderer, relevant catalog link/title, nav status, or shared build dependency triggers relevant outputs; unrelated documentation, tests, status metadata and raw stories do not on their own render unrelated PDFs. Navigation links are live for `published` or `pending_publish` destinations; `unpublished` shows Coming Soon.