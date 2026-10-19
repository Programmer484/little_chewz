# Little Chewz — start here

Edit the source, review the generated document, then publish only when authorized. [AGENTS.md](AGENTS.md) is the AI entry point; [WORKFLOW.md](system/WORKFLOW.md) owns the editing and delivery routine.

## Where things belong

| Location | Owns |
| --- | --- |
| `content/` | Lesson wording, companions, stories, artwork, and local review status |
| `catalog/quests.json` | Navigation to quest manifests |
| `catalog/resources.json` | Authoritative linked names, stable resource IDs, and approved destinations |
| `catalog/migration_inventory.json` | Inventory of materials awaiting conversion |
| [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) | Types, paths, version authority, statuses, and source/output boundaries |
| [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) | Teacher Guide writing and presentation requirements |
| [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) | Companion writing and presentation requirements |
| [action_labels.json](system/action_labels.json) | Allowed action labels and internal row types |
| [WORKFLOW.md](system/WORKFLOW.md) | Edit, validate, review, save, merge, publish, and report |
| [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) | Creating source files and transferring binary assets |
| `templates/` | Starting structures for new content; not approved activities |
| `scripts/validate.py` | Implemented automatic content checks |
| `scripts/renderers/` | Shared PDF layout and generation code |
| `scripts/select_builds.py`, `scripts/build_selected.py` | Select and build affected approved PDFs |
| `tests/` | Checks for the tools |
| `.github/workflows/` | Automated validation, PDF previews, and preview cleanup |
| `exports/` | Generated PDFs; never the editable source |
| [SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md) | Tooling backlog; each entry records its implementation status |

## Find a lesson

Follow `catalog/quests.json` → the quest's `quest.json` → its lesson folder and any `stage.json` → the named source. The current quest lives at `content/confetti-cake-cottage/quest-01-bake-off-betrayal/`.

Lesson folders run from `00-activate` through `06-celebrate`. Companions live under `resources/teacher_companion/`; raw stories and letters live under `story/`. Read review status before editing or building: a folder's existence does not mean its material is approved.

## Current capabilities

- Automated builds support three approved PDFs: Activate Teacher Guide, Mission Video Questions, and Confetti File Questions.
- Set the Table has a draft transcription; later lessons still need conversion. Songwriting Extension is a draft excluded from approved builds.
- Slides are maintained per lesson under the content contract. Slide and worksheet generation are not implemented.
- The validator checks selected required fields, resource references, registry IDs/HTTPS destinations, covers, action labels, and step order. It does not fully validate every content structure, inspect draft lessons, test Drive access, or grant editorial approval.

## Local checks and approved previews

From the repository root, with Python 3.10+:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python -m pip install -r requirements.txt
python scripts/select_builds.py --all --output /tmp/little-chewz-build-selection.json
python scripts/build_selected.py --manifest /tmp/little-chewz-build-selection.json
```

Teacher Guide rendering requires installed Lato fonts. The selected builder replaces PDFs in `exports/`; keep review copies elsewhere if needed. `scripts/build.py` also supports direct builds, but its `companions` command includes drafts: use the selected builder for approved-output previews.

## GitHub previews

Relevant PR changes trigger **PDF previews**: validation and tool tests run, then only affected registered PDFs are rebuilt. A shared dependency can select all three; documentation-only changes may produce no PDFs. Manual **Actions → PDF previews → Run workflow** builds all three.

Download the artifact from the PR's Checks run within seven days, or open the PDF links in the run summary. Browser previews live on disposable `pdf-preview-pr-N` branches, deleted when the PR closes; manual previews reuse `pdf-preview-manual`. These outputs never enter `main` or update Drive. New, unregistered resources are not covered by a passing preview run.

[MIGRATION_REPORT.md](MIGRATION_REPORT.md) records the original migration findings; it is historical context, not current operating instructions.
