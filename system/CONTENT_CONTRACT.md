# Content contract

Owns file organization, source authority, delivery statuses, and source/output boundaries. Writing rules belong in the editorial guides; delivery belongs in [WORKFLOW.md](WORKFLOW.md).

## Organization and ownership

Hierarchy: Little Chewz / Chewlandia Academy → school → quest → lesson → resource.

Current school: Confetti Cake Cottage School (`ccc`). Current quest: Quest 01, The Bake-Off Betrayal (`ccc-q01`); mission: Restore the Sparkle.

| Material | Owning source |
| --- | --- |
| Quest facts, lesson sequence, and each lesson's **only lifecycle status** | `content/<school>/<quest>/quest.json` |
| Lesson wording and teaching steps | `lessons/<stage>/lesson.json` within the quest |
| Unconverted lesson provenance | Optional, short `lessons/<stage>/stage.json`; never owns status, teaching content, or preview switches |
| Draft and accepted lesson source | The same `lessons/<stage>/lesson.json` path; drafts do not need a separate filename |
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

The only delivery states are `unpublished`, `pending_publish`, and `published`. **Editorial approval is not a stored status.** The owner's authorization to merge provides the review gate.

| Status | Meaning |
| --- | --- |
| `unpublished` | No confirmed teacher-facing Drive publication exists. Draft sources and unverified Drive URLs do not count. Default if absent. |
| `pending_publish` | An older Drive publication exists, but the accepted `main` deliverable has changed or replacement has not been verified. The previous Drive version stays live. |
| `published` | The current accepted `main` output matches the verified Drive deliverable. Linked-only resources require a verified live destination. |

**Work in progress is a branch, not a status.** A published resource stays published while agents edit on `edit/<stable-resource-id>`. Merging an output change makes it `pending_publish` if Drive already has a published version; first-time material remains `unpublished` until delivery. Only successful, exact Drive verification establishes `published`. Unrelated `main` commits and metadata-only changes must not affect status.

**Single owners:** `quest.json.learning_sequence[].status` for lesson source; `catalog/resources.json[<stable-id>].status` for linked resources and companions. A lesson and its separately published Teacher Guide may legitimately have different statuses. Do not copy status to `lesson.json`, `stage.json`, or companion content. Keep resource identities and Drive IDs stable.

**Target automatic detection:** persist the digest of the exact build last verified in Drive, compare it with the current accepted `main` build, and verify all deliverables for paired PDF/PPTX releases. A URL, push, merge, or successful renderer is not proof of publication. Do not label a source `published` without confirmation.

**Implementation limitation:** automatic build/Drive hash reconciliation, merge-triggered publishing, and first-time Drive creation are not yet implemented. Existing statuses are being migrated conservatively; keep the documented stale-Drive notices and report uncertainty. No separate user-facing `/publish` command exists.

## Source authority

1. Explicit human decisions within their stated scope, recorded in the owning source or instructions.
2. Current accepted editable content and its quest/resource-catalog delivery records.
3. Current reviewed lesson slides or media for slide-specific details.
4. `Full Guide Revised.pdf` as editorial and visual benchmark, not automatic authority for current slide numbers.
5. Older PDFs as recovery inputs only where editable sources are missing.

A newer timestamp or extraction does not establish publication or content authority. Flag disagreements between records; do not silently choose the more permissive status. Historical reports and backlog proposals do not override current rules or establish implemented capabilities.

## Resources, slides, and assets

- Resolve linked titles and destinations through `catalog/resources.json` (an existing PPTX target may be recorded as `powerpoint_file_id` alongside its lesson PDF resource). The registry object key is the resource ID; omit repeated `resource_id` fields. Retired aliases are archived in [`archive/2026-10/resource-aliases.json`](../archive/2026-10/resource-aliases.json). Use stable `ref` IDs in lesson flow, not literal Drive URLs. Missing, stale, or unverified destinations block release; never guess a URL or fall back to unlinked text. A recorded URL does not prove external sharing works.
- Maintain one independent slide set per lesson, with local numbering and a stable resource ID; link that lesson's reviewed set in Preparation. `SHOW`/`KEEP` numbers are navigation, not resource IDs; verify them against that set. The reviewed lesson PDF is the slide source; [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md) owns PPTX conversion and Drive replacement. No editable slide renderer exists. Preserve the seven-slide published Activate asset until the human approves a specific revision. Never reuse the archived 44-slide quest-wide numbering ([`quest-slideshow.json`](../archive/2026-10/quest-slideshow.json)), merge decks, or republish them automatically.
- Commit every image consumed by a PDF build to GitHub: covers, full-page images, backgrounds, illustrations, and reusable artwork. Keep editable text separately. Required build assets must be repository-local; a Drive link is insufficient.
- **Build templates from individual assets.** When creating or revising a template or a templated document, save each logo, crest, icon, illustration, or other piece of artwork as its own image file (in the template's or document's `assets/` folder) and let the renderer place it alongside live text, colour, rules, and spacing. Do not generate a whole page or template as one image (AI-generated or rasterized), and do not bake editable text into artwork. The one exception is original cover artwork, kept as a losslessly cut `cover.pdf` ([CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md)).
- A finished image distributed directly from Drive, with no PDF-building step, may remain Drive-link-only; retain its stable registry ID and verified link.
- Do not copy large exported PDFs into the source package. A legacy PDF awaiting conversion may remain a migration input. Follow [CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md) for source creation and binary transfer.
