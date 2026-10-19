# Little Chewz — Mandatory AI instructions

You are editing a **source-first educational content repository**, not a PDF as the source of truth.

## Read in this order

1. `START_HERE.md` for navigation and system intent.
2. `system/CONTENT_CONTRACT.md` for types, paths, and version rules.
3. `system/EDITORIAL_GUIDE.md` and, for companions, `system/RESOURCE_GUIDELINES.md`.
4. `catalog/quests.json` -> targeted `quest.json` -> editable lesson/resource file.
5. `catalog/resources.json` for the only authoritative URLs and linked names.
6. Relevant renderer in `scripts/renderers/` **only if editing layout/generation**.
7. `system/CHAT_FILE_CREATION.md` **when creating or transferring files through chat**, especially images or other binary assets.

## Hard rules

- Use **only** approved source facts, canon, names, dialogue, existing activities, and approved resource URLs. Do not extrapolate or create 'missing' worksheets.
- `status: migration_needed` or `status: draft_transcription` means NOT APPROVED for final teaching/publishing. Never silently upgrade it.
- Edit lesson-level text/steps in `content/**/lessons/**/lesson.json`; companion blocks in `content/**/resources/**.json`; stories and raw letters in Markdown.
- Single content owner: Never duplicate whole resource text inside the teacher flow. Teacher Guide links to resources by stable ID; slideshow navigation uses slide numbers only.
- PDFs are generated exports, **except a legacy PDF still waiting to be converted**. Every image consumed by a PDF build must be checked into GitHub as a versioned source asset, including full-page images and covers. A finished image distributed directly from Drive without any PDF-building step may be Drive-link-only. Preserve its stable ID in the resource registry. Don't copy large exported PDFs into this edit-source package.
- Generate and maintain **one independent slide set/deck per lesson**, rather than a full quest deck. Use slide numbers local to each lesson, and link its approved slide set in the Teacher Guide. Make updates surgically (one or two slides where possible); rebuild only the affected lesson's slides, not the entire quest. This is future policy; no slide renderer or slide build workflow exists yet.
- Keep the seven-slide published Activate asset unchanged. The older 44-slide continuous quest deck is a historical reference only; never automatically reuse its global slide numbers, merge assets, or republish Drive materials.
- Missing, stale, or unapproved links MUST be flagged; never invent URLs or quietly fall back to unlinked text.
- Preserve teacher-guide structure and exact approved editorial rules described in `system/EDITORIAL_GUIDE.md`.
- Use `system/action_labels.json` as the single authority for action vocabulary (renderer and validator must consult the same list when validation applies).
- Separate **content changes** from **visual design changes** and **publishing actions**; verify the regenerated document before publication.
- **Files made in chat:** Use `system/CHAT_FILE_CREATION.md` for source creation, binary assets, verification, and temporary-transfer cleanup. Never stop at “the connector cannot upload binary” without checking its verified Base64 blob + tree/commit/ref workflow. Do not claim an uploaded asset is approved or publish it automatically.

## Save work and finish through PRs

- Use PRs as the review queue; branches are temporary working locations. Create one branch and PR per coherent change. Open a draft PR when work is unfinished so it is visible and recoverable.
- Before ending an editing session, commit and push all intended source changes and required assets. Verify the remote branch contains the commits. A local file, local commit, chat attachment, or PR description alone is not a saved GitHub source. Preserve unrelated user changes; never include secrets or temporary/generated files merely to make the working tree clean.
- Run applicable validation and checks. When merging is authorized and the change is ready, merge the PR and verify it reached `main`. Otherwise leave a pushed draft/review PR with a clear summary and remaining blockers. Existing user authorization applies; do not request the same permission again.
- Useful unfinished educational content may be merged as explicitly marked draft source, with unresolved work recorded in its stage/source metadata. Merging stores the work; it does not promote `draft_transcription` or `draft_unpublished` to approved content, enable a build target, or authorize Drive publication. Keep drafts excluded from approved-output builds until their separate approval requirements are met.
- GitHub's **Automatically delete head branches** setting is enabled. After merging, verify source-branch deletion and the existing PDF-preview cleanup workflow. Never merge `pdf-preview-pr-*` branches into `main`; they contain disposable generated outputs. Do not delete an unmerged source branch just because it is old or its PR is closed. For squash merges, verify the merged PR and any subsequent branch commits rather than relying only on `git branch --merged`.
- After cleanup, fetch/prune remote refs and update local `main` when safe. Report any remaining PRs, unpushed commits, local-only source/assets, or cleanup failures explicitly. Never claim all work is saved when verification failed.

## Required output from each future AI edit

State: files edited; source and review status; validation result; generated outputs; remaining unresolved issues; commit/PR link and whether it is pushed or merged; any unsaved work or remaining branch cleanup. If changing the published Drive PDF, document the exact file ID and confirm it was replaced in place.
