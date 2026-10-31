# Editing the catalogue

- `resources.json` owns stable linked-resource IDs, production type, provenance, holding and official URLs, build mapping, publication evidence and linked-resource delivery status. See [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states).
- Use `generated_pdf` only for existing Python-rendered PDF outputs with GitHub editable sources and explicit `build`. Externally authored PDFs remain `external`, as do slides and image-based resources.
- `drive_folders.json` owns verified review-holding folder IDs. The existing Slide PDFs area remains separate. Never invent file IDs, URLs, statuses or folder IDs; a `holding_url` must never be treated as `published_url`.
- [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) owns status definitions; **[DRIVE_PUBLISHING.md](../system/DRIVE_PUBLISHING.md) alone owns the actions and verification that permit recording `published`**. Legacy records can remain explicitly unverified.
- The compatibility `url` is used by existing Teacher Guides; preserve established live links and never redirect them to a holding file.
- `quests.json` indexes quest manifests; each quest's `quest.json` owns lesson-source delivery status, separate from linked resource status.

Follow [CREATE.md](../system/CREATE.md) for drafts, [DRIVE_PUBLISHING.md](../system/DRIVE_PUBLISHING.md) for release, and [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) for slide pairs. Run `python scripts/validate.py` after changes.
