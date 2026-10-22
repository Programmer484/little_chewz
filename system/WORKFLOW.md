# Editing and delivery workflow

Applies to source, instruction, and tooling edits. Existing user authorization carries through the task; do not ask again for an already authorized action.

## Routine

1. **Inspect.** Check the working tree and remote state. Read the task's owning instructions and source/status records. Identify whether the request changes content, presentation, tooling, or publication.
2. **Edit.** Multiple AIs can work simultaneously, using separate task branches and PRs. Edit the owning files and preserve unrelated changes. Before merging, compare against the latest `main` and reconcile parallel edits to avoid overwriting another AI's work. For new resources, use the matching template, assign a stable ID, and record source/status and blockers in existing metadata.
3. **Verify.** Review the diff and run `python scripts/validate.py`. Run relevant tool tests for code changes. For document changes, build only affected supported outputs and inspect pages, text, artwork, and hyperlinks. **Generate Teacher Guide review copies with the repository renderer, including draft sources (`python scripts/renderers/teacher_guide.py --content <lesson.draft.json> --output <review.pdf>`); never use an independent ad-hoc layout script.** Drafts remain review-only and are not automatically covered by approved-output CI builds. Check changed instructions for conflicting rules, obsolete paths, and broken local links. Report check limits; do not imply unregistered drafts were validated or rendered.
4. **Save.** Commit and push all intended source changes and required assets; exclude secrets and temporary/generated files. Verify the remote branch contains the commits. Open a draft PR if unfinished, or a review PR if ready, with checks and remaining blockers. Local files, commits, attachments, and PR descriptions alone are not saved GitHub source.
5. **Finish.** The user prefers **merge-first, reconcile-on-`main`**. When authorized and checks pass, merge the PR promptly, verify `main` contains its intended changes and preserves concurrent updates, and review the resulting `main` Actions run. Do not delay an authorized merge just to preserve a temporary preview link. Otherwise leave the pushed PR and blockers stated. Unapproved draft source may be merged if authorized; retain its status and keep it excluded from approved-output builds.
6. **Clean up.** Do **not** automatically delete GitHub PDF preview branches when PRs merge or close. Never merge `pdf-preview-run-*` (or legacy `pdf-preview-pr-*`) into `main`. Manual preview cleanup requires explicit user instruction. Source-branch cleanup is separate: preserve any unmerged work, check for commits added after squash merges, and synchronize local `main` safely.

## Preview links and retention

- Give the **actual GitHub Actions run URL** (`https://github.com/Programmer484/little_chewz/actions/runs/<run-id>`) as the **default first link** for PDF reviews. Prefer the relevant successful **post-merge `main` push run**, reflecting the combined AI edits. Use the PR run if it is the latest verified run and `main` has not generated a preview. For validation-only or failed runs, say so; never imply that a PDF exists. Never reuse an old example run for new work.
- The run summary links to browser PDFs on **run-specific retained** `pdf-preview-run-<run-id>` branches. Direct PDF links can follow the run URL; do not lead with a PR Files tab or generated-branch link. Source merge and PDF preview are not teaching-content approval or Drive publication.
- **No automatic preview-branch deletion** on PR closure or merge. Branches stay for historical review, with manual pruning only on request. Workflow artifacts expire after **seven days**, but browser previews stay accessible.

## Publication is separate

- A source merge does not approve content, register a build target, or authorize Drive publication. Follow the status rules in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md).
- Publish only within explicit authorization, after source approval and review of the exact regenerated output. Resolve missing, stale, or unapproved links first; verify intended access.
- When updating a published Drive PDF, replace the existing file in place to preserve its ID. Do not rename, duplicate, merge, or republish live assets as a side effect of source maintenance.
- Register a new approved destination in `catalog/resources.json` after publication. Preserve stable IDs for existing resources.

## Classroom slide PDF to PowerPoint

The [slide conversion standard](SLIDE_CONVERSION.md) is the technical companion to this workflow. This is a **human-approved publication path**, separate from the unimplemented editable-slide generator.

