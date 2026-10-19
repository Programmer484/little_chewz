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
