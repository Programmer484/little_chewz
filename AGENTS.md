# Little Chewz — agent instructions

Read only the instructions relevant to the files and task you are changing. Folder `AGENTS.md` files route to the owning guides; do not load every guide by default.

## Non-negotiable rules

- Edit authoritative sources, not generated PDFs. Preserve approved story text, lesson canon, names, and existing working links; do not invent facts, IDs, Drive locations or approvals.
- `catalog/resources.json` owns stable resource IDs, official/holding URLs and publication evidence. Publication status is **derived**, never stored. See [content contract](system/CONTENT_CONTRACT.md).
- **Creating, editing, previews and ordinary merges do not publish.** Only publish an explicitly approved exact version through [PUBLISH.md](system/PUBLISH.md), with existing Drive identity, access and checksum checks. Never replace a live Drive file during editing.
- Keep images/assets committed alongside editable text; never rasterize an entire editable page. Do not expose secrets or upload unapproved content.
- Reuse the shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch for lesson work unless instructed otherwise. Reconcile remote changes; never force-push or overwrite unrelated work.

## Read by task

- **New or existing resources:** [EDIT.md](system/EDIT.md); [WORKFLOW.md](system/WORKFLOW.md) for review and previews.
- **Publication or official Drive changes:** [PUBLISH.md](system/PUBLISH.md) and [INSPECTION.md](system/INSPECTION.md). This is a separate authorization step.
- **Lesson/stories/companions:** [content/AGENTS.md](content/AGENTS.md); **resource data:** [catalog/AGENTS.md](catalog/AGENTS.md).
- **Renderers, validation, releases:** [scripts/AGENTS.md](scripts/AGENTS.md); **templates:** [templates/AGENTS.md](templates/AGENTS.md); **apps:** [apps/AGENTS.md](apps/AGENTS.md).
- **Editorial standards:** [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) for Teacher Guides; [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) for companions; [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) for slides.
- **Binary/connector transfers:** [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).

## Finish the work

- Check the relevant files and current remote branch before editing. Run `python scripts/validate.py` plus relevant checks; inspect affected PDF previews and links when applicable.
- Update a rule in **one owning guide**, link to it elsewhere, and remove superseded guidance. Don't embed instruction paragraphs in JSON or maintain a generated root guide.
- Report the committed changes, GitHub Actions run, any unresolved uncertainty and whether publication occurred. Give the verified Actions run URL first for PDF review.
