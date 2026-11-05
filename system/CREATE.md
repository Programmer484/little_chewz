# Create — stage an identity

**Every Drive-managed file starts with one Holding Drive file and one catalogue entry.** A prototype is enough; creation is not editorial approval or publication. Externally hosted URLs (YouTube videos and web apps) are not Drive files: register their IDs and publish their actual URLs only after exact-link human approval.

1. Check `catalog/resources.json` for an existing ID; reuse it instead of creating a duplicate.
2. Choose its stable ID, title, published-folder `type`, and the corresponding **permitted Holding folder** in `catalog/drive_folders.json`.
3. Create/upload a real file in Holding and read back its exact Drive ID, MIME type, parent and URL. Contents may be provisional, but the file's **format must be compatible with the final deliverable**: a PDF placeholder is unsuitable for a future PPTX or Google-native file.
4. Register `title`, `type`, `holding_url` and `published_url: null` in `catalog/resources.json`. A future generated PDF **does not need `pdf` metadata or source JSON yet**; add those at first Edit.
5. Save the catalogue change on the owning review branch and run `python scripts/validate.py`. Report the Holding URL and resource ID.

For an external-link-only resource, register its ID, title, type and both URLs as null while preparing it; do not invent a Holding Drive file. No status flag, automatic publication, dummy public URL or approval is created. Continue in [Edit](EDIT.md). Use [Binary transfer](BINARY_TRANSFER.md) only for GitHub connector binary transfers.
