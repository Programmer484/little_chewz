# Content contract — Little Chewz

## Hierarchy: product -> school -> quest -> stage -> resource

**Product:** Little Chewz / Chewlandia Academy
**School:** Confetti Cake Cottage School (`ccc`)
**Quest:** Quest 01: The Bake-Off Betrayal (`ccc-q01`), Mission: Restore the Sparkle
**Stages:** `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`.

The source directory matches the learning sequence. A shared template never lives in a quest folder. A raw letter is a story asset, not a teacher guide. An optional teacher question bank is a teacher companion, not a lesson.

## Stable naming

- Folder and filename: lowercase `kebab-case`; for lessons include order prefix `00-` through `06-`.
- Stable content ID: `ccc-q01-<stage>-<slug>`; e.g. `ccc-q01-activate-video-questions`.
- Never use file extension, current PDF title, or location as the stable ID.
- Never rename a published Drive file merely to adjust a source filename; Google file IDs are stable references.

## Type taxonomy

| Type | Source | Generator/consumer | Example |
|---|---|---|---|
| `lesson` | JSON | teacher_guide renderer | Activate teaching flow |
| `teacher_companion` | JSON blocks | teacher_companion renderer | Mission Video Questions |
| `student_worksheet` | JSON | future worksheet renderer | KWLS Starter |
| `teacher_reference` | JSON or Markdown | future reference renderer | Teacher Answer Key |
| `slide_deck` | JSON manifest + assets per lesson | future lesson-slide renderer | Set the Table slides |
| `story` | Markdown | story/audio workflow | Bakery Log (1958) |
| `media` | JSON metadata + external URL | external media tools | Song/audio/video |
| `visual_asset` | PNG/SVG/JPG with source metadata | renderers | Cover artwork |
| `published_export` | PDF/PPTX/etc | generated-only | Teacher Guide PDF |

New types are added by supplying (a) a new `templates/<type>/` blueprint and schema, (b) the type in the taxonomy, (c) an index entry, and (d) a renderer only if output is required. Do not modify existing content to fit an unrelated template.

## Review-status vocabulary

- `approved_source`: existing approved editable source; not a claim of current public release.
- `draft_transcription`: converted from a PDF, pending human check.
- `migration_needed`: source still exists as legacy PDF/slides, not yet converted.
- `draft_unpublished`: editable draft but no approved live link yet.
- `published_legacy`: original Drive PDF still public; editable source is absent or pending republish.
- `archived`: historical only. Never silently treat archived material as latest.

## Rules for source / output separation

- All approved destinations live in `catalog/resources.json`, indexed by stable IDs (`resource_id`), one record each. No literal Google Drive URL inside lesson flow.
- Teaching Flow stores `ref` IDs for external resources; `SHOW slide(s)` is navigation within the specific lesson's slide set, not a resource record.
- **Future slide generation contract:** Generate one independent slide set/deck for each stage, with lesson-local slide numbering, editable lesson-specific sources/assets, and a stable resource ID per lesson set. Regenerate only the changed slide(s) or affected lesson's slides, never an entire quest by default. Historical global slide positions are migration references, not approved current numbers. Do not invent slides or assume a renderer/build target already exists.
- Renderer code lives under `scripts/renderers/`; templates define reusable content structure. Never copy generator code into a quest.
- **PDF build dependency rule:** Commit every image used to generate a PDF to GitHub as a versioned source asset, whether it is a cover, full-page image, background, illustration, character art, or reusable layout artwork. Store generated text separately when it must remain editable. All PDF generation must work with repository-local assets; a Drive link alone is not sufficient for a required PDF input.
- **Standalone image exception:** AI-generated images distributed directly as finished images, without being consumed by a PDF build, may stay in Google Drive. Keep their approved link and stable resource ID in `catalog/resources.json`; do not copy them into GitHub solely for distribution.
- **Existing cover:** PNG/SVG/JPG is a visual source; a PDF cover in the old package can be converted once and kept as a versioned source image in GitHub.
- **Chat file transfers:** When a connector cannot upload local binary files directly, use the verified GitHub Base64 blob + tree/commit/ref procedure in [`CHAT_FILE_CREATION.md`](CHAT_FILE_CREATION.md), including SHA verification and removal of any temporary transfer copy. Uploading the asset does not change its approval status.
- Generated PDFs live in `exports/` only. They are not canonical text sources.
- For files that have no editable source yet, a **legacy PDF may remain the migration input**. Conversion is a one-time audited step, not the future workflow.

## Publishing invariants

- Resource URL must be an approved HTTP(S) link; `approved` does not assert its external sharing setting was tested.
- Publishing updates an existing Drive file in place when maintaining old links. Don't duplicate a live file and leave two apparent current versions.
- Lesson `slides` and stage references must match the **current approved slides for that lesson**, not the older continuous quest deck.
- PDF typography/artwork changes belong in renderer/assets, not the educational content JSON.
- Human validation is required before promoting `draft_transcription` to `approved_source`.