1. **Human PDF editing.** The human downloads the lesson-specific PDF from the [Slide PDFs folder](https://drive.google.com/drive/u/0/folders/1Qryh6aiuHsZqiTpzP_BvulK-W43EK45g). Human and AI iterate using the revised PDF; it is the review artifact. Keep lesson-local slides separate. Inspect its page count, order, content, external media links, and link hotspots against the lesson's current review record. The PowerPoint is **not** the editing source.
2. **Approval gate.** Do not update Drive while iterating. The human must explicitly approve the **exact final PDF** and intended lesson. A past approval, GitHub merge, generated PPTX, or successful conversion check is not approval of a changed PDF. Resolve any slide-count or content disagreement before publishing.
3. **Generate and validate.** Run `python scripts/pdf_to_linked_slides.py approved.pdf -o approved.pptx --json conversion-report.json`. Keep full-slide images (nonselectable text), faithfully restore PDF hyperlinks as transparent clickable hotspots, and require zero dropped links, matching slide/page count, and visual inspection. For tiny type use `--scale 2 --quality 94`. Do not silently replace missing link actions.
4. **Replace both existing Drive files directly.** Confirm the expected target IDs/MIME types in `catalog/resources.json` and current Drive metadata. Use binary **in-place update** of the existing PDF in the Slide PDFs folder, and of its paired existing **`.pptx` PowerPoint file** (not a copy, new file, or native Google Slides conversion). Preserve both original Drive file IDs, location, and sharing. A missing PPTX destination is a blocker, not permission to invent a new one. Stage/check both deliverables before replacing either.
5. **Read back and test.** Verify both IDs and MIME types are unchanged, both new versions are retrievable, slide count/visuals match, and every distinct link works in PowerPoint and when presenting in Google Slides. If one update fails, report the partial publication and explicitly restore/retry as appropriate. Report the exact updated IDs and final approval scope.

Do not promote lesson/source review statuses or mark a link approved just because a PDF/PPTX was uploaded; those changes require their own human approval. Editable slide JSON rendering and CI builds remain future work.

## Completion report

State concisely:

- Files changed and source/review status.
- Checks, generated outputs, and remaining issues.
- **Actions run URL first** for PDF previews (prefer post-merge `main`); then commit/PR link and whether `main` was verified.
- Any unsaved work, remaining PRs, unpushed commits, local-only source/assets, or cleanup failures. Never claim all work is saved if verification failed.
- For a published Drive replacement: exact file ID and confirmation of replacement in place.

## PDF build selection

Run source validation and tool tests for relevant PR updates **and pushes to `main`**, including tests and tooling. Render a review PDF only when one of its actual inputs changes or it is explicitly requested. PR selection compares the complete proposal against its base; `main` selection compares the before/after push commits. Generation never changes source content, grants editorial approval, merges a PR, or publishes to Drive.

`scripts/select_builds.py` discovers lessons through `catalog/quests.json` → `quest.json` → stage/source records, and companions in those quests. Approved lessons require approved quest and stage statuses (and source status when present). Approved companions require `review_status: approved_source`. To enable an unapproved lesson preview, set `preview_enabled: true` in its existing `stage.json` and name its `lesson_source`; for a companion, set the flag in its source. Do not change approval status to enable a preview. Incomplete drafts without opt-in remain excluded. Set the Table is opted in; its outstanding editorial and resource-link blockers remain.

Sources and their local cover artwork select only their own outputs. Shared renderers select their eligible consumers. Resource-registry changes select only documents referencing changed IDs; external Drive edits without a registry change do not trigger a build. PyMuPDF changes select guides; ReportLab changes select companions. Other added requirements conservatively select all eligible outputs. Changes to rendering environment settings (runner, Python, font installation, rendering commands) in the workflow select eligible outputs; artifact and trigger settings do not. The selected builder affects every output; the direct legacy builder is not used by CI. When adding a renderer input or changing how build commands are invoked, update the selector and its regression tests in the same PR.

Status-only edits check eligibility without publication. Enabling a draft preview generates its first preview. Source metadata such as review status, provenance notes, and publication references does not itself change PDF content. Editorial documentation, unused templates, unrelated stories/worksheets/slides, tests, and validation/selection logic do not trigger PDF regeneration alone. Action-label data is validation-only; current renderers do not read it.

Manual builds accept one exact eligible output filename or `all-approved`. Unknown, disabled, missing-source, or unresolved-link requests fail explicitly. Draft previews may show existing unapproved HTTPS links, with validation warnings; they do not authorize release. Every eligible draft receives the same source checks and PDF verification as approved-source review copies. `scripts/build_selected.py` rechecks eligibility before rendering. Each PDF-rendering Actions run saves a unique, retained browser preview branch. PR closure or merging does not delete it; source merge never publishes to Drive.
