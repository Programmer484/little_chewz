# First-time resource creation

This procedure follows **`/create` after a prototype already exists** in the AI conversation.

1. Identify the resource's school, quest, lesson and type. Search existing IDs and Drive records; reuse an existing identity rather than duplicating it. Choose a new stable resource ID only when genuinely new.
2. Create/reuse its `edit/<stable-resource-id>` branch based on latest `main`. Follow the source's `$instructions` and supported template. Commit editable content and separate required assets to GitHub; avoid output-only PDFs as editable source. For binary transfers follow [CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md).
3. Reserve the item in `catalog/resources.json` with type, title, tags and status `unpublished`; do not guess a Drive URL or folder ID. A lesson's status lives in its `quest.json`. Validate the source and provide the GitHub preview.
4. Continue iterations through `/update` on the same branch. On `/merge`, reconcile and merge, build the accepted `main` version, determine the actual appropriate Drive lesson/quest folder from existing Drive records, create the first file there, verify its ID/type/access, and only then register the URL and mark `published`.
5. If Drive folder, permissions, build output, or verification is missing, keep `unpublished` and report it. For existing resources, never create a duplicate: replace in place and preserve file IDs and sharing.

**Not implemented yet:** automated first-time Drive creation and the merge orchestrator. This is the required agent workflow; do not claim unsupported operations ran.