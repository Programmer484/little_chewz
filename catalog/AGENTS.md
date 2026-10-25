# Editing the catalogue

- `resources.json` owns stable linked-resource IDs, production type, provenance, holding and official URLs, build mapping, publication evidence and linked-resource delivery status. See [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states).
- Use `generated_pdf` only for existing Python-rendered PDF outputs with GitHub editable sources and explicit `build`. Externally authored PDFs remain `external`, as do slides and image-based resources.
- `drive_folders.json` owns verified review-holding folder IDs. The existing Slide PDFs area remains separate. Never invent file IDs, URLs, statuses or folder IDs; a `holding_url` must never be treated as `published_url`.
- Delivery states are `unpublished`, `pending_publish`, `published`. Generated PDFs use exact Drive checksum confirmation after an authorized PDF `/merge`; external resources are published by agents and recorded only after live verification. Legacy records may remain explicitly unverified.
- The compatibility `url` is used by existing Teacher Guides; preserve established live links and never redirect them to a holding file.
- `quests.json` indexes quest manifests; each quest's `quest.json` owns lesson-source delivery status, separate from linked resource status.

Follow [CREATE.md](../system/CREATE.md), [DRIVE_PUBLISHING.md](../system/DRIVE_PUBLISHING.md), and [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) as appropriate. Run `python scripts/validate.py` after changes.
