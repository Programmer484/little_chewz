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
| Shared starting structures | `templates/<template>/TEMPLATE.json`: `teacher_guide`, `teacher_companion`, `activity_guide` (option activity guides), `option_overview` (choosing between options) and `welcome` (clean page style and quest navigation) |
| Verified review and official Drive folder configuration | `catalog/drive_folders.json` |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Each resource has one content owner. Teacher Guides reference resources by stable ID; they do not copy whole resource text. Keep templates and renderers shared, outside quests.

Use lowercase kebab-case for new content filenames and folders, retaining established paths. Lesson order is `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`. Stable content IDs follow `ccc-q01-<stage>-<slug>`; never use a filename, extension, location, or changing display title as identity. Preserve existing IDs and published Drive file IDs.

## Catalogue resource categories

Catalogue `type` mirrors the **five published Drive folders**. It represents the delivery destination, not genre, format, or audience.

| `type` | Published folder | Included |
| --- | --- | --- |
| `welcome` | `00_WELCOME` | Quest Overview and welcome materials |
| `teacher_guide` | `01_TEACHER_GUIDES` | Lesson Teacher Guides |
| `classroom_slides` | `02_CLASSROOM_SLIDES` | Lesson presentation decks |
| `student_material` | `03_STUDENT_MATERIALS` | Student-facing worksheets and activity cards |
| `teacher_resource` | `04_TEACHER_RESOURCES` | Teacher companions, answer keys, references, letters, media, posters, and print-pack links |

The folder category is the only audience/content classification. No `audience`, free-form `tags`, `story` type or duplicate source flags are stored. Python-generated resources carry a `pdf` object; all other resources omit it. A `story/*.md` directory is an editable content source, not a resource type. Source JSON for companions may still use its own `kind` (`questions`, `extension`, `answer_key`) for its printed masthead.

## Production workflows and delivery states

Generation is inferred from the presence of `pdf` in `catalog/resources.json` (no redundant `production_type`, `pdf_template`, `source`, `build` or `url`). The object contains:
- `renderer`: the Python renderer that builds the PDF: `teacher_guide`, `teacher_companion` or `welcome`. It is not the *template*. Every generated-PDF source declares its template (the content structure it follows) as its first key, `"template": "<name>"`, copied from `templates/<name>/TEMPLATE.json`. One renderer can serve several templates: `teacher_companion` builds both `teacher_companion` and `activity_guide` sources. `scripts/validate.py` (`TEMPLATE_RENDERER`) checks each source's template against its `pdf.renderer`.
- `output`: registered PDF filename for guide/companion; alternatively `source`: explicit editable GitHub JSON path for the standalone Welcome renderer.
- `approved_md5` and `revision`: written only after verified Drive read-back of the exact generated PDF. Missing checksum is **unknown parity**; never infer equality.

Every resource retains its stable catalogue key, `title`, folder-aligned `type`, `published_url` and nullable `holding_url`. Optional extras are `pdf_url` (original classroom-slide source PDF), `print.cards_per_sheet` (student-material cutouts) and `human_reviewed_url` (the exact approved non-Drive URL). Non-Drive links without approval automatically report NEEDS REVIEW; `review_mode` and URL-keyed `human_review` maps do not exist. All published Drive files, regardless of owner or category, undergo Drive existence/permission inspection.

`catalog/drive_folders.json` keeps verified staging and official folder IDs. Files published externally are managed manually and have no PDF renderer or source checksum. Stage a distinct `holding_url` while revising; clear it on release. The official URL may remain unchanged when the same file is moved to an approved folder. An existing permanent URL is never evidence of public access without a real inspection.

Resource delivery has **three derived states**; never store a separate resource `status` field:

| Derived state | Rule |
| --- | --- |
| `unpublished` | No `published_url` |
| `pending_publish` | An official URL exists **and** a distinct holding file exists (external resources), or the current GitHub-generated PDF MD5 differs from the approved `pdf.approved_md5` (generated PDFs) |
| `published` | An official URL exists and no pending change was detected |

