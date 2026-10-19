# Editing and delivery workflow

Applies to source, instruction, and tooling edits. Existing user authorization carries through the task; do not ask again for an already authorized action.

## Routine

1. **Inspect.** Check the working tree and remote state. Read the task's owning instructions and source/status records. Identify whether the request changes content, presentation, tooling, or publication.
2. **Edit.** Use one branch and PR per coherent change. Make the smallest complete change in the owning files; preserve unrelated work. For new resources, use the matching template, assign a stable ID, and record source/status and blockers in existing metadata.
3. **Verify.** Review the diff and run `python scripts/validate.py`. Run relevant tool tests for code changes. For document changes, build only affected supported outputs and inspect pages, text, artwork, and hyperlinks. **Generate Teacher Guide review copies with the repository renderer, including draft sources (`python scripts/renderers/teacher_guide.py --content <lesson.draft.json> --output <review.pdf>`); never use an independent ad-hoc layout script.** Drafts remain review-only and are not automatically covered by approved-output CI builds. Check changed instructions for conflicting rules, obsolete paths, and broken local links. Report check limits; do not imply unregistered drafts were validated or rendered.
4. **Save.** Commit and push all intended source changes and required assets; exclude secrets and temporary/generated files. Verify the remote branch contains the commits. Open a draft PR if unfinished, or a review PR if ready, with checks and remaining blockers. Local files, commits, attachments, and PR descriptions alone are not saved GitHub source.
5. **Finish.** If merge is authorized and checks pass, merge and verify the result on `main`. Otherwise leave the pushed PR with its remaining work stated. Useful unfinished content may be merged as explicitly unapproved draft source; retain its blockers and keep it excluded from approved-output builds.
6. **Clean up.** After merge, verify automatic source-branch deletion and the PDF-preview cleanup workflow. Never merge `pdf-preview-pr-*` branches into `main`. Never delete an unmerged source branch solely because it is old or closed. For squash merges, verify the merged PR and any later branch commits before deleting a local branch. Fetch/prune and update local `main` when safe.

## Publication is separate

- A source merge does not approve content, register a build target, or authorize Drive publication. Follow the status rules in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).
- Publish only within explicit authorization, after source approval and review of the exact regenerated output. Resolve missing, stale, or unapproved links first; verify intended access.
- When updating a published Drive PDF, replace the existing file in place to preserve its ID. Do not rename, duplicate, merge, or republish live assets as a side effect of source maintenance.
- Register a new approved destination in `catalog/resources.json` after publication. Preserve stable IDs for existing resources.

## Completion report

State concisely:

- Files changed and source/review status.
- Checks, generated outputs, and remaining issues.
- Commit/PR link; whether pushed or merged and verified on `main`.
- Any unsaved work, remaining PRs, unpushed commits, local-only source/assets, or cleanup failures. Never claim all work is saved if verification failed.
- For a published Drive replacement: exact file ID and confirmation of replacement in place.

## PDF build selection

Run source validation and tool tests for relevant PR changes, including tests and tooling. Generate a review PDF only when one of its actual inputs changes or that output is explicitly requested. PR selection compares the complete proposed change against the PR base. Generation never changes source content, grants editorial approval, merges a PR, or publishes to Drive.

`scripts/select_builds.py` discovers lessons through `catalog/quests.json` → `quest.json` → stage/source records, and companions in those quests. Approved lessons require approved quest and stage statuses (and source status when present). Approved companions require `review_status: approved_source`. To enable an unapproved lesson preview, set `preview_enabled: true` in its existing `stage.json` and name its `lesson_source`; for a companion, set the flag in its source. Do not change approval status to enable a preview. Incomplete drafts without opt-in remain excluded. Set the Table is opted in; its outstanding editorial and resource-link blockers remain.

Sources and their local cover artwork select only their own outputs. Shared renderers select their eligible consumers. Resource-registry changes select only documents referencing changed IDs; external Drive edits without a registry change do not trigger a build. PyMuPDF changes select guides; ReportLab changes select companions. Other added requirements conservatively select all eligible outputs. Changes to rendering environment settings (runner, Python, font installation, rendering commands) in the workflow select eligible outputs; artifact and trigger settings do not. The selected builder affects every output; the direct legacy builder is not used by CI. When adding a renderer input or changing how build commands are invoked, update the selector and its regression tests in the same PR.

Status-only edits check eligibility without publication. Enabling a draft preview generates its first preview. Source metadata such as review status, provenance notes, and publication references does not itself change PDF content. Editorial documentation, unused templates, unrelated stories/worksheets/slides, tests, and validation/selection logic do not trigger PDF regeneration alone. Action-label data is validation-only; current renderers do not read it.

Manual builds accept one exact eligible output filename or `all-approved`. Unknown, disabled, missing-source, or unresolved-link requests fail explicitly. Draft previews may show existing unapproved HTTPS links, with validation warnings; they do not authorize release. Every eligible draft receives the same source checks and PDF verification as approved-source review copies. `scripts/build_selected.py` rechecks eligibility before rendering. PR closure deletes its temporary preview branch through the existing cleanup workflow; source merge never publishes to Drive.
