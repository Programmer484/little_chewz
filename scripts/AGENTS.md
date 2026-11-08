# Editing tooling

| File | Purpose | Read first |
| --- | --- | --- |
| `renderers/teacher_guide.py` | Teacher Guide PDF layout | [EDITORIAL_GUIDE.md §7](../system/EDITORIAL_GUIDE.md#7-generator-engineering-boundaries) |
| `renderers/teacher_companion.py` | Companion PDF layout | [RESOURCE_GUIDELINES.md](../system/RESOURCE_GUIDELINES.md#presentation) |
| `renderers/welcome.py` | Welcome page style | [templates/welcome/README.md](../templates/welcome/README.md) |
| `renderers/celebrate.py` | Celebrate Teacher Guide (invitation, party sizes, finale) | [templates/celebrate/README.md](../templates/celebrate/README.md) |
| `select_builds.py`, `build_selected.py` | Explicit generated-PDF output mappings and previews | [Edit](../system/EDIT.md) |
| `validate.py` | Objective source, template, and registry checks | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) |
| `publication_state.py` | One derived publication-state rule and read-only resource/lesson reports (`python scripts/publication_state.py --lessons`) | [CONTENT_CONTRACT.md](../system/CONTENT_CONTRACT.md) |
| `publish_to_drive.py` | Generated-PDF in-place Drive replacement/checksum, one or many IDs or a release marker; run by **Actions → Publish** | [PUBLISH.md](../system/PUBLISH.md) |
| `inspect_publications.py` | Read-only Drive permission / exact-URL human-review audit of published resources | [INSPECTION.md](../system/INSPECTION.md) |
| `pdf_to_linked_slides.py` | Human-reviewed slide PDF to linked PPTX | [SLIDE_CONVERSION.md](../system/SLIDE_CONVERSION.md) |

PDF previews and releases use official `published_url` whenever present, and draft previews use holding links otherwise. `publication_checks.py` rejects release dependencies without an official URL; `publish_to_drive.py` (agent-run or **Actions → Publish**) rejects unpublished dependencies without invoking the separate published-resource audit as a pre-publish gate. `publication_state.py` derives resource status from distinct external holding URLs or generated-PDF MD5 parity. Only Python-generated PDFs use the build pipeline. Publishing happens only for human-named IDs: a manual **Publish** run or a merged PR that added `.github/resource-releases/<PR>.json`; other CI events and merges never publish. Agents handle explicit human-directed Holding moves or in-place public replacements.

New PDF blocks still need rendering logic, but no dependency registration: `select_builds.py` discovers existing local file paths from nested JSON values and conservatively rebuilds for unknown potential inputs. Keep asset paths in source JSON and run `python scripts/validate.py` plus relevant checks after tooling changes.
