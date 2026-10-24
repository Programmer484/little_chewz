# Content contract

Owns file organization, source authority, review statuses, and source/output boundaries. Writing rules belong in the editorial guides; delivery belongs in [WORKFLOW.md](WORKFLOW.md).

## Organization and ownership

Hierarchy: Little Chewz / Chewlandia Academy → school → quest → lesson → resource.

Current school: Confetti Cake Cottage School (`ccc`). Current quest: Quest 01, The Bake-Off Betrayal (`ccc-q01`); mission: Restore the Sparkle.

| Material | Owning source |
| --- | --- |
| Quest facts, lesson sequence, and each lesson's **only lifecycle status** | `content/<school>/<quest>/quest.json` |
| Lesson wording and teaching steps | `lessons/<stage>/lesson.json` within the quest |
| Unconverted lesson provenance | Optional, short `lessons/<stage>/stage.json`; never owns status, teaching content, or preview switches |
| Unapproved and approved lesson source | The same `lessons/<stage>/lesson.json` path; drafts do not need a separate filename |
| Companion blocks | `resources/teacher_companion/*.json` within the quest; status is in the resource registry |
| Raw stories and letters | `story/*.md` within the quest |
| Linked names, destinations, stable ID object keys, and **only linked-resource lifecycle status** | `catalog/resources.json` |
| Shared starting structures | `templates/teacher_guide/`, `templates/teacher_companion/`, `templates/story/`, and `templates/claude/` (clean page style and quest navigation) |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Each resource has one content owner. Teacher Guides reference resources by stable ID; they do not copy whole resource text. Keep templates and renderers shared, outside quests.

Use lowercase kebab-case for new content filenames and folders, retaining established paths. Lesson order is `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`. Stable content IDs follow `ccc-q01-<stage>-<slug>`; never use a filename, extension, location, or changing display title as identity. Preserve existing IDs and published Drive file IDs.

## Content types

| Type | Source | Consumer |
| --- | --- | --- |
| `lesson` | JSON | Teacher Guide renderer |
| `teacher_companion` | JSON blocks | Companion renderer |
| `student_worksheet` | Linked or externally authored files | No repository worksheet renderer |
| `teacher_reference` | Linked or externally authored files | No repository reference renderer |
| `slide_deck` | Human-reviewed lesson PDF and derived PPTX | `pdf_to_linked_slides.py`; no editable slide JSON renderer |
| `story` | Markdown | Story/audio workflow |
| `media` | Registry and external URL | External provider; no repository renderer |
| `visual_asset` | PNG/SVG/JPG and source metadata | Renderers or direct distribution |
| `published_export` | Generated PDF/PPTX/etc. | Distribution |

Only maintain templates for resource types with working source-authoring workflows. Linked-only and future types need no placeholder template or renderer. Add checks and a renderer when real sources need them; `scripts/validate.py` owns implemented automatic checks.

## Lifecycle status

Only three values are valid: `unapproved` → `approved` → `published`.

| Status | Meaning |
| --- | --- |
| `unapproved` | New, edited, or unreviewed work. **Default if a status is absent.** Previewable once a valid source exists. |
| `approved` | Human approved this exact source revision; it has not yet been confirmed live. |
| `published` | Human-approved current revision has been published to its intended Drive destination. |

**One owner per item:** `quest.json.learning_sequence[].status` for lesson source; `catalog/resources.json[<stable-id>].status` for linked resources/companions. A standalone raw story's frontmatter describes the local transcription, not its separate Drive distribution. Do not copy a lifecycle status into `lesson.json`, `stage.json`, or companion content.

A link recorded in Drive is not necessarily a cleared resource. For legacy registry entries, a previously unverified `approved_link: false` maps conservatively to `unapproved`, even if there is already a Drive URL; the `link_note` preserves the reason. Previously verified live entries map to `published`. Never infer external permissions solely from a status or URL.

New editing starts in `unapproved`; editing a published source starts a new unapproved revision while the previous file stays live. **Review status is not publication authorization.** Transition to `approved` only after explicit human approval; to `published` only after the exact approved version is updated in Drive and verified. GitHub commits, generated previews, or a passing check never change statuses by themselves. A lesson whose source has not been transcribed stays `unapproved` with no `lesson.json` and is not built.

## Source authority

1. Explicit human decisions within their stated scope, recorded in the owning source or instructions.
2. Current approved editable content and its quest/resource-catalog status records.
3. Current approved lesson slides or media for slide-specific details.
4. `Full Guide Revised.pdf` as editorial and visual benchmark, not automatic authority for current slide numbers.
5. Older PDFs as recovery inputs only where editable sources are missing.

A newer timestamp or extraction does not confer approval. Flag disagreements between records; do not silently choose the more permissive status. Historical reports and backlog proposals do not override current rules or establish implemented capabilities.

## Resources, slides, and assets

- Resolve linked titles and destinations through `catalog/resources.json` (an existing PPTX target may be recorded as `powerpoint_file_id` alongside its lesson PDF resource). The registry object key is the resource ID; omit repeated `resource_id` fields. Retired aliases are archived in [`archive/2026-10/resource-aliases.json`](../archive/2026-10/resource-aliases.json). Use stable `ref` IDs in lesson flow, not literal Drive URLs. Missing, stale, or unapproved destinations block release; never guess a URL or fall back to unlinked text. An approved URL record does not prove external sharing works.
- Maintain one independent slide set per lesson, with local numbering and a stable resource ID. Link that lesson's approved set in Preparation. `SHOW`/`KEEP` numbers are navigation, not resource IDs; verify them against that set.
- Maintain independent lesson-scoped slides. Editable slide-JSON generation remains future policy: no slide renderer/build target exists. Separately, the reviewed **lesson PDF** is the human/AI iteration artifact; after explicit approval only, `scripts/pdf_to_linked_slides.py` produces an image-based PPTX with the PDF's links restored. See [WORKFLOW.md](WORKFLOW.md#classroom-slide-pdf-to-powerpoint) and [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). Preserve the seven-slide published Activate asset until the human approves a specific revision. The old 44-slide crosswalk is archived in [`archive/2026-10/quest-slideshow.json`](../archive/2026-10/quest-slideshow.json); never reuse global numbering, merge decks, or republish them automatically.
- Commit every image consumed by a PDF build to GitHub: covers, full-page images, backgrounds, illustrations, and reusable artwork. Keep editable text separately. Required build assets must be repository-local; a Drive link is insufficient.
- A finished image distributed directly from Drive, with no PDF-building step, may remain Drive-link-only; retain its stable registry ID and approved link.
- Do not copy large exported PDFs into the source package. A legacy PDF awaiting conversion may remain a migration input. Follow [CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md) for source creation and binary transfer.
