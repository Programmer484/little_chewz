# Little Chewz — agent guide

Read the nearest folder `AGENTS.md` for changed files, then only guides relevant to the task. [Project map](START_HERE.md).

## Guardrails

- Edit authoritative JSON, text and assets—not generated PDFs. Preserve verified canon, approved stories and working links; never invent facts, file IDs, Drive URLs or approvals.
- `catalog/resources.json` owns resource identities, URLs and publication evidence. Status is **derived**, not stored ([contract](system/CONTENT_CONTRACT.md)).
- **Editing, holding uploads, previews and ordinary merges never publish.** Official Drive changes require human approval of the exact version and checks in [PUBLISH.md](system/PUBLISH.md). Never replace live files while editing.
- Reuse the shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch unless told otherwise. Reconcile remote work; never force-push, overwrite unrelated edits, expose secrets or upload unapproved content.

## Read for the task

- **Create/revise:** [EDIT.md](system/EDIT.md) and [WORKFLOW.md](system/WORKFLOW.md).
- **Publish/Drive access:** [PUBLISH.md](system/PUBLISH.md), [INSPECTION.md](system/INSPECTION.md).
- **Lessons, stories, companions:** [content/AGENTS.md](content/AGENTS.md); **catalogue:** [catalog/AGENTS.md](catalog/AGENTS.md).
- **Code/renderers:** [scripts/AGENTS.md](scripts/AGENTS.md); **templates:** [templates/AGENTS.md](templates/AGENTS.md); **apps:** [apps/AGENTS.md](apps/AGENTS.md).
- **Editorial:** [Teacher Guide](system/EDITORIAL_GUIDE.md), [companions](system/RESOURCE_GUIDELINES.md), [slides](system/SLIDE_CONVERSION.md).
- **File transfers:** [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).

## Complete the task

Check the owning source and latest branch; run `python scripts/validate.py` and relevant checks. Inspect affected PDFs and links. Keep each rule in one owning guide rather than duplicating it in JSON or other guides. Report changes, verified Actions run, blockers and whether publication occurred; lead PDF reviews with the Actions URL.
