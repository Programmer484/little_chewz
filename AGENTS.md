# Little Chewz — AI instructions

This is an editable educational source repository. PDFs are outputs; legacy PDFs are inputs only while awaiting conversion.

## Read for the task

1. Read [START_HERE.md](START_HERE.md) for navigation and current capabilities.
2. Read [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) for source ownership, status, and version authority.
3. For edits, follow [WORKFLOW.md](system/WORKFLOW.md). Read the relevant writing guide before changing content:
   - Teacher Guides: [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md).
   - Companions: [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md).
4. Locate the source through `catalog/quests.json` → `quest.json` → stage/source file. Read `catalog/resources.json` for linked names and destinations.
5. Read the relevant `scripts/renderers/` file only for layout or generation work. For file creation/transfers, read [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).

## Non-negotiable boundaries

- Use approved facts, canon, names, dialogue, activities, and resource links. Flag missing or conflicting evidence; never invent a substitute.
- Preserve review status. Uploading, merging, rendering, or a passing check does not approve teaching content or authorize publication.
- Edit the owning source; do not duplicate resources inside Teacher Guides. Keep required PDF images versioned in GitHub.
- Keep content, visual changes, and publishing actions distinct. Preserve the published seven-slide Activate asset; historical quest-wide slide numbers are not current lesson numbers.
- Save edits through a pushed PR and verify the remote result. Follow the workflow through merge and cleanup when authorized. Preserve unrelated user work.

## Maintaining instructions

- Treat “from now on” and equivalent requests as lasting rules; keep one-time requests within the task. Record lesson-specific decisions in that lesson's existing source/status metadata.
- Find the rule's owner in `START_HERE.md`. Update it there; replace superseded wording and link from other documents instead of copying the rule.
- State the scope, required behavior, and any necessary exception. Use direct instructions and keep examples only when they clarify a decision.
- Search for conflicts and stale references. Update affected templates or behavior within the authorized scope; record remaining work explicitly.
- Keep editorial judgment in prose, shared values in their existing data files, and objective checks in `scripts/validate.py`. Do not add unused enforcement files or speculative tooling.
- Apply explicit user decisions within their scope. If conflicting instructions would change approval, publication, or content meaning and intent is unclear, flag the conflict and continue independent work.
- Report where the rule was saved, what now enforces it, and any existing materials still needing updates. Do not silently rewrite or publish the whole collection.