Compare holding and published **Drive file IDs**, not incidental sharing URL parameters. For generated PDFs, the current PDF must be built before comparing MD5. Run `python scripts/publication_state.py` (or `--resource-id <id>`) for a read-only, source-built status report. A missing approved/current checksum is **unknown parity**, not proof of a match; inspection and publication approval handle that separately. The official resource remains available while an update is pending.

**Human approval remains mandatory for publication.** Staging or a checksum change never publishes a resource. The generated-PDF publisher retains the established official Drive file ID, verifies checksum read-back, then writes `pdf.approved_md5` and `pdf.revision` automatically. At first-time manual publication, record the approved checksum only after the exact uploaded PDF bytes are verified. For legacy generated PDFs without a verified checksum, leave it absent and let inspection report NEEDS REVIEW. External publication records only the official link after verification; do not invent content parity.

**Lesson publication is derived from its Teacher Guide.** `quest.json.learning_sequence[]` owns only lesson order, title and provenance—no status or URLs. For each lesson folder, resolve the existing registered generated-PDF `pdf.output` named `<folder>-teacher-guide.pdf` in `catalog/resources.json` and apply the same `publication_state.py` URL/checksum rules. No Guide or no official Guide URL means `unpublished`; a current Guide checksum differing from the approved MD5 means `pending_publish`. A missing checksum remains a verification uncertainty, not proof of parity. Run `python scripts/publication_state.py --lessons` for the source-built lesson report. Linked worksheets, slides and companions retain their independent derived publication states.

Publishing and initial official-link authorization belong to [PUBLISH.md](PUBLISH.md). Generated guides/companions require every linked resource to have an official URL, even if its next version is pending. Inspection checks the existing published destination independently of whether a newer version is staged. There is no external auto-publisher or scheduled inspector.

## Source authority

1. Explicit human decisions within their stated scope, recorded in the owning source or instructions.
2. Current accepted editable content and its quest/resource-catalog delivery records.
3. Current reviewed lesson slides or media for slide-specific details.
4. Existing approved Teacher Guides and teacher companion resources for editorial and instructional patterns.

A newer timestamp or extraction does not establish publication or content authority. Flag disagreements between records; do not silently choose the more permissive status. Historical reports and backlog proposals do not override current rules or establish implemented capabilities.

## Resources, slides, and assets

- Resolve linked titles and destinations through `catalog/resources.json` (an existing PPTX target may be recorded as `powerpoint_file_id` alongside its lesson PDF resource). The registry object key is the resource ID; omit repeated `resource_id` fields. Use stable `ref` IDs in lesson flow, not literal Drive URLs. Missing, stale, or unverified destinations block release; never guess a URL or fall back to unlinked text. A recorded URL does not prove external sharing works.
- Maintain one independent slide set per lesson, with local numbering and a stable resource ID; link that lesson's reviewed set in Preparation. `SHOW`/`KEEP` numbers are navigation, not resource IDs; verify them against that set. The reviewed lesson PDF is the slide source; [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md) owns PPTX conversion and Drive replacement. No editable slide renderer exists. Preserve the seven-slide published Activate asset until the human approves a specific revision. Never reuse the retired 44-slide quest-wide numbering, merge decks, or republish them automatically.
- Commit every image consumed by a PDF build to GitHub: covers, full-page images, backgrounds, illustrations, and reusable artwork. Keep editable text separately. Required build assets must be repository-local; a Drive link is insufficient.
- **Build templates from individual assets.** When creating or revising a template or a templated document, save each logo, crest, icon, illustration, or other piece of artwork as its own image file (in the template's or document's `assets/` folder) and let the renderer place it alongside live text, colour, rules, and spacing. Do not generate a whole page or template as one image (AI-generated or rasterized), and do not bake editable text into artwork. The one exception is original cover artwork, kept as a losslessly cut `cover.pdf` ([CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md)).
- A finished image distributed directly from Drive, with no PDF-building step, may remain Drive-link-only; retain its stable registry ID and verified link.
- Do not copy large exported PDFs into the source package. A legacy PDF awaiting conversion may remain a migration input. Follow [CHAT_FILE_CREATION.md](CHAT_FILE_CREATION.md) for source creation and binary transfer.
