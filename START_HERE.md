# Little Chewz — AI Source System (starter v1)

**START HERE for humans and AI.** This is a proposed source-first migration package based on the current Google Drive inventory on 2026-10-15. It does not alter or republish the live Drive materials.

## 90-second orientation

1. Read `AGENTS.md` (mandatory AI start) and `system/EDITORIAL_GUIDE.md`.
2. Read `catalog/quests.json` and the relevant `content/**/quest.json` to locate the quest/stage and its revision status.
3. Read `catalog/resources.json` to look up a resource's stable ID, approved destination, format and audience. Never invent a URL.
4. Read the selected lesson `lesson.json` or resource `*.json` and its schema. **Edit these sources**, not PDFs.
5. Use the shared generator under `scripts/renderers/` and review the generated result before publishing.

## Directory map

```text
AGENTS.md                         Master rules for future AI
START_HERE.md                     Orientation
system/
  EDITORIAL_GUIDE.md              Existing approved teacher-guide writing rules
  RESOURCE_GUIDELINES.md          Existing companion resource guidelines
  CONTENT_CONTRACT.md             File types, statuses, naming and precedence
  action_labels.json              One editable allowed-label registry
catalog/
  quests.json                     Navigation index (no duplicated lesson bodies)
  resources.json                  SINGLE canonical registry of approved resource URLs
  migration_inventory.json        What exists and what is not yet migrated
schemas/                         JSON validation contracts
templates/                       JSON/Markdown content blueprints (no renderer code)
  teacher_guide/TEMPLATE.json
  teacher_companion/TEMPLATE.json
  student_worksheet/TEMPLATE.json
  teacher_reference/TEMPLATE.json
  slide_deck/TEMPLATE.json      Future lesson-specific slide blueprint
  story/TEMPLATE.md
  media/TEMPLATE.json
scripts/renderers/
  teacher_guide.py                Existing approved PyMuPDF renderer (adapted paths)
  teacher_companion.py            Existing ReportLab renderer
content/
  confetti-cake-cottage/
    quest-01-bake-off-betrayal/
      quest.json                  Quest-level facts and status
      lessons/00-activate/        One working current lesson JSON + image cover
      lessons/01-... etc         Placeholders/statuses, NOT invented sources
      resources/teacher_companion/ Three editable source JSON files
      story/                     Draft transcriptions for human verification
scripts/renderers/               PDF generation code shared by all quests
scripts/validate.py              Local checks for ID/URL/label/step consistency
scripts/build.py                 Generate available PDFs into exports/ only
exports/                         Generated outputs; ignore as editorial source
```

## Commands (local, Python 3.10+)

```bash
python scripts/validate.py
pip install pymupdf reportlab
python scripts/build.py teacher --lesson content/confetti-cake-cottage/quest-01-bake-off-betrayal/lessons/00-activate/lesson.json
python scripts/build.py companions
```

The teacher-guide generator requires locally installed Lato fonts, which are not bundled.

## Editorial authority and version priority

1. Explicit newly approved human decisions and recorded status in `quest.json`.
2. The approved current editable JSON/Markdown in `content/`.
3. Latest matching slideshow/source media for slide-specific references.
4. `Full Guide Revised.pdf` for the *editorial and visual benchmark*; it is not the newest authority for every slide number.
5. `Full Guide.pdf` and older PDF exports only for recovering materials that have no editable source yet.

**Do not treat a PDF extraction as an automatically approved canonical source.** Flag migration status and verify every source/slide/version discrepancy.

## Slideshow policy (decision made 2026-10-19)

Generate and maintain **a separate set of classroom slides per lesson**, with numbering local to that lesson. Make individual-slide edits where practical and regenerate only the affected lesson's slides; **do not assemble or regenerate the entire quest deck by default**. In each Teacher Guide, link the relevant lesson's approved slide resource in Preparation and verify `SHOW`/`KEEP` references against it. Never infer current numbers from historical quest-wide ranges.

The existing seven-slide Activate PDF remains unchanged; the former 44-slide quest deck and `slides/quest-slideshow.json` are historical references, not generation targets. A slide renderer, build targets, resource links for later lessons, preview QA, and publication will be implemented only when real approved slides are ready. Current GitHub Actions builds **PDF resources only**, not slides. Do not alter published Google Drive materials as part of this decision.

## New resource workflow

1. Assign a permanent `resource_id` (e.g. `ccc-q01-activate-video-questions`).
2. Choose resource type and audience from `system/CONTENT_CONTRACT.md`.
3. Copy a matching template, and edit its raw JSON/Markdown.
4. Add its source location and review status to the stage/quest manifest; add an approved URL to `catalog/resources.json` **only after it is published**.
5. Run validation, generate output, visually QA it, check links, and publish by replacing the existing Drive file *in place* where applicable (preserves file IDs).

## Migration warning

Do not move/delete/rename the current public Drive files yet. The current teacher guides link directly to Drive file IDs; migration should preserve those IDs. This package is a reviewable source-system draft, not an approved content rewrite.

## Automated PDF previews in GitHub

When a pull request modifies current lesson/resource sources, rendering code, templates, schemas, the resource registry, or the build workflow, **PDF previews** runs automatically. Open the pull request's **Checks** tab, select the run, and download the `little-chewz-approved-pdf-previews` artifact. It is kept for **7 days**.

The workflow currently validates source and regenerates only the *existing approved outputs*: the Activate Teacher Guide, Mission Video Questions and Confetti File Questions. The Songwriting Extension is a draft and is intentionally excluded. The six later lesson skeletons, worksheets and slides do not have build targets.

For an optional manual build, use **Actions → PDF previews → Run workflow**. In addition to the ZIP artifact, generated PDFs are committed to isolated `pdf-preview-pr-N` branches (or the reusable `pdf-preview-manual` branch) and linked in the workflow run summary for in-browser review. PR preview branches are deleted automatically when their PR closes; manual previews are overwritten on the next manual run. These generated previews never enter `main` and the workflow never writes to Google Drive. To avoid redundant usage it deliberately does **not** run again on every push to `main` after a pull request has passed.

See `SYSTEM_IMPROVEMENTS.md` for the next phase (dependency-aware targeted builds). Each Actions run on the private repository consumes GitHub-hosted runner minutes; artifact retention is kept short to limit storage usage.

**Initial measured run (2026-10-18):** 10.9 seconds of runner log time, which uses approximately **one billable Linux minute** after per-job rounding; three PDF files produced a **740 KB** compressed artifact. Actual runtime may rise as resources are added. GitHub Free currently includes 2,000 Actions minutes monthly across the account; overage for standard 2-core Linux is $0.006/minute. Check GitHub Billing for your plan and remaining allowance.
