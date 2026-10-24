# Little Chewz — start here

Edit the source, review the generated document, then publish only when authorized. [AGENTS.md](AGENTS.md) is the AI entry point; [WORKFLOW.md](system/WORKFLOW.md) owns the editing and delivery routine.

## Where things belong

| Location | Owns |
| --- | --- |
| [AGENTS.md](AGENTS.md) and each folder's `AGENTS.md` | AI routing: which instructions apply to which files |
| [AI_BRIEF.md](AI_BRIEF.md) | Generated copy of every instruction file, for pasting into AI chats (`scripts/build_ai_brief.py`) |
| `content/` | Lesson wording, companions, stories, artwork, and local review status |
| `catalog/quests.json` | Navigation to quest manifests |
| `catalog/resources.json` | Authoritative linked names, stable resource IDs, and approved destinations |
| [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) | Types, paths, version authority, statuses, source/output boundaries, and asset rules (including asset-first templates) |
| [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) | Teacher Guide writing and presentation requirements |
| [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) | Companion writing and presentation requirements |
| [action_labels.json](system/action_labels.json) | Allowed action labels and internal row types |
| [WORKFLOW.md](system/WORKFLOW.md) | Edit, validate, review, save, merge, publish, and report |
| [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) | Slide PDF review, approval, linked-PowerPoint conversion, and in-place Drive replacement |
| [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) | Manual **Publish to Drive** workflow: in-place replacement of approved PDFs, service-account setup |
| [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) | Creating source files and transferring binary assets |
| `templates/` | Templates for supported lesson, companion, and raw-story sources, plus the `claude` page style (clean pages and quest navigation) |
| `scripts/validate.py` | Implemented automatic content checks |
| `scripts/renderers/` | Shared PDF layout and generation code |
| `scripts/select_builds.py`, `scripts/build_selected.py` | Select and build affected eligible PDF previews |
| `tests/` | Checks for the tools |
| `.github/workflows/` | Automated validation and retained PDF previews after PR updates and `main` merges |
| `exports/` | Generated PDFs; never the editable source |
| [SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md) | Tooling backlog; each entry records its implementation status |

## Find a lesson

Follow `catalog/quests.json` → the quest's `quest.json` (lesson status and folder) → `lessons/<stage>/lesson.json` when it exists. An optional short `stage.json` is historical provenance only, not a status owner. The current quest lives at `content/confetti-cake-cottage/quest-01-bake-off-betrayal/`.

Lesson folders run from `00-activate` through `06-celebrate`. Companions live under `resources/teacher_companion/`; raw stories and letters live under `story/`. Read lifecycle status before publishing: a folder's existence does not mean its material is approved.

## Current capabilities

- Automated builds discover authored lessons and companions through the quest catalog and registry. Only `approved` or `published` items enter approved-only builds. Registry entries with a `build` renderer (currently the Welcome PDF) are discovered the same way. Current approved-only outputs: Activate Teacher Guide, Welcome, Mission Video Questions, and Confetti File Questions.
- Every existing valid source can generate a preview: Set the Table and Songwriting Extension are unapproved; five lessons without a `lesson.json` are not renderable. Previews do not publish.
- Slides are maintained per lesson under the content contract. Editable slide generation is not implemented; the **approved-PDF-to-linked-PPTX converter** is available separately (`scripts/pdf_to_linked_slides.py`). [Slide conversion standard](system/SLIDE_CONVERSION.md).
- The validator checks selected required fields, resource references, registry IDs/HTTPS destinations, covers, action labels, and step order. It checks `lesson.json`, but does not fully validate every content structure, test Drive access, or grant editorial approval.

## Local checks and approved previews

From the repository root, with Python 3.10+:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python -m pip install -r requirements.txt
python scripts/select_builds.py --all --output /tmp/little-chewz-build-selection.json
python scripts/build_selected.py --manifest /tmp/little-chewz-build-selection.json
```

Teacher Guide rendering requires installed Lato fonts. `scripts/build_selected.py` is the supported batch builder; it replaces PDFs in `exports/`, so keep review copies elsewhere. For direct iteration on a single PDF, invoke its renderer in `scripts/renderers/`.

## GitHub previews

Relevant PR updates **and merges to `main`** run validation and tests, then render only affected registered PDFs as permanent browser previews; documentation-only changes produce validation-only runs. Review links, retention, and manual runs follow [WORKFLOW.md](system/WORKFLOW.md#preview-links-and-retention). [Browse PDF previews runs](https://github.com/Programmer484/little_chewz/actions/workflows/build-resources.yml).

The original inventories and superseded slideshow decisions are in [archive/2026-10/](archive/2026-10/README.md); they are not operating instructions.
