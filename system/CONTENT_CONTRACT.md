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
| Stable IDs, production method, holding/published URLs, build records, and linked-resource delivery status | `catalog/resources.json` |
| Shared starting structures | `templates/teacher_guide/`, `templates/teacher_companion/`, `templates/welcome/` (clean page style and quest navigation) |
| Verified review and official Drive folder configuration | `catalog/drive_folders.json` |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Each resource has one content owner. Teacher Guides reference resources by stable ID; they do not copy whole resource text. Keep templates and renderers shared, outside quests.

Use lowercase kebab-case for new content filenames and folders, retaining established paths. Lesson order is `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`. Stable content IDs follow `ccc-q01-<stage>-<slug>`; never use a filename, extension, location, or changing display title as identity. Preserve existing IDs and published Drive file IDs.

## Content types

| Type | Source | Consumer |
| --- | --- | --- |
| `lesson` | JSON | Teacher Guide renderer |
| `teacher_companion` | JSON blocks (question banks, extensions, answer keys) | Companion renderer with the shared resource masthead |
| `student_worksheet` | Linked or externally authored files | No repository worksheet renderer |
| `teacher_reference` | Linked or externally authored files | No repository reference renderer |
| `slide_deck` | Human-reviewed lesson PDF and derived PPTX | `pdf_to_linked_slides.py`; no editable slide JSON renderer |
| `story` | Markdown | Story/audio workflow |
| `media` | Registry and external URL | External provider; no repository renderer |
| `print_pack` | Registry entry linking one lesson in the Print Pack Builder | Teacher Guide Preparation; the app reads guides and the catalogue itself |
| `visual_asset` | PNG/SVG/JPG and source metadata | Renderers or direct distribution |
| `published_export` | Generated PDF/PPTX/etc. | Distribution |

Only maintain templates for resource types with working source-authoring workflows. Linked-only and future types need no placeholder template or renderer. Add checks and a renderer when real sources need them; `scripts/validate.py` owns implemented automatic checks.

## Production workflows and delivery states

Each catalogue resource has an explicit `production_type`, independent of its `type` or filename extension:

- **`generated_pdf`:** Python-rendered Teacher Guides, teacher companions, and other repository PDF outputs. Editable GitHub source and a valid explicit `build.output` or `build.renderer` + `build.source` mapping are required. Use the shared lesson editing branch by default (legacy `edit/<resource-id>` branches remain supported); only generated PDFs can use the authorized release marker and automatic post-merge Drive PDF replacement.
- **`external`:** image-generated worksheets, posters, externally authored PDFs, lesson slide PDFs/PPTX, media and other tool-authored files. These may have no GitHub editable source or rendering pipeline; an agent creates, holds, updates and publishes them manually. Do not infer a Python build because their filename ends in .pdf.

`catalog/drive_folders.json` names verified **holding** folders for generated PDF reviews, worksheets, posters/visuals, other external resources and the pre-existing separate Slide PDFs review folder. `catalog/resources.json` stores:

| Field | Meaning |
| --- | --- |
| Stable object key | Resource identity, independent of filename, Drive ID or title |
| `production_type` | Python-generated PDF or external creation |
| `source` | GitHub path, known external original, or explicitly unknown provenance |
| `build` | Required only for generated PDFs, resolved against `scripts/select_builds.py.targets()` |
| `holding_url` | Optional temporary review file URL for unpublished/draft content. Clear it when a non-slide resource is published; retain only an actual separate slide-review asset when needed. Not proof of publication. |
| `published_url` | Verified official destination; may be the **same URL as the former holding URL** if the same file was moved without changing its Drive ID |
| `url` | Backward-compatible link. **Any resource marked `published` always renders `published_url`**, even in review PDFs; draft previews may use `holding_url` or `url`. Published resources without `published_url` must not silently fall back to other links. |
| `publication` | Explicit evidence/uncertainty: verification, method, confirmed revision/version, file ID, and generated-PDF MD5 only when actually checked |
| `print` | Optional, student worksheets only: `{"cards_per_sheet": N}` when each page holds N identical cards, counted from the actual file. Read by the [Print Pack Builder](../apps/AGENTS.md) to print sheets instead of one page per card. |

When an externally published resource is converted to `generated_pdf`, keep its status, live URL and `external_agent` publication evidence unchanged; the validator accepts that evidence without a digest until the next verified generated release replaces the file in place. For legacy resources whose Drive history is uncertain, preserve existing links, notes and delivery status; record publication verification as `unverified` or `unknown` rather than inventing a digest or pretending a historic upload was confirmed.

Only three delivery states are valid:

| Status | Python-generated PDF | External resource |
| --- | --- | --- |
| `unpublished` | No confirmed official version exists; holding-only copies remain drafts | In holding or not confirmed live |
| `pending_publish` | A previously live PDF exists but accepted source update has not been checksum-verified at Drive | Older live version exists; agent-managed update is awaiting verification |
| `published` | Exact accepted PDF bytes and intended Drive file ID have been verified | Agent has confirmed official destination and recorded publication |

Human approval is a decision, **not another status**. Editing a draft branch never changes a previously published resource. Merging an accepted generated-PDF change is not itself publication; only verified Drive read-back allows the publication record to advance. Subsequent generated-PDF publications persist the exact build MD5 and accepted Git revision. Externally made files have no repository build checksum; manual verification must not assert content parity without evidence.

**One status owner:** lesson-source status lives in `quest.json.learning_sequence[].status`; linked-resource status and publication records live in `catalog/resources.json[<stable-id>]`. A lesson and a separately published Teacher Guide can legitimately have different status. Stable file URLs do not determine status; verified official placement does. No duplicate status in `lesson.json`, `stage.json` or companion JSON. Preserve established file IDs and slideshow pairing.

Publication procedures, release checks, and the timing of status updates belong exclusively to [PUBLISH.md](PUBLISH.md). For generated guides and companions, the publisher automatically blocks release while **any referenced catalogue item** is not `published` with an official URL. This contract defines identity and status, not a release authorization. On-demand inspection is read-only and checks only published resources using the three-category contract in [INSPECTION.md](INSPECTION.md). Externally approved file checksums and official folders must be recorded manually at release; there is no external auto-publisher, scripted `/create` engine, scheduled inspector or configured publishing slash command.

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
