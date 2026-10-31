# Little Chewz — start here

Prototype in chat, then choose the Python-generated PDF or external-resource workflow. [AGENTS.md](AGENTS.md) is the generated AI entry point; **[COMMANDS.md](system/COMMANDS.md) routes requests**, **[CREATE.md](system/CREATE.md) owns drafts**, **[WORKFLOW.md](system/WORKFLOW.md) owns editing/review**, and **[DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) owns all publication**.

## Quick route

- Create: **COMMANDS → CREATE**; stop at a review copy in holding.
- Update: **COMMANDS → WORKFLOW**; do not alter a verified live release.
- Publish: **DRIVE_PUBLISHING**; verify the official Drive copy before recording `published`.
- Identify IDs, links or status: **CONTENT_CONTRACT** and `catalog/resources.json`.

## Where things belong

| Location | Owns |
| --- | --- |
| [AI_RULES.md](system/AI_RULES.md) | AI routing, non-negotiable boundaries, and how instructions are maintained |
| [AGENTS.md](AGENTS.md) | **Generated** from every instruction file (`scripts/build_agents_md.py`); auto-loaded by agents and pasteable into chats. Never edit directly. |
| Each folder's `AGENTS.md` | Which instructions apply to the files in that folder |
| `content/` | Lesson wording, companions, stories, artwork, and lesson delivery status |
| `catalog/quests.json` | Navigation to quest manifests |
| `catalog/resources.json` | Stable IDs, production classification, holding/published URLs, builds and publication records |
| `catalog/drive_folders.json` | Verified holding folders (including separate Slide PDFs) and official folder configuration |
| [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) | Types, paths, version authority, statuses, source/output boundaries, and asset rules (including asset-first templates) |
| [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) | Teacher Guide writing and presentation requirements |
| [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) | Companion writing and presentation requirements |
| [action_labels.json](system/action_labels.json) | Allowed action labels and internal row types |
| [WORKFLOW.md](system/WORKFLOW.md) | Edit, validate, review, save and report; not publication |
| [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) | Slide PDF review, approval, linked-PowerPoint conversion, and in-place Drive replacement |
| [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) | Single publication owner for generated PDFs and external resources, checks and verification |
| [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) | Creating source files and transferring binary assets |
| [COMMANDS.md](system/COMMANDS.md) | Command and natural-language publication routing |
| [CREATE.md](system/CREATE.md) | Draft-only resource creation and holding-folder staging |
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

Lesson folders run from `00-activate` through `06-celebrate`. Companions live under `resources/teacher_companion/`; raw stories and letters live under `story/`. Read lifecycle status before publishing: a folder or URL does not prove its latest source is live.

## Current capabilities

- Only `generated_pdf` resources (Teacher Guides, Python-rendered companions, Welcome) use editable GitHub source branches and the authorized `/merge`→Drive checksum pipeline. Generated first release needs manual destination setup.
- `external` resources (including PDFs made outside the renderer, posters, images, worksheets and slide pairs) stay in Drive holding until an agent manually publishes and verifies them. No external `/merge` or checksum tracking.
- The new [Drive holding area](https://drive.google.com/drive/folders/1UJYL2ADO7_pfrLSK1BpzstaHCoBmx-jJ) has PDF-generated, worksheets, posters/visuals and other folders; existing Slide PDFs remain separate. Holding is not publication.
- `/create`, `/update` and `/merge` are agent instructions defined in [COMMANDS.md](system/COMMANDS.md), not Python create/update CLI programs.

- Automated builds discover authored lessons and companions through the quest catalog and registry. All valid existing sources can be previewed; registry-built documents (including Welcome) are handled the same way.
- Every existing valid source can generate a preview; five lessons without a `lesson.json` are not renderable. Previews do not publish.
- Slides are maintained per lesson under the content contract. Editable slide generation is not implemented; the **approved-PDF-to-linked-PPTX converter** is available separately (`scripts/pdf_to_linked_slides.py`). [Slide conversion standard](system/SLIDE_CONVERSION.md).
- The validator checks selected required fields, resource references, registry IDs/HTTPS destinations, covers, action labels, and step order. It checks `lesson.json`, but does not fully validate every content structure, test Drive access, or prove external content parity. An on-demand read-only inspection workflow is available.

## Local checks and previews

From the repository root, with Python 3.10+:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python -m pip install -r requirements.txt
python scripts/select_builds.py --all --output /tmp/little-chewz-build-selection.json
python scripts/build_selected.py --manifest /tmp/little-chewz-build-selection.json
```

Lato and the other fonts are bundled under `templates/`, so renders match CI. `scripts/build_selected.py` is the supported batch builder; it replaces PDFs in `exports/`, so keep review copies elsewhere. For direct iteration on a single PDF, invoke its renderer in `scripts/renderers/`.

## GitHub previews

Relevant PR updates **and merges to `main`** run validation and tests, then render only affected registered PDFs as permanent browser previews; documentation-only changes produce validation-only runs. Review links, retention, and manual runs follow [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup). [Browse PDF previews runs](https://github.com/Programmer484/little_chewz/actions/workflows/build-resources.yml).

The original inventories and superseded slideshow decisions are in [archive/2026-10/](archive/2026-10/README.md); they are not operating instructions.
