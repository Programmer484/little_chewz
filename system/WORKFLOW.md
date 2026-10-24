# Editing and delivery workflow

Applies to source, instruction, and tooling edits. Existing user authorization carries through the task; do not ask again for an already authorized action.

## Routine

1. **Inspect.** Check the working tree and remote state. Read the task's owning instructions and source/status records. Identify whether the request changes content, presentation, tooling, or publication.
2. **Edit.** Multiple AIs can work simultaneously, using separate task branches and PRs. Edit the owning files and preserve unrelated changes. Before merging, compare against the latest `main` and reconcile parallel edits to avoid overwriting another AI's work. For new resources, use an existing supported template when available, assign a stable ID, and record status only in its owning source; do not add speculative templates.
3. **Verify.** Review the diff and run `python scripts/validate.py`. Run relevant tool tests for code changes. For document changes, build only affected supported outputs and inspect pages, text, artwork, and hyperlinks. **Generate Teacher Guide review copies with the repository renderer, including unapproved sources (`python scripts/renderers/teacher_guide.py --content <lesson.json> --output <review.pdf>`); never use an independent ad-hoc layout script.** Drafts remain review-only and are not automatically covered by approved-output CI builds. Check changed instructions for conflicting rules, obsolete paths, and broken local links. Report check limits; do not imply unregistered drafts were validated or rendered.
4. **Save.** Commit and push all intended source changes and required assets; exclude secrets and temporary/generated files. Verify the remote branch contains the commits. Open a draft PR if unfinished, or a review PR if ready, with checks and remaining blockers. Local files, commits, attachments, and PR descriptions alone are not saved GitHub source.
5. **Finish.** The user prefers **merge-first, reconcile-on-`main`**. When authorized and checks pass, merge the PR promptly, verify `main` contains its intended changes and preserves concurrent updates, and review the resulting `main` Actions run. Do not delay an authorized merge just to preserve a temporary preview link. Otherwise leave the pushed PR and blockers stated. Unapproved source may be merged if authorized; retain its status. It may produce a review preview but remains excluded from approved-only output selection.
6. **Clean up.** Do **not** automatically delete GitHub PDF preview branches or history folders when PRs merge or close. Never merge `pdf-preview-history` or earlier `pdf-preview-run-*` / `pdf-preview-pr-*` branches into `main`. Manual preview cleanup requires explicit user instruction. Source-branch cleanup is separate: preserve any unmerged work, check for commits added after squash merges, and synchronize local `main` safely.

## Preview links and retention

- Give the **actual GitHub Actions run URL** (`https://github.com/Programmer484/little_chewz/actions/runs/<run-id>`) as the **default first link** for PDF reviews. Prefer the relevant successful **post-merge `main` push run**, reflecting the combined AI edits. Use the PR run if it is the latest verified run and `main` has not generated a preview. For validation-only or failed runs, say so; never imply that a PDF exists. Never reuse an old example run for new work.
- The run summary links to permanent `previews/<run-id>/` folders on the **single** `pdf-preview-history` branch. This avoids creating a branch per run while keeping every review URL stable. Existing `pdf-preview-run-*` branches and links remain intact. Direct PDF links can follow the run URL; do not lead with a PR Files tab or generated-branch link. Source merge and PDF preview are not teaching-content approval or Drive publication.
- **No automatic preview deletion** on PR closure or merge. Historical branches and the per-run history folders remain intact; manual pruning requires explicit instruction. Workflow artifacts expire after **seven days**, but browser previews stay accessible.

## Publication is separate

- A source merge does not approve content, register a build target, or authorize Drive publication. Follow the status rules in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).
- Publish only within explicit authorization, after source approval and review of the exact regenerated output. Resolve missing, stale, or unapproved links first; verify intended access.
- When updating a published Drive PDF, replace the existing file in place to preserve its ID. For registry entries with `build` instructions, use the **Publish to Drive** workflow ([DRIVE_PUBLISHING.md](DRIVE_PUBLISHING.md)), dry run first. Do not rename, duplicate, merge, or republish live assets as a side effect of source maintenance.
- Register a new verified destination and set the linked resource status to `published` in `catalog/resources.json` after publication. Preserve stable IDs for existing resources.

## Classroom slide PDF to PowerPoint

Slide PDF editing, approval, PPTX conversion, and in-place Drive replacement follow [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). It is a human-approved publication path, separate from source previews and the unimplemented editable-slide generator.

## Completion report

State concisely:

- Files changed and source/review status.
- Checks, generated outputs, and remaining issues.
- **Actions run URL first** for PDF previews (prefer post-merge `main`); then commit/PR link and whether `main` was verified.
- Any unsaved work, remaining PRs, unpushed commits, local-only source/assets, or cleanup failures. Never claim all work is saved if verification failed.
- For a published Drive replacement: exact file ID and confirmation of replacement in place.

## PDF build selection

Relevant PR updates **and pushes to `main`** run source validation and tool tests. A review PDF renders only when one of its actual inputs changes or it is explicitly requested. PR selection compares the complete proposal against its base; `main` selection compares the before/after push commits. Generation never changes source content, grants approval, merges a PR, or publishes to Drive.

`scripts/select_builds.py` discovers lessons through `catalog/quests.json` → `quest.json` → each lesson's fixed `lessons/<stage>/lesson.json`; a lesson without one is skipped, with no placeholder. Every valid lesson source is previewable regardless of status. Lesson status comes **only** from `quest.json` (default `unapproved`); companion status **only** from its `catalog/resources.json` entry. `all-approved` includes only `approved` or `published` sources. There is no `stage.json` status check, `preview_enabled` flag, or separate draft filename.

Registry entries with `build.renderer` (such as the Welcome PDF, `ccc-q01-welcome`) are also targets, output as `<resource-id>.pdf` with status from that registry entry. **Publish to Drive** builds through the same path.

What rebuilds:

- A source (even a metadata or provenance edit) or its local cover artwork rebuilds only its own output. Creating an eligible source creates its first preview.
- A shared renderer change rebuilds its eligible consumers.
- A resource-registry change rebuilds only documents referencing changed IDs, titles, or destinations. Status-only edits rebuild nothing, except that navigation pages rebuild when a linked entry's status changes (it decides **Open Guide** versus **Coming Soon**). Drive edits without a registry change rebuild nothing.
- A registry-built document also rebuilds when anything in its source folder or `templates/<renderer>/assets/` changes.
- Any edit to `requirements.txt`, `scripts/build_selected.py`, or the PDF workflow rebuilds all eligible PDFs. This deliberately favors an occasional extra preview over complex dependency detection.
- Editorial documentation, unused templates, unrelated stories/worksheets/slides, tests, validation/selection logic, and action-label data (validation-only) rebuild nothing on their own.

When adding a renderer input or changing how build commands are invoked, update the selector and its regression tests in the same PR.

Manual builds (**Actions → PDF previews → Run workflow**) accept one exact eligible output filename (such as `01-set-the-table-teacher-guide.pdf`) or `all-approved` (drafts excluded). Unknown, missing-source, or unresolved-link requests fail explicitly. Drafts get the same source checks and PDF verification as approved sources; their previews may show existing unverified HTTPS links with validation warnings and do not authorize release. `scripts/build_selected.py` is the supported batch builder and rechecks eligibility before rendering. Each PDF-rendering run adds a unique folder on `pdf-preview-history` (retention above).
