# Little Chewz — start here

The resource lifecycle has **three explicit actions**: [Create](system/CREATE.md) → [Edit](system/EDIT.md) → [Publish](system/PUBLISH.md). [AGENTS.md](AGENTS.md) is the short entrypoint; [Content contract](system/CONTENT_CONTRACT.md) owns identities, catalogue fields and derived publication states.

**Create:** register a real Holding Drive file of the right format and its stable catalogue ID; contents may be a prototype. Externally hosted URLs (YouTube/web apps) have catalogue identities but no Drive file to stage or move.

**Edit:** iterate generated PDFs from editable JSON in GitHub Actions previews; other files in chat/native tools. The GitHub preview is the review copy for generated PDFs; stage other files' final candidate in Holding for human review of content/links. Don't modify live resources while editing.

**Publish:** merging a PR into `main` automatically republishes every already-live generated PDF it affects (`[no publish]` in the title skips this); anything else only when the human names exact IDs, in chat or **Actions → Publish**. First-time Drive files move Holding → Public **with the same Drive ID and URL**; external URLs are recorded only after exact-link approval. Revisions replace the established public file in place. Publish all dependencies first; never publish a PDF that references an unpublished resource. No scheduled or catalogue-based publication.

**Audit:** the existing [Inspect Action](https://github.com/Programmer484/little_chewz/actions/workflows/inspect-publications.yml) is on demand and read-only. It checks published resources only, rejecting unpublished dependencies of a published parent. It does not replace human destination review or gate publication.

## References

- `catalog/resources.json`: IDs, Holding/Public URLs, optional explicit dependency IDs, generated-PDF checksum/revision.
- `catalog/drive_folders.json`: verified permitted Holding/Public folder destinations.
- `catalog/quests.json` → quest manifest → lesson JSON: lesson content and order.
- `templates/`, `scripts/renderers/`: shared generated-PDF source and layout.
- [Editorial](system/EDITORIAL_GUIDE.md), [Companions](system/RESOURCE_GUIDELINES.md), [Slides](system/SLIDE_CONVERSION.md), [Binary transfer](system/BINARY_TRANSFER.md): specialist runbooks.

Use the shared lesson branch for its resources. `exports/` contains generated files, not editable source. GitHub PRs and main updates run validation and affected PDF previews; previews **never publish**. Only the **Publish** Action (on merge, or for human-named IDs) changes live files.

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python -m pip install -r requirements.txt
python scripts/select_builds.py --all --output /tmp/selection.json
python scripts/build_selected.py --manifest /tmp/selection.json
```

[PDF preview Action](https://github.com/Programmer484/little_chewz/actions/workflows/build-resources.yml). `scripts/publish_to_drive.py` is a manual, explicit-ID helper for already-published generated PDFs only.
