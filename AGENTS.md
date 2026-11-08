# Little Chewz — agent guide

Read the nearest folder `AGENTS.md` and task-relevant guides only. [Start here](START_HERE.md).

- **Create → Edit → Publish**: every new Drive-managed file gets a Holding file and catalogue entry (externally hosted URLs are registered without a fake Drive file) ([Create](system/CREATE.md)); draft updates and GitHub previews never change live resources ([Edit](system/EDIT.md)); only the **explicit resource IDs named by the human** may be published after approval, directly or on merge through a PR release marker; generated PDFs need no Holding copy ([Publish](system/PUBLISH.md)).
- `catalog/resources.json` owns stable IDs, Holding and Public URLs, generation mapping and publication evidence. Status is derived, not stored ([Content contract](system/CONTENT_CONTRACT.md)).
- Preserve approved story content, working links and authoring assets; never invent Drive IDs, URLs, approvals or verified checksums. A released resource cannot depend on an unpublished one. Public content uses only published links.
- Reuse the shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch for lessons; use a review branch for system work. No force-push, unrelated edits, secrets or silent live replacement.
- **Audit:** existing [Inspect](system/INSPECTION.md) runs manually on **published resources only** and reports unpublished dependencies as FAIL. It is not an automatic publisher, separate auditor or release gate.

Routes: [content](content/AGENTS.md), [catalog](catalog/AGENTS.md), [scripts](scripts/AGENTS.md), [templates](templates/AGENTS.md), [apps](apps/AGENTS.md), [Teacher Guide](system/EDITORIAL_GUIDE.md), [Companions](system/RESOURCE_GUIDELINES.md), [Slides](system/SLIDE_CONVERSION.md), [Binary transfer](system/BINARY_TRANSFER.md).

Run `python scripts/validate.py` and relevant tests; review affected PDFs and human-facing destinations. Report checks, exact file IDs and URLs, unresolved blockers, and whether publication actually occurred. For generated-PDF review give the verified Actions preview link first.
