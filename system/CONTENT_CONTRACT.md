# Content contract

Owns file organization, source authority, delivery statuses, and source/output boundaries. Writing rules belong in the editorial guides; delivery belongs in [WORKFLOW.md](WORKFLOW.md).

## Organization and ownership

Hierarchy: Little Chewz / Chewlandia Academy → school → quest → lesson → resource.

Current school: Confetti Cake Cottage School (`ccc`). Current quest: Quest 01, The Bake-Off Betrayal (`ccc-q01`); mission: Restore the Sparkle.

| Material | Owning source |
| --- | --- |
| Quest facts and ordered lesson list (no publication status) | `content/<school>/<quest>/quest.json` |
| Lesson wording and teaching steps | `lessons/<stage>/lesson.json` within the quest |
| Unconverted lesson provenance | Optional, short `lessons/<stage>/stage.json`; never owns status, teaching content, or preview switches |
| Draft and accepted lesson source | The same `lessons/<stage>/lesson.json` path; drafts do not need a separate filename |
| Companion blocks | `resources/teacher_companion/*.json` within the quest; resource delivery is derived from publication evidence |
| Raw stories and letters | `story/*.md` within the quest |
| Stable IDs, production method, holding/published URLs, builds and publication evidence | `catalog/resources.json` |
| Shared starting structures | `templates/teacher_guide/`, `templates/teacher_companion/`, `templates/welcome/` (clean page style and quest navigation) |
| Verified review and official Drive folder configuration | `catalog/drive_folders.json` |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Each resource has one content owner. Teacher Guides reference resources by stable ID; they do not copy whole resource text. Keep templates and renderers shared, outside quests.

Use lowercase kebab-case for new content filenames and folders, retaining established paths. Lesson order is `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`. Stable content IDs follow `ccc-q01-<stage>-<slug>`; never use a filename, extension, location, or changing display title as identity. Preserve existing IDs and published Drive file IDs.

## Catalogue resource categories

Catalogue `type` describes the **four teacher-facing delivery categories**, not a story genre or file format. It aligns with the published Drive organization:

| `type` | Delivery folder | Included |
| --- | --- | --- |
| `teacher_guide` | `01_TEACHER_GUIDES` | Published lesson Teacher Guides |
| `teacher_resource` | `04_EXTRA_RESOURCES` (or the established Welcome area) | Teacher companions, reference PDFs, lesson stories and letters, media, posters, print-pack links, and Quest Overview |
| `student_worksheet` | `03_STUDENT_MATERIALS` | Printable student-facing worksheets and activity cards |
| `slides` | `02_CLASSROOM_SLIDES` | Published lesson PPTX files |

`type` is **not** a PDF renderer selector. The source remains `production_type` (`generated_pdf` or `external`), with `build` describing the generated output when applicable.

Keep metadata structured rather than adding arbitrary keyword tags:
- `audience`: `teacher` or `student`, describing the intended reader. Worksheets are `student` even when teachers distribute them.
- `pdf_template`: `teacher_guide`, `teacher_companion`, or `welcome` for Python-rendered PDFs; `null` for externally authored files, links, media and slides.
- No free-form `tags` field. Lesson identity comes from the stable resource ID, references and source path, not an extra genre label.

Companion files retain their own `kind` (`questions`, `extension`, `answer_key`, etc.) inside their editable JSON to control the printed masthead; this is independent of catalogue classification. Similarly, `story/*.md` may remain a source directory for raw prose but is not a catalogue resource type.

## Production workflows and delivery states

Each catalogue resource has an explicit `production_type`, independent of its `type` or filename extension:

- **`generated_pdf`:** Python-rendered Teacher Guides, teacher companions, and other repository PDF outputs. Editable GitHub source and a valid explicit `build.output` or `build.renderer` + `build.source` mapping are required. Use the shared lesson editing branch by default (legacy `edit/<resource-id>` branches remain supported); only generated PDFs can use the authorized release marker and automatic post-merge Drive PDF replacement.
- **`external`:** image-generated worksheets, posters, externally authored PDFs, lesson slide PDFs/PPTX, media and other tool-authored files. These may have no GitHub editable source or rendering pipeline; an agent creates, holds, updates and publishes them manually. Do not infer a Python build because their filename ends in .pdf.

