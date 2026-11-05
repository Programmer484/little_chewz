# Content contract

Owns file organization, source authority, delivery statuses, and source/output boundaries. Writing rules belong in editorial guides; lifecycle steps are [Create](CREATE.md), [Edit](EDIT.md) and [Publish](PUBLISH.md).

## Organization and ownership

Hierarchy: Little Chewz / Chewlandia Academy → school → quest → lesson → resource.

Current school: Confetti Cake Cottage School (`ccc`). Current quest: Quest 01, The Bake-Off Betrayal (`ccc-q01`); mission: Restore the Sparkle.

| Material | Owning source |
| --- | --- |
| Quest facts and ordered lesson list (no publication status) | `content/<school>/<quest>/quest.json` |
| Lesson wording and teaching steps | `lessons/<stage>/lesson.json` within the quest |
| Draft and accepted lesson source | The same `lessons/<stage>/lesson.json` path; drafts do not need a separate filename |
| Companion blocks | `resources/teacher_companion/*.json` within the quest; resource delivery is derived from publication evidence |
| Raw stories and letters | `story/*.md` within the quest |
| Stable IDs, production method, holding/published URLs, builds and publication evidence | `catalog/resources.json` |
| Shared starting structures | `templates/<template>/TEMPLATE.json`: `teacher_guide`, `teacher_companion`, `activity_guide` (option activity guides), `option_overview` (choosing between options) and `welcome` (clean page style and quest navigation) |
| Verified review and official Drive folder configuration | `catalog/drive_folders.json` |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Keep active JSON limited to current content, resource identities, and fields needed to build or publish. Do not store migration logs or source-page crosswalks in lesson or quest data.

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
- `approved_md5` and `revision`: written only after verifying that the official Drive bytes match the accepted GitHub-generated PDF. Keep the local MD5 as a **source baseline** in the handoff until then. A missing checksum is **unknown parity**; never infer equality from the official URL.

Every resource retains its stable catalogue key, `title`, folder-aligned `type`, `published_url` and nullable `holding_url`. Every new **Drive-managed file** starts with a Holding file; the source and `pdf` metadata for a generated PDF may be created at first Edit. External-link-only resources (YouTube and print-pack URLs) have no Drive file to move: they start with null URLs until explicitly authorized publication of the real destination. Holding file MIME types must be compatible with their intended final files. Optional extras are `pdf_url` (original classroom-slide source PDF), `print.cards_per_sheet` (student-material cutouts), `dependencies` (explicit stable resource IDs for non-generated files), and `human_reviewed_url` (the exact approved non-Drive URL). Non-Drive links without approval automatically report NEEDS REVIEW; `review_mode` and URL-keyed `human_review` maps do not exist. The manually invoked audit may check all published Drive files, regardless of owner or category; it is not a release gate.

`catalog/drive_folders.json` keeps verified staging and official folder IDs. Files published externally are managed manually and have no PDF renderer or source checksum. Every new Drive-managed file starts with a real Holding file and catalogue entry; external-link-only resources have a catalogue identity without a fake Holding file. Generated PDFs iterate via GitHub previews, then replace the same Holding Drive file with the final approved candidate. Existing live resources stage separate Holding revisions. Stage a distinct `holding_url` for any existing-resource revision, including generated PDFs, when preparing a candidate; clear it only after successful release. The official URL may remain unchanged when the same file is moved to an approved folder. An existing permanent URL alone is never evidence of public access; verify sharing on publication, independently of the optional audit.

Resource delivery has **three derived states**; never store a separate resource `status` field:

| Derived state | Rule |
| --- | --- |
| `unpublished` | No `published_url` |
| `pending_publish` | An official URL exists **and** a distinct Holding file exists (all resources), or the current GitHub-generated PDF MD5 differs from its approved `pdf.approved_md5` |
| `published` | An official URL exists and no pending change was detected |

Compare holding and published **Drive file IDs**, not incidental sharing URL parameters. For generated PDFs, the current PDF must be built before comparing MD5. Run `python scripts/publication_state.py` (or `--resource-id <id>`) for a read-only, source-built status report. A missing approved/current checksum is **unknown parity**, not proof of a match; the read-only status report labels this verification uncertainty independently of derived publication status. The official resource remains available while an update is pending. Draft builds prefer a staged Holding URL; release builds accept published URLs only.

