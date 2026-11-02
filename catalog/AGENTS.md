# Editing the catalogue

- `resources.json` owns stable linked-resource IDs, production type, provenance, holding and official URLs, build mapping, publication evidence and linked-resource delivery status. See [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states).
- Use `generated_pdf` only for existing Python-rendered PDF outputs with GitHub editable sources and explicit `build`. Externally authored PDFs remain `external`, as do slides and image-based resources.
- `drive_folders.json` owns four holding category folder IDs mirroring the official Drive layout; existing nested subfolders retain their IDs. Legacy Slide PDF originals remain separate. Never invent file or folder IDs. A holding file is not published **even when its permanent URL will be unchanged**.
- [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) owns status definitions; **[PUBLISH.md](../system/PUBLISH.md) alone owns the actions and verification that permit recording `published`**. Legacy records can remain explicitly unverified. Add `human_review: {"<exact URL>": "pending"}` for non-Drive links and externally owned Drive links; set to `reviewed` only after the human checks that same URL.
- Published resources always render their `published_url`, in both review and release PDFs. Draft previews may use a genuine holding link; non-slide published resources must have `holding_url: null`. Release builds require every referenced resource to have `status: published` and an official URL.
- `quests.json` indexes quest manifests; each quest's `quest.json` owns lesson-source delivery status, separate from linked resource status.

Follow [CREATE.md](../system/CREATE.md) for new drafts, [UPDATE.md](../system/UPDATE.md) for revisions, and [PUBLISH.md](../system/PUBLISH.md) for release; [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) owns slide-specific conversion. Run `python scripts/validate.py` after changes.
