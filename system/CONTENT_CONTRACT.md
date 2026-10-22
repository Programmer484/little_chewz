# Content contract

Owns file organization, source authority, review statuses, and source/output boundaries. Writing rules belong in the editorial guides; delivery belongs in [WORKFLOW.md](WORKFLOW.md).

## Organization and ownership

Hierarchy: Little Chewz / Chewlandia Academy → school → quest → lesson → resource.

Current school: Confetti Cake Cottage School (`ccc`). Current quest: Quest 01, The Bake-Off Betrayal (`ccc-q01`); mission: Restore the Sparkle.

| Material | Owning source |
| --- | --- |
| Quest facts and lesson sequence | `content/<school>/<quest>/quest.json` |
| Lesson wording and teaching steps | `lessons/<stage>/lesson.json` within the quest |
| Lesson preview/review routing | `lessons/<stage>/stage.json`: identity, review status, source filename, preview flag, and active blockers only; do not duplicate lesson content or slide structure |
| Unapproved lesson transcription | Existing draft file named by `stage.json`, such as `lesson.draft.json` |
| Companion blocks | `resources/teacher_companion/*.json` within the quest |
| Raw stories and letters | `story/*.md` within the quest |
| Linked names, destinations, and stable IDs | `catalog/resources.json` |
| Shared starting structures | `templates/<type>/` |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Each resource has one content owner. Teacher Guides reference resources by stable ID; they do not copy whole resource text. Keep templates and renderers shared, outside quests.

Use lowercase kebab-case for new content filenames and folders, retaining established paths. Lesson order is `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`. Stable content IDs follow `ccc-q01-<stage>-<slug>`; never use a filename, extension, location, or changing display title as identity. Preserve existing IDs and published Drive file IDs.

## Content types

| Type | Source | Consumer |
| --- | --- | --- |
| `lesson` | JSON | Teacher Guide renderer |
| `teacher_companion` | JSON blocks | Companion renderer |
| `student_worksheet` | JSON | Future worksheet renderer |
| `teacher_reference` | JSON or Markdown | Future reference renderer |
| `slide_deck` | Lesson-specific JSON manifest and assets | Future slide renderer |
| `story` | Markdown | Story/audio workflow |
| `media` | Metadata and external URL | External media tools |
| `visual_asset` | PNG/SVG/JPG and source metadata | Renderers or direct distribution |
| `published_export` | Generated PDF/PPTX/etc. | Distribution |

Add a type only for a real resource: provide its template, document it here, and index it. Add checks and a renderer when actually needed. Templates describe starting structure; `scripts/validate.py` owns implemented automatic checks. No unused schema layer is required.

## Review status

| Status | Meaning |
| --- | --- |
| `approved_source` | Approved editable source; not proof of public release |
| `draft_transcription` | Converted from legacy material; awaiting human verification |
| `migration_needed` | Editable source still needs conversion |
| `draft_unpublished` | Editable draft without an approved live link |
| `published_legacy` | Original Drive material remains public; editable source absent or pending republish |
| `archived` | Historical reference only |

Preserve these distinctions. Human review is required to promote a transcription. Record unresolved work in existing stage/source metadata; never infer approval from storage, build success, or publication of an older version.

## Source authority

1. Explicit human decisions within their stated scope, recorded in the owning source or instructions.
2. Current approved editable content and its quest/stage/source status records.
3. Current approved lesson slides or media for slide-specific details.
4. `Full Guide Revised.pdf` as editorial and visual benchmark, not automatic authority for current slide numbers.
5. Older PDFs as recovery inputs only where editable sources are missing.

A newer timestamp or extraction does not confer approval. Flag disagreements between records; do not silently choose the more permissive status. Historical reports and backlog proposals do not override current rules or establish implemented capabilities.

## Resources, slides, and assets

- Resolve linked titles and destinations through `catalog/resources.json` (an existing PPTX target may be recorded as `powerpoint_file_id` alongside its lesson PDF resource). Use `ref` IDs in lesson flow, not literal Drive URLs. Missing, stale, or unapproved destinations block release; never guess a URL or fall back to unlinked text. An approved URL record does not prove external sharing works.
- Maintain one independent slide set per lesson, with local numbering and a stable resource ID. Link that lesson's approved set in Preparation. `SHOW`/`KEEP` numbers are navigation, not resource IDs; verify them against that set.
- Maintain independent lesson-scoped slides. Editable slide-JSON generation remains future policy: no slide renderer/build target exists. Separately, the reviewed **lesson PDF** is the human/AI iteration artifact; after explicit approval only, `scripts/pdf_to_linked_slides.py` produces an image-based PPTX with the PDF's links restored. See [WORKFLOW.md](WORKFLOW.md#classroom-slide-pdf-to-powerpoint) and [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). Preserve the seven-slide published Activate asset until the human approves a specific revision. The old 44-slide deck and `slides/quest-slideshow.json` are historical; never reuse global numbering, merge decks, or republish them automatically.
- Commit every image consumed by a PDF build to GitHub: covers, full-page images, backgrounds, illustrations, and reusable artwork. Keep editable text separately. Required build assets must be repository-local; a Drive link is insufficient.
- A finished image distributed directly from Drive, with no PDF-building step, may remain Drive-link-only; retain its stable registry ID and approved link.
- Do not copy large exported PDFs into the source package. A legacy PDF awaiting conversion may remain a migration input. Follow [CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md) for source creation and binary transfer.
