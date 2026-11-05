# Little Chewz — start here

Prototype in chat, then follow the **independent workflow matching the action**. [AGENTS.md](AGENTS.md) is the short AI entry point. Shared definitions and checks are in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) and [WORKFLOW.md](system/WORKFLOW.md).

## Choose a workflow

- **[Edit](system/EDIT.md):** for new or existing resources. Check for an existing stable ID, edit the source, stage a review copy in holding and preserve the live release. Do not publish.
- **[Publish](system/PUBLISH.md):** after explicit human authorization, deliver the exact reviewed resource, verify the official Drive file, then save the official URL and approved checksum; resource status derives automatically. Existing generated PDFs use a guarded release-PR merge within this workflow.

Use one `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch per lesson unless you explicitly request a separate task branch. No chat slash-command integration exists; ordinary GitHub merges and previews do not publish.

## Where things belong

| Location | Owns |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Small agent entry point: universal safeguards and task routing; edited directly. |
| Each folder's `AGENTS.md` | Which instructions apply to the files in that folder |
| `content/` | Lesson order, wording, companions, stories and artwork (no stored lesson publication status) |
| `catalog/quests.json` | Navigation to quest manifests |
| `catalog/resources.json` | Stable IDs, production classification, holding/published URLs, builds and publication records |
| `catalog/drive_folders.json` | Verified holding folders (including separate Slide PDFs) and official folder configuration |
| [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) | Types, paths, version authority, statuses, source/output boundaries, and asset rules (including asset-first templates) |
| [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) | Teacher Guide writing and presentation requirements |
| [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) | Companion writing and presentation requirements |
| [action_labels.json](system/action_labels.json) | Allowed action labels and internal row types |
| [WORKFLOW.md](system/WORKFLOW.md) | Shared validation, preview, and review/reporting conventions |
| [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) | Slide PDF review, approval, linked-PowerPoint conversion, and in-place Drive replacement |
| [PUBLISH.md](system/PUBLISH.md) | Single publication owner for generated PDFs and external resources, checks and verification |
| [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) | Creating source files and transferring binary assets |
| [EDIT.md](system/EDIT.md) | New and existing resource editing, holding staging, and review |
| `templates/` | One folder per content template (`teacher_guide`, `teacher_companion`, `activity_guide`, `option_overview`, `welcome`); each `TEMPLATE.json` is copied to start a source, which keeps its `"template"` field |
| `scripts/validate.py` | Implemented automatic content checks |
| `scripts/renderers/` | Shared PDF layout and generation code |
| `scripts/select_builds.py`, `scripts/build_selected.py` | Select and build affected eligible PDF previews |
| `tests/` | Checks for the tools |
| `.github/workflows/` | Automated validation and retained PDF previews after PR updates and `main` merges |
| `exports/` | Generated PDFs; never the editable source |
| `apps/` | Standalone teacher web apps, such as the [Print Pack Builder](apps/print-pack-builder/README.md); read-only consumers of the catalogue, never publishers |
| [SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md) | Tooling backlog; each entry records its implementation status |

## Find a lesson

Follow `catalog/quests.json` → the quest's `quest.json` (lesson order and folder) → `lessons/<stage>/lesson.json` when it exists. Derive each lesson's publication state from its registered Teacher Guide in `catalog/resources.json`, using `python scripts/publication_state.py --lessons`. The current quest lives at `content/confetti-cake-cottage/quest-01-bake-off-betrayal/`.

Lesson folders run from `00-activate` through `06-celebrate`. Companions live under `resources/teacher_companion/`; raw stories and letters live under `story/`. Derive lifecycle status from official URL / holding URL or generated checksum before publishing: a folder or URL does not prove its latest source is live.

## Current capabilities

- Only resources with a `pdf` object (Teacher Guides, Python-rendered companions, Welcome) use editable GitHub branches and an authorized release-PR merge/checksum pipeline. First release needs manual destination setup.
- Resources without `pdf` (including externally authored PDFs, posters, images, worksheets and slides) stay in holding until an agent manually publishes and verifies them. No automatic external release or checksum tracking.
- [Drive holding](https://drive.google.com/drive/folders/1UJYL2ADO7_pfrLSK1BpzstaHCoBmx-jJ) now mirrors the official four categories: `01_TEACHER_GUIDES`, `02_CLASSROOM_SLIDES`, `03_STUDENT_MATERIALS`, `04_TEACHER_RESOURCES`. Existing subfolders retain their Drive IDs; legacy Slide PDF originals remain in their separate review folder. Holding is not publication.
- Use Edit and Publish workflow documents directly; no chat slash commands are configured.

- Automated builds discover authored lessons and companions through the quest catalog and registry. All valid existing sources can be previewed; registry-built documents (including Welcome) are handled the same way.
- Every existing valid source can generate a preview; stages without a `lesson.json` are not renderable. Previews do not publish.
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

Every PR update and push to `main` runs validation and tests. The selector renders affected registered PDFs, with a safe full-build fallback when impact is uncertain; documentation-only changes produce validation-only runs. Review links, retention, and manual runs follow [WORKFLOW.md](system/WORKFLOW.md#validation-and-previews). [Browse PDF previews runs](https://github.com/Programmer484/little_chewz/actions/workflows/build-resources.yml).