`catalog/drive_folders.json` names verified **holding** folders for generated PDF reviews, worksheets, posters/visuals, other external resources and the pre-existing separate Slide PDFs review folder. `catalog/resources.json` stores:

| Field | Meaning |
| --- | --- |
| Stable object key | Resource identity, independent of filename, Drive ID or title |
| `type` | Four delivery categories: `teacher_guide`, `teacher_resource`, `student_worksheet`, `slides` |
| `audience` | Intended reader: `teacher` or `student` |
| `pdf_template` | PDF generator template (`teacher_guide`, `teacher_companion`, `welcome`) or `null` for non-generated resources |
| `production_type` | Python-generated PDF or external creation |
| `source` | GitHub path, known external original, or explicitly unknown provenance |
| `build` | Required only for generated PDFs, resolved against `scripts/select_builds.py.targets()` |
| `holding_url` | Optional staged replacement/draft URL. For non-generated resources, a distinct holding file means an update is pending. Clear it when the approved replacement goes live. Same Drive file ID is not a distinct draft. |
| `published_url` | Verified official destination; may be the **same URL as the former holding URL** if the same file was moved without changing its Drive ID |
| `url` | Legacy compatibility link; never establishes publication. If `published_url` exists, **both preview and release** link only to it; otherwise a draft preview may use `holding_url` or `url`. |
| `publication` | Explicit evidence/uncertainty: verification, method, confirmed revision/version, file ID, and generated-PDF MD5 only when actually checked |
| `human_review` | Exact-URL map: `{"https://...": "pending"}` or `reviewed`. Required for published non-Drive links; optional for standard Drive or generated links. Approval is invalidated when the URL changes. |\n| `review_mode` | Optional `human` for externally owned Drive links, bypassing automated Drive checks. Human review does not bypass checks for ordinary Drive links. |\n| `print` | Optional, student worksheets only: `{"cards_per_sheet": N}` when each page holds N identical cards, counted from the actual file. Read by the [Print Pack Builder](../apps/AGENTS.md) to print sheets instead of one page per card. |

When an externally published resource is converted to `generated_pdf`, keep its live URL and `external_agent` publication evidence unchanged; the validator accepts that evidence without a digest until the next verified generated release replaces the file in place. For legacy resources whose Drive history is uncertain, preserve existing links, notes and delivery status; record publication verification as `unverified` or `unknown` rather than inventing a digest or pretending a historic upload was confirmed.

Resource delivery has **three derived states**; never store a separate resource `status` field:

| Derived state | Rule |
| --- | --- |
| `unpublished` | No `published_url` |
| `pending_publish` | An official URL exists **and** a distinct holding file exists (external resources), or the current GitHub-generated PDF MD5 differs from the approved `publication.artifact_md5` (generated PDFs) |
| `published` | An official URL exists and no pending change was detected |

Compare holding and published **Drive file IDs**, not incidental sharing URL parameters. For generated PDFs, the current PDF must be built before comparing MD5. Run `python scripts/publication_state.py` (or `--resource-id <id>`) for a read-only, source-built status report. A missing approved/current checksum is **unknown parity**, not proof of a match; inspection and publication approval handle that separately. The official resource remains available while an update is pending.

**Human approval remains mandatory.** Staging or a checksum change never publishes a resource. The publisher retains the established official file ID, checks Drive read-back, then saves the new approved MD5. External publication records an official link only after verification; clear the holding link after release. For legacy uncertain records, retain explicit verification uncertainty, never invent approval.

**Lesson publication is derived from its Teacher Guide.** `quest.json.learning_sequence[]` owns only lesson order, title and provenance—no status or URLs. For each lesson folder, resolve the existing registered generated-PDF `build.output` named `<folder>-teacher-guide.pdf` in `catalog/resources.json` and apply the same `publication_state.py` URL/checksum rules. No Guide or no official Guide URL means `unpublished`; a current Guide checksum differing from the approved MD5 means `pending_publish`. A missing checksum remains a verification uncertainty, not proof of parity. Run `python scripts/publication_state.py --lessons` for the source-built lesson report. Linked worksheets, slides and companions retain their independent derived publication states.

Publishing and initial official-link authorization belong to [PUBLISH.md](PUBLISH.md). Generated guides/companions require every linked resource to have an official URL, even if its next version is pending. Inspection checks the existing published destination independently of whether a newer version is staged. There is no external auto-publisher or scheduled inspector.

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