**Human approval of the exact staged artifact and an explicit human instruction naming resource IDs are required for every publication.** First releases move the same Holding file into Public, preserving its Drive ID and URL; updates replace the existing Public file in place. No merge or catalogue condition auto-publishes. The generated-PDF publisher retains the established official Drive file ID, verifies checksum read-back, then writes `pdf.approved_md5` and `pdf.revision` automatically. At first-time manual publication, move the **existing approved Holding file** to the Public folder without changing its ID/URL; confirm public sharing and record the published URL only after Drive read-back. The manual audit is optional and never gates publication. Record approved PDF checksums only after exact Drive/source byte parity. For legacy generated PDFs without a verified checksum, leave it absent and let inspection report NEEDS REVIEW. External publication records only the official link after verification; do not invent content parity.

**Lesson publication is derived from its Teacher Guide.** `quest.json.learning_sequence[]` owns only lesson order (folder and title)—no status or URLs. For each lesson folder, resolve the existing registered generated-PDF `pdf.output` named `<folder>-teacher-guide.pdf` in `catalog/resources.json` and apply the same `publication_state.py` URL/checksum rules. No Guide or no official Guide URL means `unpublished`; a current Guide checksum differing from the approved MD5 means `pending_publish`. A missing checksum remains a verification uncertainty, not proof of parity. Run `python scripts/publication_state.py --lessons` for the source-built lesson report. Linked worksheets, slides and companions retain their independent derived publication states.

Publishing and initial official-link authorization belong to [PUBLISH.md](PUBLISH.md). Generated guides/companions require every linked resource to have an official URL, even if its next version is pending. When manually invoked, the audit checks the existing published destination independently of whether a newer version is staged. There is no automatic publisher, scheduled inspection or separate audit agent. The existing manual Inspect Action audits published resources only and rejects their unpublished dependencies; external resource dependencies must be explicitly recorded in the catalogue.

## Source authority

1. Explicit human decisions within their stated scope, recorded in the owning source or instructions.
2. Current accepted editable content and its quest/resource-catalog delivery records.
3. Current reviewed lesson slides or media for slide-specific details.
4. Existing approved Teacher Guides and teacher companion resources for editorial and instructional patterns.

A newer timestamp or extraction does not establish publication or content authority. Flag disagreements between records; do not silently choose the more permissive status. Historical reports and backlog proposals do not override current rules or establish implemented capabilities.

## Resources, slides, and assets

- Resolve linked titles and destinations through `catalog/resources.json` (an existing PPTX target may be recorded as `powerpoint_file_id` alongside its lesson PDF resource). The registry object key is the resource ID; omit repeated `resource_id` fields. An optional `dependencies` list records explicit IDs of resources linked from externally authored files; never use it to store URLs or duplicate source-only build refs. Use stable `ref` IDs in lesson flow, not literal Drive URLs. Missing, stale, or unverified destinations block release; never guess a URL or fall back to unlinked text. A recorded URL does not prove external sharing works.
- Maintain one independent slide set per lesson, with local numbering and a stable resource ID; link that lesson's reviewed set in Preparation. `SHOW`/`KEEP` numbers are navigation, not resource IDs; verify them against that set. The reviewed lesson PDF is the slide source; [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md) owns PPTX conversion and Drive replacement. No editable slide renderer exists. Preserve the seven-slide published Activate asset until the human approves a specific revision. Never reuse the retired 44-slide quest-wide numbering, merge decks, or republish them automatically.
- Commit every image consumed by a PDF build to GitHub: covers, full-page images, backgrounds, illustrations, and reusable artwork. Keep editable text separately. Required build assets must be repository-local; a Drive link is insufficient.
- **Build templates from individual assets.** When creating or revising a template or a templated document, save each logo, crest, icon, illustration, or other piece of artwork as its own image file (in the template's or document's `assets/` folder) and let the renderer place it alongside live text, colour, rules, and spacing. Do not generate a whole page or template as one image (AI-generated or rasterized), and do not bake editable text into artwork. The one exception is original cover artwork, kept as a losslessly cut `cover.pdf` ([BINARY_TRANSFER.md](BINARY_TRANSFER.md)).
- A finished image distributed directly from Drive, with no PDF-building step, may remain Drive-link-only; retain its stable registry ID and verified link.
- Do not copy large exported PDFs into the source package. A legacy PDF awaiting conversion may remain a migration input. Follow [BINARY_TRANSFER.md](BINARY_TRANSFER.md) for connector binary transfers.
