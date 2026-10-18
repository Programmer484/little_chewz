# Little Chewz — Mandatory AI instructions

You are editing a **source-first educational content repository**, not a PDF as the source of truth.

## Read in this order

1. `START_HERE.md` for navigation and system intent.
2. `system/CONTENT_CONTRACT.md` for types, paths, and version rules.
3. `system/EDITORIAL_GUIDE.md` and, for companions, `system/RESOURCE_GUIDELINES.md`.
4. `catalog/quests.json` -> targeted `quest.json` -> editable lesson/resource file.
5. `catalog/resources.json` for the only authoritative URLs and linked names.
6. Relevant renderer in `scripts/renderers/` **only if editing layout/generation**.

## Hard rules

- Use **only** approved source facts, canon, names, dialogue, existing activities, and approved resource URLs. Do not extrapolate or create 'missing' worksheets.
- `status: migration_needed` or `status: draft_transcription` means NOT APPROVED for final teaching/publishing. Never silently upgrade it.
- Edit lesson-level text/steps in `content/**/lessons/**/lesson.json`; companion blocks in `content/**/resources/**.json`; stories and raw letters in Markdown.
- Single content owner: Never duplicate whole resource text inside the teacher flow. Teacher Guide links to resources by stable ID; slideshow navigation uses slide numbers only.
- PDFs are generated exports, **except a legacy PDF still waiting to be converted**. Visual artwork belongs in image assets; links belong in the registry. Don't copy large PDFs into this edit-source package.
- Use **one continuous slideshow per quest**, with stable continuous numbering. The live seven-slide Activate export is a legacy segment; do not conflate it with the approved completed continuous quest deck. Later slide ranges remain unverified until the continuous deck is reconciled.
- Missing, stale, or unapproved links MUST be flagged; never invent URLs or quietly fall back to unlinked text.
- Preserve teacher-guide structure and exact approved editorial rules described in `system/EDITORIAL_GUIDE.md`.
- Use `system/action_labels.json` as the single authority for action vocabulary (renderer and validator must consult the same list when validation applies).
- Separate **content changes** from **visual design changes** and **publishing actions**; verify the regenerated document before publication.

## Required output from each future AI edit

State: files edited; source and review status; validation result; generated outputs; remaining unresolved issues. If changing the published Drive PDF, document the exact file ID and confirm it was replaced in place.
