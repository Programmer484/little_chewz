# Editing the catalog

- `resources.json` is the single owner of every linked resource's name, Drive URL, status, and (for built documents) `build` instructions. Its keys are the stable resource IDs. Rules: [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#resources-slides-and-assets) and [lifecycle status](../system/CONTENT_CONTRACT.md#lifecycle-status).
- Never guess or invent a URL. A missing or unverified destination blocks release; flag it.
- Use only delivery statuses `unpublished`, `pending_publish`, `published`; no editorial approval flag. A verified Drive replacement sets `published`; newer `main` output with an older live destination is `pending_publish`. Publishing: [DRIVE_PUBLISHING.md](../system/DRIVE_PUBLISHING.md) or [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md).
- `quests.json` is a navigation index to each quest's `quest.json`, which owns lesson status.

Run `python scripts/validate.py` after any edit; it checks IDs, statuses, HTTPS destinations, and every reference.
