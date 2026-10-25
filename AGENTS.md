# Little Chewz: agent instructions

> **Generated file. Do not edit.** Built by `python scripts/build_agents_md.py` from the instruction files below; change a rule in its owning file, then regenerate.
> Repository: https://github.com/Programmer484/little_chewz

You are helping edit the Little Chewz teaching-material repository. This file is the complete, current set of rules, in the order to read them, and can be pasted into any AI chat. Each part is headed by the file that owns it. Paths are relative to the repository root.

If you cannot read the repository directly, ask the user to paste the exact current file before proposing changes to it, and return complete replacement text for each changed file with its path. Never reconstruct file contents, URLs, statuses, or Drive IDs from memory.

## Contents

- `system/AI_RULES.md`
- `START_HERE.md`
- `system/CONTENT_CONTRACT.md`
- `system/WORKFLOW.md`
- `system/EDITORIAL_GUIDE.md`
- `system/action_labels.json`
- `system/RESOURCE_GUIDELINES.md`
- `templates/claude/README.md`
- `system/SLIDE_CONVERSION.md`
- `system/DRIVE_PUBLISHING.md`
- `system/CHAT_FILE_CREATION.md`
- `system/COMMANDS.md`
- `system/CREATE.md`
- `SYSTEM_IMPROVEMENTS.md`
- `content/AGENTS.md`
- `catalog/AGENTS.md`
- `templates/AGENTS.md`
- `scripts/AGENTS.md`
- `system/AGENTS.md`

---

# File: `system/AI_RULES.md`

## AI rules: routing, boundaries, maintaining instructions

Owns how agents find instructions, the non-negotiable boundaries, and how instructions are maintained. The root `AGENTS.md` is generated from this file and the other instruction files.

This is an editable educational source repository. PDFs are outputs; legacy PDFs are inputs only while awaiting conversion.

### Read for the task

1. Read [START_HERE.md](START_HERE.md) for navigation and current capabilities, and [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) for ownership, status, assets, and version authority.
2. Open the file you will change. Its `$instructions` key (stories: `instructions:` frontmatter) names the guides to read first. Each folder's `AGENTS.md` routes everything in it:

   | Changing | Folder guide | Main rules |
   | --- | --- | --- |
   | Lessons, companions, stories, quest status, Welcome | [content/AGENTS.md](content/AGENTS.md) | [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md), [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) |
   | Resource names, links, status, publishing | [catalog/AGENTS.md](catalog/AGENTS.md) | [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) |
   | Lesson slide PDFs and PPTX | | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |
   | Templates and their artwork | [templates/AGENTS.md](templates/AGENTS.md) | Asset rules in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#resources-slides-and-assets) |
   | Renderers, build selection, validation, publishing scripts | [scripts/AGENTS.md](scripts/AGENTS.md) | [WORKFLOW.md](system/WORKFLOW.md#pdf-build-selection) |
   | The instructions themselves | [system/AGENTS.md](system/AGENTS.md) | [Maintaining instructions](#maintaining-instructions) |

3. For every edit, follow [WORKFLOW.md](system/WORKFLOW.md). For file creation or binary transfers through a connector, read [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).

### Non-negotiable boundaries

- Use verified facts, canon, names, dialogue, activities, and resource links. Flag missing or conflicting evidence; never invent a substitute.
- Use only `unpublished`, `pending_publish`, and `published` for Drive delivery, per [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Editorial approval is a human merge decision, not a recorded state. Merging an authorized resource change initiates publication once the required automation exists; do not claim it runs today.
- Edit the owning source; do not duplicate resources inside Teacher Guides. Keep required PDF images versioned in GitHub, as separate asset files rather than pre-rendered pages.
- Keep content, visual changes, and publishing actions distinct. Preserve the published seven-slide Activate asset; historical quest-wide slide numbers are not current lesson numbers.
- Use one remote resource branch across chats; multiple agents commit to that branch without force-pushing, reconcile changes against the latest remote head and `main`, and merge only when authorized. Verify the merged result and preserve unrelated work.
- For PDF previews, give the verified **GitHub Actions run URL first**, preferably the post-merge `main` run. Follow [WORKFLOW.md](system/WORKFLOW.md#preview-links-and-retention); do not use a preview-branch or PR Files link as the primary review link.

### Maintaining instructions

- Treat “from now on” and equivalent requests as lasting rules; keep one-time requests within the task. Record lesson-specific decisions in that lesson's existing source/status metadata.
- Find the rule's owner in `START_HERE.md`. Update it there; replace superseded wording and link from other documents instead of copying the rule.
- State the scope, required behavior, and any necessary exception. Use direct instructions and keep examples only when they clarify a decision.
- Search for conflicts and stale references. Update affected templates or behavior within the authorized scope; record remaining work explicitly.
- Keep agents routed: a new source type gets a `$instructions` pointer (defined in `scripts/validate.py`) and a template carrying it; a new folder of editable files gets an `AGENTS.md`, a row in the table above, and an entry in `scripts/build_agents_md.py`.
- Never edit the root `AGENTS.md`; it is generated. After editing any instruction file, run `python scripts/build_agents_md.py`; `scripts/validate.py` fails while `AGENTS.md` is stale. A new instruction file is added to `SOURCES` in that script.
- Keep editorial judgment in prose, shared values in their existing data files, and objective checks in `scripts/validate.py`. Do not add unused enforcement files or speculative tooling.
- Apply explicit user decisions within their scope. If conflicting instructions would change human review scope, publication, or content meaning and intent is unclear, flag the conflict and continue independent work.
- Report where the rule was saved, what now enforces it, and any existing materials still needing updates. Do not silently rewrite or publish the whole collection.

---

# File: `START_HERE.md`

## Little Chewz — start here

Prototype, save editable source to a resource branch, and merge/publish together when authorized. [AGENTS.md](AGENTS.md) is the AI entry point (generated; rules live in [AI_RULES.md](system/AI_RULES.md)); [WORKFLOW.md](system/WORKFLOW.md) owns the editing and delivery routine.

### Where things belong

| Location | Owns |
| --- | --- |
| [AI_RULES.md](system/AI_RULES.md) | AI routing, non-negotiable boundaries, and how instructions are maintained |
| [AGENTS.md](AGENTS.md) | **Generated** from every instruction file (`scripts/build_agents_md.py`); auto-loaded by agents and pasteable into chats. Never edit directly. |
| Each folder's `AGENTS.md` | Which instructions apply to the files in that folder |
| `content/` | Lesson wording, companions, stories, artwork, and lesson delivery status |
| `catalog/quests.json` | Navigation to quest manifests |
| `catalog/resources.json` | Authoritative linked names, stable resource IDs, and verified destinations |
| [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) | Types, paths, version authority, statuses, source/output boundaries, and asset rules (including asset-first templates) |
| [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) | Teacher Guide writing and presentation requirements |
| [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) | Companion writing and presentation requirements |
| [action_labels.json](system/action_labels.json) | Allowed action labels and internal row types |
| [WORKFLOW.md](system/WORKFLOW.md) | Edit, validate, review, save, merge, publish, and report |
| [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) | Slide PDF review, approval, linked-PowerPoint conversion, and in-place Drive replacement |
| [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) | Internal in-place Drive publisher; merge wiring pending |
| [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) | Creating source files and transferring binary assets |
| [COMMANDS.md](system/COMMANDS.md) | `/create`, `/update`, `/merge` agent contract |
| [CREATE.md](system/CREATE.md) | First-time resource creation and cataloguing |
| `templates/` | Templates for supported lesson, companion, and raw-story sources, plus the `claude` page style (clean pages and quest navigation) |
| `scripts/validate.py` | Implemented automatic content checks |
| `scripts/renderers/` | Shared PDF layout and generation code |
| `scripts/select_builds.py`, `scripts/build_selected.py` | Select and build affected eligible PDF previews |
| `tests/` | Checks for the tools |
| `.github/workflows/` | Automated validation and retained PDF previews after PR updates and `main` merges |
| `exports/` | Generated PDFs; never the editable source |
| [SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md) | Tooling backlog; each entry records its implementation status |

### Find a lesson

Follow `catalog/quests.json` → the quest's `quest.json` (lesson status and folder) → `lessons/<stage>/lesson.json` when it exists. An optional short `stage.json` is historical provenance only, not a status owner. The current quest lives at `content/confetti-cake-cottage/quest-01-bake-off-betrayal/`.

Lesson folders run from `00-activate` through `06-celebrate`. Companions live under `resources/teacher_companion/`; raw stories and letters live under `story/`. Read lifecycle status before publishing: a folder or URL does not prove its latest source is live.

### Current capabilities

- Automated builds discover authored lessons and companions through the quest catalog and registry. All valid existing sources can be previewed; registry-built documents (including Welcome) are handled the same way.
- Every existing valid source can generate a preview; five lessons without a `lesson.json` are not renderable. Previews do not publish.
- Slides are maintained per lesson under the content contract. Editable slide generation is not implemented; the **approved-PDF-to-linked-PPTX converter** is available separately (`scripts/pdf_to_linked_slides.py`). [Slide conversion standard](system/SLIDE_CONVERSION.md).
- The validator checks selected required fields, resource references, registry IDs/HTTPS destinations, covers, action labels, and step order. It checks `lesson.json`, but does not fully validate every content structure, test Drive access, or verify publication.

### Local checks and previews

From the repository root, with Python 3.10+:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python -m pip install -r requirements.txt
python scripts/select_builds.py --all --output /tmp/little-chewz-build-selection.json
python scripts/build_selected.py --manifest /tmp/little-chewz-build-selection.json
```

Lato and the other fonts are bundled under `templates/`, so renders match CI. `scripts/build_selected.py` is the supported batch builder; it replaces PDFs in `exports/`, so keep review copies elsewhere. For direct iteration on a single PDF, invoke its renderer in `scripts/renderers/`.

### GitHub previews

Relevant PR updates **and merges to `main`** run validation and tests, then render only affected registered PDFs as permanent browser previews; documentation-only changes produce validation-only runs. Review links, retention, and manual runs follow [WORKFLOW.md](system/WORKFLOW.md#preview-links-and-retention). [Browse PDF previews runs](https://github.com/Programmer484/little_chewz/actions/workflows/build-resources.yml).

The original inventories and superseded slideshow decisions are in [archive/2026-10/](archive/2026-10/README.md); they are not operating instructions.

---

# File: `system/CONTENT_CONTRACT.md`

## Content contract

Owns file organization, source authority, delivery statuses, and source/output boundaries. Writing rules belong in the editorial guides; delivery belongs in [WORKFLOW.md](system/WORKFLOW.md).

### Organization and ownership

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

### Content types

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

### Lifecycle status

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

### Source authority

1. Explicit human decisions within their stated scope, recorded in the owning source or instructions.
2. Current accepted editable content and its quest/resource-catalog delivery records.
3. Current reviewed lesson slides or media for slide-specific details.
4. `Full Guide Revised.pdf` as editorial and visual benchmark, not automatic authority for current slide numbers.
5. Older PDFs as recovery inputs only where editable sources are missing.

A newer timestamp or extraction does not establish publication or content authority. Flag disagreements between records; do not silently choose the more permissive status. Historical reports and backlog proposals do not override current rules or establish implemented capabilities.

### Resources, slides, and assets

- Resolve linked titles and destinations through `catalog/resources.json` (an existing PPTX target may be recorded as `powerpoint_file_id` alongside its lesson PDF resource). The registry object key is the resource ID; omit repeated `resource_id` fields. Retired aliases are archived in [`archive/2026-10/resource-aliases.json`](archive/2026-10/resource-aliases.json). Use stable `ref` IDs in lesson flow, not literal Drive URLs. Missing, stale, or unverified destinations block release; never guess a URL or fall back to unlinked text. A recorded URL does not prove external sharing works.
- Maintain one independent slide set per lesson, with local numbering and a stable resource ID; link that lesson's reviewed set in Preparation. `SHOW`/`KEEP` numbers are navigation, not resource IDs; verify them against that set. The reviewed lesson PDF is the slide source; [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) owns PPTX conversion and Drive replacement. No editable slide renderer exists. Preserve the seven-slide published Activate asset until the human approves a specific revision. Never reuse the archived 44-slide quest-wide numbering ([`quest-slideshow.json`](archive/2026-10/quest-slideshow.json)), merge decks, or republish them automatically.
- Commit every image consumed by a PDF build to GitHub: covers, full-page images, backgrounds, illustrations, and reusable artwork. Keep editable text separately. Required build assets must be repository-local; a Drive link is insufficient.
- **Build templates from individual assets.** When creating or revising a template or a templated document, save each logo, crest, icon, illustration, or other piece of artwork as its own image file (in the template's or document's `assets/` folder) and let the renderer place it alongside live text, colour, rules, and spacing. Do not generate a whole page or template as one image (AI-generated or rasterized), and do not bake editable text into artwork. The one exception is original cover artwork, kept as a losslessly cut `cover.pdf` ([CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md)).
- A finished image distributed directly from Drive, with no PDF-building step, may remain Drive-link-only; retain its stable registry ID and verified link.
- Do not copy large exported PDFs into the source package. A legacy PDF awaiting conversion may remain a migration input. Follow [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) for source creation and binary transfer.

---

# File: `system/WORKFLOW.md`

## Editing and delivery workflow

Applies to all source, instruction, and tooling changes. The three user commands are specified in [COMMANDS.md](system/COMMANDS.md).

### Routine

1. **Inspect.** Identify the resource from chat context and its stable ID in the catalog. Read its source and `$instructions`, the latest remote branch, and `main`.
2. **Edit.** Use **one active branch per resource**, `edit/<stable-resource-id>`. Reuse it across AI chats and agents. Fetch its latest remote head, commit directly to it, and push non-force. If it changed during editing, reconcile and retry without overwriting another agent. Different resources have separate branches. Use temporary child branches only for genuinely overlapping concurrent edits.
3. **Verify.** Check the diff, run `python scripts/validate.py` and relevant tests; render affected supported documents using the repository's renderer. Inspect content, layout, and hyperlinks. Previews are not Drive publications.
4. **Save.** Push source and required assets and open/reuse the resource PR. Never consider local-only output saved.
5. **Merge.** On `/merge` or equivalent explicit user authorization, reconcile with the latest `main`, rerun checks, merge, verify the combined `main` output, and give its post-merge Actions preview. Delete the resource branch only after verifying no unmerged commits remain.
6. **Publish as part of merge.** Existing resources: replace the same Drive file ID in place and verify bytes. New resources: find the proper Drive folder, create the first file, verify its ID/URL and access, then finish catalogue registration. On failure, preserve `pending_publish` if there is an older live Drive version or `unpublished` otherwise, and state the blocker. Never claim `published` before verification.
7. **Report.** Source changes, checks, PR/merge, combined preview link (Actions URL first), Drive result/ID, and any remaining failure.

**Current implementation boundary:** GitHub has validation, targeted previews and an *internal manual* in-place Drive PDF replacement workflow. Merge-triggered publishing, first-time Drive creation and hash-based sync detection are not yet built. Until implemented, follow these steps with the available tools, disclose missing operations, and never pretend merge auto-published. **There is no independent `/publish` user command.**

### Previews and cleanup

- Prefer the verified post-merge `main` Actions run URL; use a PR run when no `main` PDF preview exists. Never invent run URLs. PDF previews use per-run `previews/<run-id>/` directories on the permanent `pdf-preview-history` branch. Workflow artifacts expire after seven days; browser previews remain.
- Delete completed resource branches after verifying merged commits. Preserve review history and any unmerged work. Never merge preview-history branches into `main`, nor delete earlier `pdf-preview-run-*` / `pdf-preview-pr-*` history as a side effect.

### Publishing

Drive delivery is the final phase of `/merge`, not a second user operation. See [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) for the existing internal PDF replacement path, and [CREATE.md](system/CREATE.md) for the first-time registration flow. Keep file IDs and sharing unchanged on replacements. Confirm paired slide PDF and PPTX under [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md). Unverified links block release.

### PDF build selection

PR updates and `main` pushes validate, run tests and rebuild only affected registered PDFs. All existing valid lesson, companion, and registry-rendered sources are previewable regardless of delivery state. Missing `lesson.json` creates no placeholder. Manual preview selection is one exact PDF filename or `all` (all registered outputs); there is no approval-filtered build mode.

A changed source, cover, template asset, renderer, relevant catalog link/title, nav status, or shared build dependency triggers relevant outputs; unrelated documentation, tests, status metadata and raw stories do not on their own render unrelated PDFs. Navigation links are live for `published` or `pending_publish` destinations; `unpublished` shows Coming Soon.

---

# File: `system/EDITORIAL_GUIDE.md`

## Little Chewz — Canonical Teacher Guide / LLM Instructions

**Scope:** These instructions apply to every AI or editor drafting or revising Little Chewz teacher-guide content and to any AI working on the teacher-guide generator. Use **Full Guide Revised.pdf** as the editorial and visual benchmark; use the **latest approved** lesson sequence and slideshow for content. This file governs *writing*, while generator code governs *rendering*.


File locations and source authority are defined in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Edit the current lesson source under `content/`; layout implementation lives in `scripts/renderers/teacher_guide.py`. Validation, review, and delivery follow [WORKFLOW.md](system/WORKFLOW.md).

### 1. Primary editorial rule

**Tell teachers only what they need to do next.** Write concise, practical instructions in the tone of the Revised Full Guide. Eliminate the obvious, redundant reminders, repeated slide content, lengthy explanations, and instructions that don't change what the teacher does.

Keep the existing section structure and terminology unless instructed otherwise: At a Glance, Learning goal, Learning outcomes, Preparation, Teaching focus, Teaching Flow, and purposeful optional extensions. **Assessment is optional** and, when used, appears as a standalone section below Teaching focus. Never add an assessment task that is missing from the Teaching Flow.

### 2. Learning design: goal, outcomes, focus and assessment

**Learning goal**
- One concise sentence identifying the central educational purpose.
- Describe the learning, not a list of activities.

**Learning outcomes**
- Normally **three** short, observable, student-centred statements, roughly the length of the original guide.
- Begin with a useful action verb such as **ask, identify, describe, explain, compare, apply, reflect**.
- Avoid vague outcomes such as “understand” or “explore” without visible evidence of what students can do.
- Do not write “By the end of Activate…” or any equivalent introductory preamble.
- Fit the evidence and demands of the actual lesson; do not introduce assessment tasks or predictions students have not yet been equipped to make.

**Teaching focus**
- **One short sentence; one instructional priority.** Write in the direct, practical tone of the original guide.
- Avoid multiple “listen for / check / prompt” demands, and avoid assessment boilerplate.

**Assessment — optional**
- Include an Assessment section **only when it adds specific guidance beyond Teaching focus**, such as explaining what to look for in selected worksheets, activity products, or performance tasks. Omit it entirely for Activate, celebrations, or any lesson where Teaching focus already supplies sufficient guidance.
- **Assessment is not an additional activity**. Do not ask teachers to administer extra exit slips, worksheets, discussion questions, checks, or marking steps that do not already appear in the Teaching Flow.
- Tie evidence to the materials and choices **already listed in the Teaching Flow**. For choice-based lessons, give short resource-specific indicators so the teacher uses only the lines for activities selected (e.g., `Clue Tracker: identifies relevant evidence and a reasonable inference`).
- Describe **observable student thinking or work**, not vague participation; never assume every learner demonstrated understanding because a few students answered aloud.
- Do not duplicate Learning outcomes or Teaching focus; give practical evidence cues that a teacher can recognize from existing student responses, notes, discussion, or work.
- Brief, formative wording only. No formal grading or new rubric unless the chosen activity already requires one.
- In lesson JSON, **omit `assessment`**, set it to `null` or `""`, or use `[]` to hide the section. To include it, use a short string or an array of concise material-specific bullet strings. The PDF generator will include the section only when there is content.

**Approved Activate model**

Learning goal: Spark curiosity about Confetti Cake Cottage School and introduce the Zenix approach to solving mysteries through careful observation, thoughtful questions, and understanding different perspectives.

Learning outcomes:
1. Ask thoughtful questions about the school and its mysteries.
2. Identify an unusual detail about Callie Cupcake.
3. Explain why Zenix gather information and consider different perspectives before judging.

Teaching focus: Encourage students to seek understanding before making judgments.

Assessment: Omitted — Teaching focus is sufficient for Activate.

### 3. Resource labels, descriptions, and links

**Presentation pattern:** **Linked Resource Title** `—` concise, light-grey description. In generated PDFs the linked title is **bold and underlined**; the em dash and description are **light grey**. A title may appear alone when no description adds value.

- **All resource-registry items must have working approved links.** Do not allow unlinked resource names as a fallback; missing destinations are errors to resolve before release.
- **Underline means hyperlink** and nothing else. Do not underline ordinary text for emphasis.
- Keep descriptions brief and functional: e.g. `Mrs. Tongsley's Letter — Opening read-aloud`, `Chapter One — Full chapter`, `Teacher Answer Key — Teacher reference`.
- Never invent link targets or replace a missing approved resource with a guessed URL.
- Keep extra questions, full stories, student-facing material, worksheets, answer keys, and supporting resources in their **separate linked files**.
- Each lesson has **its own slide set/deck**. Link only that lesson's approved slideshow in Preparation. In Teaching Flow, `SHOW`/`KEEP` slide numbers are local to the lesson and must be verified against its current approved slides. Historical quest-wide slide numbers are not current lesson numbers.
- A command such as `SHOW Slides 1–3 — Introduce the school.` is slide navigation, **not** a separately linked resource entry. `KEEP Slide 3 — Display during the welcome letter.` is likewise slide navigation.

**Preparation should be a resource list, not an instruction paragraph.** Its purpose is to show what the teacher needs ready before class.

- Under **CORE RESOURCES**, list the lesson slideshow and materials used by every student or class, with one linked resource title per line.
- When activities offer alternatives, use **PREPARE YOUR CHOICES** for choice-dependent materials. Reserve **OPTIONAL PREPARATION** for extras that are not tied to an activity choice.
- Give each resource a short `—` description only when useful, such as which choice uses it or how many copies to prepare (`One per student`, `One per group of 3–4`). Keep activity directions in Teaching Flow.
- Omit activities that require no separate resources or printing and routine classroom supplies. Do not compress resource lists into an italic `prep_note` paragraph or repeat listed materials in prose; use a note only for essential setup information that cannot fit on a resource line.

### 4. Approved Teaching Flow action labels

Prefer this deliberately small vocabulary; use the label only when the action genuinely adds information.

| Label | Meaning |
| --- | --- |
| **SHOW** | Display or advance to specified slide(s); play media embedded on a slide. |
| **KEEP** | Remain on a named slide during the following action or passage. |
| **READ** | Open a linked reading for independent, group, or teacher read-aloud. |
| **LISTEN** | Play or direct students to a linked standalone audio recording, including as a reading alternative. |
| **ASK** | Ask the strongest, most relevant discussion question. |
| **DO** | Give a short, concrete classroom direction. |
| **GIVE** | Distribute or direct students to a linked student resource. |
| **MORE** | Link supplementary teacher resources or additional prompts. |

Avoid `NOTE`, `WATCH`, `CHECK`, `TIME`, `USE`, `OR`, `CHOICE`, `CHOOSE`, and `PLAY` as action labels. Do not create near-synonyms. For alternate ways of completing the same reading task, title the step `Read or Listen` and put `READ` and `LISTEN` on equal action rows, with no Option 1/2 labels or extra indentation. Give instructions that apply to both in a single `DO` row, using `For either format` when needed. Reserve structured A/B/C/D options for different Small Bite activities. Use `SHOW` for media embedded on slides and `LISTEN` for standalone linked audio.

**For engineering:** [action_labels.json](system/action_labels.json) owns the allowed labels and internal row types; the table explains usage. The validator and renderer must consult that file when checking validity. Rendering branches for specialized content are still appropriate.

### 5. How to write a Teaching Flow step

- Use the established **number, title, duration**, then brief labelled action rows.
- Start with the **action**. Prefer compact imperatives over explanations: `DO Pair-share for two minutes.`
- Give **one meaningful instruction per row**; avoid long paragraphs unless the paragraph itself is an approved READ excerpt.
- Follow the classroom sequence. Do not introduce the task twice (once in the title and again in the first row).
- Use the minimum number of rows needed; do not pad steps with SHOW/ASK/DO by habit.
- Give **one strong ASK question**. Put optional extra questions under MORE as linked resources.
- Say what teachers need to *do*, not why each step is pedagogically important.
- Do not repeat the wording on the slide or narrate what the video already says.
- Use exact slide numbers/ranges from the **current approved lesson slide set**, not from a historical quest-wide deck.
- Avoid navigation-only rows. Mention a transition only when it changes what the teacher needs to do.
- Follow the concise writing of **Full Guide Revised.pdf**, not the wordier Activate Teacher Guide phrasing.

**Example of preferred brevity**

```text
SHOW   Slide 5 — Play Mrs. Tongsley's video.
ASK    What are you wondering about after her message?
MORE   Mrs. Tongsley's Video — Direct video preview. [linked resource]
```

**Slide continuity**

```text
SHOW   Slides 1–3 — Introduce the school.
KEEP   Slide 3 — Display during the welcome letter.
READ   Mrs. Tongsley's Letter — Opening read-aloud. [linked resource]
```

Use KEEP only when staying on the slide is a meaningful instruction, not on every row that happens to leave a slide visible.

**A/B alternatives:** Preserve the original four-page Set the Table teaching-flow style. For a lesson with choices, set `flow_style: "compact"` and put each alternative under `step.options` with `label` (A/B), `title`, and its own `rows`. Do not flatten alternatives into ordinary rows prefixed `A —` or `B —`. Every Teaching Flow, with or without options, uses one shared grid (44 / 82 / 129 / 551 pt): step numbers at 44; options mirror the step heading one level down (a heavy accent letter about 13% larger than its bold option title, right-aligned just before it, the same ratio as step number to step title). Step numbers and option letters are vertically centred on their title (text-box middles aligned); step titles set tight beside the number (just past the widest two-digit number) so options read as indented subsets of the step; option titles and action labels at 82 in every step; instruction text at 129; times and page counters right-aligned at 551. Labels share a baseline with their text, option rows use the same type as ordinary rows, options are separated by a 0.5 pt warm-grey rule from 82 pt, and every divider has equal optical space above and below. Spacing values live as named constants at the top of the layout section in `scripts/renderers/teacher_guide.py`. Longer or revised activities may move later sections down without changing the option typography and spacing.

### 6. READ passages and excerpts

- For an approved, short passage, use the existing **indented READ passage with a coloured vertical rule**, preserving paragraph breaks and selective bold emphasis. **Do not add literal quotation marks.**
- Include excerpts only for short passages **under approximately 250 words**; this is authorial guidance, **not a programmed word-count check**.
- For longer readings, link to the **full resource** and ask the teacher to open/read it. Do not paste full student-facing stories or lengthy teacher resources into the Teacher Guide.
- Preserve the approved wording of any passage. Do not silently rewrite dialogue, lore, named characters, or the Zenix rule.
- The presence of an excerpt does not make it an unlinked resource-registry item; an explicit resource reference still requires a link.

### 7. Generator engineering boundaries

- Preserve existing PDF-native style, Lato typography, section-colour configuration, page margins and other deliberate design choices unless a change is requested.
- Handle typesetting, mixed emphasis, hyperlinks, measurable fitting/wrapping, whole-step pagination, continuation cues and destination integrity **in code**.
- Handle tone, step concision, vocabulary, passage length, exact educational priority and pedagogy **in these LLM instructions**, not in brittle heuristic validators.
- **Keep missing-resource links as errors.** Do not weaken existing strict link behaviour.
- Do **not** introduce a code-enforced 250-word limit, a banned-`NOTE` special case, or hard-coded length checks for Learning outcomes/Teaching focus.
- Prefer minimal, localized changes and data-driven configuration. Keep content and layout responsibilities separate; do not duplicate source text inside rendering functions.
- Follow the workflow for rendered-output review. Report layout discrepancies rather than silently changing approved text to fit.

### 8. Editorial review

- Are the goal, outcomes and Teaching focus **short** and tightly aligned to the actual activities?
- If Assessment is included, does it identify evidence within the selected existing materials, without adding a task or duplicating Teaching focus?
- If Assessment adds no distinct value, has it been omitted rather than padded with boilerplate?
- Does Teaching focus convey **one** idea?
- Could a teacher scan every step and act without rereading it?
- Have explanatory filler and redundant rows been removed?
- Does `KEEP Slide N` clearly cover each important continuity instruction?
- Are all resource references linked, bold and underlined, with concise grey `— descriptions` where useful?
- Are slide numbers verified against the corresponding lesson-specific slideshow?
- Are passages short, properly indented, and faithful to approved source text?
- Are links, resource names, page breaks, accents and wording checked before publishing?

### 9. MORE resources and alternatives

- Use **MORE**, not **EXTEND**, as the standard Teaching Flow label for optional linked resources. **Default to exactly one MORE block per Teaching Flow activity (step or choice), with each resource on its own new line.** Store multiple resources in a single `links` array in their intended display order. The renderer also combines separate MORE rows in the same activity for compatibility; do not intentionally author duplicate MORE rows.
- Present each resource as **bold, underlined linked title** followed by a short light-grey `— description`, such as `Mission Video Questions — Additional questions`.
- In Teaching Flow, the linked resource title and description (including **MORE** rows) use the same standard body font size as **DO** instructions. Do not shrink linked descriptions to fit; shorten the wording or adjust the shared layout instead.
- Put supplementary discussion questions in separate linked PDFs, not in the core teacher-guide flow.
- When a video has a written alternative, keep the video in SHOW and link the readable source under MORE, e.g. `Bakery Log (1958) — Read-aloud alternative to video`.
- Do not create a new mandatory teaching step for an optional extension or fallback.

### Companion resources

Illustrated instruction pages, question banks, and multi-variant chooser PDFs follow [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md). Keep the Teacher Guide itself concise and link to them rather than embedding their content.

---

# File: `system/action_labels.json`

Allowed Teacher Guide action labels and internal row types (data read by the validator):

```json
{
  "teacher_guide_actions": [
    "SHOW",
    "KEEP",
    "READ",
    "LISTEN",
    "ASK",
    "DO",
    "GIVE",
    "MORE"
  ],
  "internal_row_types": [
    "QUOTE"
  ],
  "note": "Central source for editorial action labels; QUOTE is a renderer-only long read-aloud row rendered as READ."
}
```

---

# File: `system/RESOURCE_GUIDELINES.md`

## Companion resource guidelines (Draft)

Companions support the Teacher Guide without repeating its Teaching Flow. Each must make sense when opened alone. These guidelines retain their draft status; this cleanup does not approve content.

### Writing

- Give each document one clear purpose and an activity-specific title, such as **Songwriting Extension**.
- Start with what the teacher needs to do. Include only necessary steps, prompts, materials, and examples; avoid long lesson-plan sections.
- State additional time when applicable, separately from core lesson time.
- Preserve approved content and terminology. Never invent activities to fill a template.
- Keep optional questions optional. Omit generic prompts or learning-focus sections unless they add practical value.
- Do not add a “Back to Teaching Flow” link; the resource opens in a new tab.

### Presentation

- Default to a small section name, clear resource title, optional time, and ample white space.
- Identify the origin with section accent colour plus text; never rely on colour alone.
- No decorative header, badge, page number, or boxed layout by default. Use illustrations, setup photos, badges, or folder motifs only when they aid comprehension or navigation.
- Match the Teacher Guide's readable typography and economical palette. Use one title style across companions and **8 pt title-to-section-label spacing**.
- Keep question banks easy to scan. An illustrated instruction page is appropriate when it demonstrates setup, printing, assembly, or use.
- For multiple resource variants, link the Teacher Guide to one instruction/chooser PDF that links to the separate versions.

### Source and generation

Companions use JSON with optional `paragraph`, `steps`, `questions`, `bullets`, `heading`, `note`, `image`, `links`, and `spacer` blocks. No fixed block order, minimum count, one-page requirement, or decorative filler. Start from `templates/teacher_companion/TEMPLATE.json`.

Use the ownership and approved-link rules in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Layout implementation lives in `scripts/renderers/teacher_companion.py`; follow [WORKFLOW.md](system/WORKFLOW.md) for checking, previews, and publication. See [START_HERE.md](START_HERE.md#local-checks-and-approved-previews) for current commands.

---

# File: `templates/claude/README.md`

## `claude` template: clean page style and quest navigation

A left-aligned A4 page style for Little Chewz documents, matching the Confetti Cake Cottage School look: cream page, crest or Little Chewz logo, brush headline, coral numbers and labels, hairline dividers. It includes a quest navigation page that links each stage to its Teacher Guide.

- `TEMPLATE.json`: skeleton document showing every block type (`lede`, `paragraphs`, `list`, `callout`, `nav`).
- Renderer: [`scripts/renderers/claude.py`](scripts/renderers/claude.py), with ReportLab and pypdf. Each page's spacing stretches to fill the page; a page that overflows fails loudly.
- `assets/`: school crest and Little Chewz logo (extracted from the Welcome PDF) and open-licensed fonts. New artwork goes here as separate files, never as a pre-rendered full page ([asset rule](system/CONTENT_CONTRACT.md#resources-slides-and-assets)).

```bash
python scripts/renderers/claude.py \
  content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json \
  --output exports/01-welcome.pdf
```

### Navigation links

`nav` rows name a stable resource ID from `catalog/resources.json`. A row shows **Open Guide** and becomes clickable only when that entry is `pending_publish` or `published` with an HTTPS URL; otherwise it shows **Coming Soon**. Never put Drive URLs in the document JSON.

### Fonts

The Canva originals (Better Faster, Glacial Indifference) are only partially embedded in the source PDF and Better Faster is commercial, so they cannot be reused. This template uses SIL OFL stand-ins: Lobster for headlines and Outfit for body text. Licences are in `assets/fonts/`.

### Status and builds

A document using this style is registered in `catalog/resources.json` with `"build": {"renderer": "claude", "source": "<path to its JSON>"}`. That makes it a PR preview target named `<resource-id>.pdf`, rebuilt when its JSON, anything in its folder, these assets, or the renderer changes. The same build feeds **Publish to Drive** ([DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md)). Rendering does not publish anything.

Current consumer: the Quest One Welcome PDF (`ccc-q01-welcome`).

---

# File: `system/SLIDE_CONVERSION.md`

## Classroom slide PDF → PowerPoint

Owns the slide PDF review, PPTX conversion, and in-place Drive replacement routine. Status rules belong to [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md); general saving and reporting follow [WORKFLOW.md](system/WORKFLOW.md). Human review is separate from publication status; nothing here publishes without authorization.

### Routine

1. **Iterate on the PDF.** A human downloads the **lesson-specific PDF** from the [Slide PDFs Drive folder](https://drive.google.com/drive/u/0/folders/1Qryh6aiuHsZqiTpzP_BvulK-W43EK45g). Human and AI iterate on that PDF (page order, content, clickable links). It is the review artifact; the PowerPoint is never the editing source. Keep each lesson's slides separate. Do not update Drive while iterating.
2. **Approval gate.** The human must explicitly approve the **exact final PDF** and intended lesson. A past approval, GitHub merge, generated PPTX, or passing conversion check does not approve a changed PDF. The approved PDF's actual page count and order are authoritative: lesson metadata and outlines are context, never a slide-count requirement, so do not add or remove slides to match them. Ask only when the approved artifact itself is ambiguous.
3. **Convert and check** (below).
4. **Replace both existing Drive files in place:** the PDF and its paired existing binary `.pptx` (not a copy, new file, or native Google Slides conversion). A missing PPTX destination is a blocker, not permission to create one. Stage and check both deliverables before replacing either.
5. **Read back and report** the exact file IDs and approval scope. Only the exact reviewed version, replaced and verified, may become `published`; uploading alone never advances status.

### Conversion

From the repository root after `pip install -r requirements.txt`:

    python scripts/pdf_to_linked_slides.py reviewed.pdf -o reviewed.pptx --json conversion-report.json

Default: **PyMuPDF render 1.5x → Pillow JPEG quality 92 → python-pptx**. Every PDF page becomes one full-bleed slide image, so text is intentionally not selectable. PDF URI and internal page links become transparent PowerPoint hotspots in their original clickable positions. **Unsupported PDF actions fail by default**. Do not pass `--allow-unsupported-links` on a publication build.

For exceptionally small type: `--scale 2 --quality 94`. Preserve the PDF's original aspect ratio; mixed-aspect input fails.

A previous **seven-page** Set the Table benchmark took approximately **1.1 seconds**, yielding a **5.07 MB** PPTX with both link annotations preserved (about **66% smaller** than its earlier PPTX). This is an indicative local benchmark, not an upload-time guarantee.

### Required checks before and after replacement

1. Verify pages and links against the approved PDF; the PPTX must match it exactly.
2. Run the converter; require **zero warnings**, exact page/slide count, one full-slide image per slide, and URL/internal-link parity. A picture of a play button is **not** working media unless it has a preserved link.
3. Open text-heavy and linked slides visually. Test all links in PowerPoint; **after opening the PPTX in Google Slides, use Present mode and test links again**. File validation alone cannot prove Google Slides click behavior or Drive media permissions.
4. Before upload, read target Drive metadata and verify expected **file ID and MIME type** (PDF: `application/pdf`; PPTX: `application/vnd.openxmlformats-officedocument.presentationml.presentation`). Replace bytes via Drive **files.update** / connected app's `update_file(fileId, file_uri, mime_type)`, not upload/create or rename. Preserve file IDs, folder placement, and sharing.
5. Read back both files' metadata (IDs, MIME types, updated sizes/times) and confirm the PPTX opens and its external links work. If one replacement fails, report the partial state and retry/restore deliberately; never claim the pair was published successfully.

### Verified current Drive targets (2026-10-22)

| Lesson | Existing PDF file ID | Existing PPTX file ID | Current review state |
| --- | --- | --- | --- |
| Activate | `1l_QwHQPRvKCL_n43xlvTyDHFxQy8poE_` | **Not located** | Published seven-slide PDF. Do not create/replace a PPTX without locating or approving a destination. |
| Set the Table | `1r5w-EWU3N47iz5p02NSOsmN-P7Kv7QJt` | `1PQnFI3ryAvTj70NNKmlWqfbdkOcDUPkd` | **Approved 7-slide PDF and PPTX replaced in place on 2026-10-22.** |

The PDFs are in the folder above. The Set the Table PowerPoint was located separately as `Set_The_Table_Slides.pptx`; it is a stored PPTX, not a native Google Slides file. Its file ID is also recorded with the lesson resource in `catalog/resources.json`. Confirm these IDs and MIME types **afresh** for each publication.

**Latest Set the Table publication (2026-10-22):** human selected the seven-slide edition: slide 6 “Which Word Fits?”, slide 7 “Friendship Mystery #1”. The original six-page PDF's other pages remain visually unchanged; both approved Drive files were updated in place and two audio URL link annotations are preserved on slide 4. Verified remote sizes: PDF 11,933,343 bytes, PPTX 5,034,225 bytes. External PDF link-sharing to unauthenticated viewers has **not** been verified; do not change permissions without approval. The uploaded Activate PDF is seven pages with a video URL link on pages 4 and 5; no Activate PPTX target was identified.

### Future editable slides

Editable slide-JSON generation remains **unimplemented** (see [SYS-002](SYSTEM_IMPROVEMENTS.md#sys-002--editable-lesson-slide-generation)). This utility only packages an approved PDF into a PowerPoint and restores PDF link annotations; it is not a slide editor, an automatic GitHub preview target, or an autonomous Drive publisher.

---

# File: `system/DRIVE_PUBLISHING.md`

## Publishing to Google Drive

Owns the internal in-place Drive publish step. Delivery status rules belong to [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md); the edit and review routine belongs to [WORKFLOW.md](system/WORKFLOW.md).

### What it does

**Internal fallback (not a user command):** Actions → Publish to Drive → Run workflow takes one registry ID from `catalog/resources.json` and:

1. Runs only from `main`, using the same setup, validation, and tests as PDF previews (`.github/actions/pdf-setup`); publishing adds only the Google client packages.
2. Refuses the entry unless its status is `pending_publish` or `published`. `unpublished` requires a new-file creation path, which is not yet implemented.
3. Builds the PDF from the entry's `build` instructions through `scripts/build_selected.py`, the same builder as GitHub previews.
4. Checks the Drive destination (from `url`) is a PDF the service account can edit.
5. Replaces the file's contents in place (`files.update`). The file ID, link, name, folder, and sharing stay the same; Drive keeps the previous version in **Manage versions**.
6. Verifies Drive's MD5 matches the local PDF, then changes a `pending_publish` entry to `published` and commits that to `main`.

Run it first with **dry run** ticked (the default): it builds and checks access without uploading. Every run attaches the built PDF as a run artifact. Merge-trigger automation remains to be implemented; no standalone user-facing `/publish` command exists.

### Registering a document

Add `build` to the registry entry. The entry's `url` must be the existing Drive file to replace.

```json
"ccc-q01-welcome": {
  "url": "https://drive.google.com/file/d/<file-id>/view",
  "status": "pending_publish",
  "build": {"renderer": "claude", "source": "content/.../welcome/welcome.json"}
}
```

The renderer is `scripts/renderers/<renderer>.py`, and the entry becomes a preview target named `<resource-id>.pdf`. For a Teacher Guide or companion, name its preview output instead: `"build": {"output": "00-activate-teacher-guide.pdf"}`.

Currently registered: `ccc-q01-welcome` (Quest_Overview.pdf in 00_WELCOME).

### One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.

---

# File: `system/CHAT_FILE_CREATION.md`

## Creating and transferring source files

Applies to files created, extracted, or updated through chat. Source/status rules belong to [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md); branch, PR, review, and delivery requirements belong to [WORKFLOW.md](system/WORKFLOW.md). A successful upload proves storage, not editorial approval or permission to publish.

### Choose the available path

- **Local checkout:** write the exact source files, inspect them, and commit/push through the normal workflow. No connector transfer is needed.
- **Connector, one UTF-8 file:** use GitHub text-file creation/update; fetch the existing SHA before replacement.
- **Connector, multiple files or binary assets:** use the batch procedure below. Never stop at “the connector cannot upload binary” without checking its Base64 blob + tree/commit/ref capabilities.

Keep text editable. Commit every image required by a PDF build to its source location; extract legacy covers faithfully rather than inventing replacements. Save a cover as a one-page `cover.pdf` cut losslessly from the source PDF (for example `qpdf --empty --pages <source.pdf> <page> -- cover.pdf`), never as a rasterized PNG: rasterizing turns vector text into pixels and lowers artwork resolution. Do not pass PNG/JPG/PDF/ZIP/font bytes to text-file actions or Git tree `content` fields.

### Connector batch procedure

Use one tree and commit for related files; the same procedure handles a single binary. Tool names below describe capabilities and may vary by connector.

1. **Prepare.** Confirm intended paths, the owning lifecycle status, exact bytes, and UTF-8 text. Calculate expected binary Git blob SHAs where possible: SHA-1 of `blob <byte_length>` + one NUL byte + file bytes. Preserve artwork unless a change is requested.
2. **Obtain Base64 privately.** Prefer direct access to the source bytes. If unavailable, upload required local assets as uniquely named, non-public temporary Drive files through `files.manage_library` (prefer `source_file_ref.file_id`, otherwise `container_path`). Batch multiple uploads; retain exact returned IDs and sizes. Fetch those files with `Google_Drive.fetch({url, download_raw_file:true, include_base64:true})`. Check signatures, types, and sizes; never print Base64.
3. **Upload blobs.** Call `GitHub.create_blob({repository_full_name, content:b64_string, encoding:"base64"})` for each binary. Independent fetches/blob uploads may run concurrently; await every result and retain its path and blob SHA.
4. **Read the current branch.** Obtain its head commit SHA and that commit's actual `tree.sha`, for example via GET `/repos/{owner}/{repo}/git/commits/{head_sha}`. Do not substitute a commit SHA for a tree SHA. Work on the source review branch, not directly on `main`.
5. **Create one tree.** Call `GitHub.create_tree({repository_full_name, base_tree_sha, tree_elements})`. Binary entries use `{path, mode:"100644", type:"blob", sha:<blob SHA>}`; UTF-8 entries use `{path, mode:"100644", type:"blob", content:<text>}`. Preserve unrelated paths.
6. **Commit and advance.** Call `GitHub.create_commit` with that tree and the previous head as parent, then `GitHub.update_ref` with `force:false` and `expected_sha:<previous head>`. If the branch moved, rebuild against its new head; never overwrite concurrent changes.
7. **Verify remote files.** Fetch each committed binary with `GitHub.fetch_file({path, ref:branch, encoding:"base64"})`. Require its blob SHA to match the upload and the local expected SHA where available. Compare/parse committed text, inspect important images, and verify the commit contains every intended path. Only then record assets as committed.
8. **Clean temporary transfers.** Delete only the exact temporary IDs created in step 2 using `Google_Drive.delete_file`; verify deletion. The Library deletion action did not support Drive in the tested workflow. Remove temporary test fixtures before merge and report any cleanup failure. Never delete teacher-facing originals.

Transfer only authorized project files. Do not include secrets, create public transfer links, or use this procedure to bypass permissions. Complete validation, output review, and PR delivery under the workflow; a green preview covers only registered outputs.

### Verification history

The connector procedure was verified on 2026-10-19 for a single binary ([PR #8](https://github.com/Programmer484/little_chewz/pull/8)) and a batch of two PNGs plus one JSON file ([commit fe197fec](https://github.com/Programmer484/little_chewz/commit/fe197fec38888fd2bd64d63c797a8b63a2ed2d22)); remote blob SHAs matched and temporary Drive files were deleted. Covers have since moved to losslessly cut `cover.pdf` files, per the rule above.

---

# File: `system/COMMANDS.md`

## Command contract

The only user-facing commands are **`/create`**, **`/update`**, and **`/merge`**. Natural-language instructions after a command apply. Infer the resource from conversation and confirm its ID against current GitHub records. These files define agent behavior; slash-command aliases require separate client configuration.

### `/create [instructions]`

The user has already prototyped the resource in chat. Follow [CREATE.md](system/CREATE.md): establish identity, create/reuse `edit/<stable-resource-id>`, commit editable sources/assets to GitHub, register intent as `unpublished`, validate and share the PR preview. **Do not upload to Drive yet.**

### `/update [instructions]`

Find/reuse the resource's branch (or branch from current `main` if missing), fetch its latest remote head, edit only the requested scope, validate, commit and push without force. Multiple agents across chats use the same resource branch. On concurrent updates reconcile rather than overwrite.

### `/merge [instructions]`

This is permission to accept the resource change and initiate publication. Reconcile the latest `main`, verify and merge, show the **combined `main`** output, and delete the branch after checking that all intended commits were merged. Replace the existing Drive destination in place, or create the first file in its proper Drive folder and update the catalogue. Verify exact deliverables and set `published` only after confirmation. On failure retain `pending_publish` (older live Drive version) or `unpublished` (none) and report the blocker.

**No `/publish` command.** Publication is part of `/merge`. Today the merge-trigger orchestration is not built; the manual GitHub Action is an internal temporary fallback. Never claim the automatic step executed if it did not.

---

# File: `system/CREATE.md`

## First-time resource creation

This procedure follows **`/create` after a prototype already exists** in the AI conversation.

1. Identify the resource's school, quest, lesson and type. Search existing IDs and Drive records; reuse an existing identity rather than duplicating it. Choose a new stable resource ID only when genuinely new.
2. Create/reuse its `edit/<stable-resource-id>` branch based on latest `main`. Follow the source's `$instructions` and supported template. Commit editable content and separate required assets to GitHub; avoid output-only PDFs as editable source. For binary transfers follow [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).
3. Reserve the item in `catalog/resources.json` with type, title, tags and status `unpublished`; do not guess a Drive URL or folder ID. A lesson's status lives in its `quest.json`. Validate the source and provide the GitHub preview.
4. Continue iterations through `/update` on the same branch. On `/merge`, reconcile and merge, build the accepted `main` version, determine the actual appropriate Drive lesson/quest folder from existing Drive records, create the first file there, verify its ID/type/access, and only then register the URL and mark `published`.
5. If Drive folder, permissions, build output, or verification is missing, keep `unpublished` and report it. For existing resources, never create a duplicate: replace in place and preserve file IDs and sharing.

**Not implemented yet:** automated first-time Drive creation and the merge orchestrator. This is the required agent workflow; do not claim unsupported operations ran.

---

# File: `SYSTEM_IMPROVEMENTS.md`

## System improvements

This file tracks **active** system work. The original migration and completed CI proposals are preserved in [archive/2026-10/](archive/2026-10/README.md).

Live editing, status and publishing rules belong to [WORKFLOW.md](system/WORKFLOW.md), [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) and [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md). A backlog item never grants permission to publish to Drive.

### SYS-004 — Merge-triggered Drive publication

**Status:** Planned, not implemented. **Priority:** High.

Wire `/merge` to the accepted `main` build, in-place Drive replacement or first-time creation in the correct folder, file verification, and stored published-build digests. Automatically detect `pending_publish` without agent-maintained flags. Support paired PDF/PPTX resources. Remove the internal manual fallback only after this flow is verified; do not add a `/publish` command.

### SYS-002 — Editable lesson slide generation

**Status:** Planned, not implemented. **Priority:** Optional.

Current slides are independently maintained human-reviewed lesson PDFs. The supported `scripts/pdf_to_linked_slides.py` tool derives image-based, linked PowerPoint files from an approved PDF.

An eventual editable slide renderer could regenerate a single changed slide or the affected lesson from reviewed editable sources. Build this only when a real editing need justifies it. Do not add placeholder slide JSON, reuse the old continuous 44-slide deck, introduce unused templates, or automatically publish to Drive.

### SYS-003 — Teacher-owned presentation copies

**Status:** Proposed, not implemented. **Priority:** To be decided.

Allow each teacher to make or receive their **own copy of a lesson's slide deck**, then mark slides they do not want to show as **skipped/hidden during presentation**, without deleting the slides or changing the master deck.

**Desired result:**
- Each teacher can independently choose which slides appear in their presentation.
- Hidden slides remain available for the teacher to restore later.
- The approved master deck and other teachers' copies stay unchanged.
- Preserve slide order, clickable media/resource links, and lesson-local numbering wherever the presentation format supports them.

**To determine before implementation:** Teacher access and the copy-delivery workflow (for example, a copyable Google Slides presentation versus a downloadable PowerPoint). Confirm that the chosen format actually supports skipping slides during its presenter/slideshow mode and that copied media links continue to work. This is a teacher-facing convenience feature, **not** permission to edit or republish the approved master.

### Already implemented

- GitHub Actions validation, targeted PDF previews, and permanent browser previews on a shared history branch: [WORKFLOW.md](system/WORKFLOW.md#pdf-build-selection).
- Approved lesson PDF to linked PPTX conversion: [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- Prior designs and completed proposals: [historical system improvements](archive/2026-10/SYSTEM_IMPROVEMENTS_ORIGINAL.md).

---

# File: `content/AGENTS.md`

## Editing teaching content

Every source file in this folder opens with a `$instructions` key (stories: an `instructions:` frontmatter line) naming the guides to read before editing it. `scripts/validate.py` requires it, and the templates carry it, so new files get it too.

| Editing | Read first |
| --- | --- |
| `<school>/<quest>/quest.json` | [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#lifecycle-status). It owns lesson delivery status; branch-only edits do not change it. |
| `lessons/<stage>/lesson.json` | [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md), then [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) |
| `lessons/<stage>/stage.json` | Provenance only. To convert a lesson, start from [templates/teacher_guide/TEMPLATE.json](templates/teacher_guide/TEMPLATE.json). |
| `resources/teacher_companion/*.json` | [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) |
| `story/*.md` | [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md); approved text only, wording preserved |
| `welcome/` (registry-built documents) | [templates/claude/README.md](templates/claude/README.md) |
| Lesson slides (Drive PDFs, not stored here) | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |
| Covers, icons, artwork | [Asset rules](system/CONTENT_CONTRACT.md#resources-slides-and-assets): separate image files, covers as cut `cover.pdf` |

Linked resource names, URLs, and companion status live in [catalog/resources.json](catalog/AGENTS.md), never in these files. After editing, run `python scripts/validate.py` and save through a PR per [WORKFLOW.md](system/WORKFLOW.md).

---

# File: `catalog/AGENTS.md`

## Editing the catalog

- `resources.json` is the single owner of every linked resource's name, Drive URL, status, and (for built documents) `build` instructions. Its keys are the stable resource IDs. Rules: [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#resources-slides-and-assets) and [lifecycle status](system/CONTENT_CONTRACT.md#lifecycle-status).
- Never guess or invent a URL. A missing or unverified destination blocks release; flag it.
- Use only delivery statuses `unpublished`, `pending_publish`, `published`; no editorial approval flag. A verified Drive replacement sets `published`; newer `main` output with an older live destination is `pending_publish`. Publishing: [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) or [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- `quests.json` is a navigation index to each quest's `quest.json`, which owns lesson status.

Run `python scripts/validate.py` after any edit; it checks IDs, statuses, HTTPS destinations, and every reference.

---

# File: `templates/AGENTS.md`

## Editing templates

Templates are starting structures for supported source types: `teacher_guide/` (lesson.json), `teacher_companion/`, `story/`, and the `claude/` page style with its assets. `fonts/` holds the bundled Lato (OFL) used by the Teacher Guide and companion renderers; it is the same Lato 2.015 CI used before it was bundled. Add a template only for a source type with a working authoring workflow.

- **Build templates from individual assets.** Logos, crests, icons, and illustrations go in the template's `assets/` folder as separate image files that the renderer places around live text. Never generate or rasterize a whole page as one image. Full rule: [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#resources-slides-and-assets).
- Each `TEMPLATE.json` opens with the same `$instructions` pointer its sources need (the story template has an `instructions:` line), so copies inherit it. `scripts/validate.py` checks this.
- Renderers live in `scripts/renderers/`, not here ([scripts/AGENTS.md](scripts/AGENTS.md)).

---

# File: `scripts/AGENTS.md`

## Editing tooling

| File | Purpose | Read first |
| --- | --- | --- |
| `renderers/teacher_guide.py` | Teacher Guide PDF layout | [EDITORIAL_GUIDE.md §7](system/EDITORIAL_GUIDE.md#7-generator-engineering-boundaries) (layout constants, Lato, strict links) |
| `renderers/teacher_companion.py` | Companion PDF layout | [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md#presentation) |
| `renderers/claude.py` | `claude` page style (Welcome PDF) | [templates/claude/README.md](templates/claude/README.md) |
| `select_builds.py`, `build_selected.py` | Which PDFs a change previews, and the batch builder | [WORKFLOW.md: PDF build selection](system/WORKFLOW.md#pdf-build-selection) |
| `validate.py` | Objective source checks, including `$instructions` pointers and `AGENTS.md` freshness | [AI_RULES.md: maintaining instructions](system/AI_RULES.md#maintaining-instructions) |
| `build_agents_md.py` | Regenerates the root `AGENTS.md` from all instruction files | Run after editing any instruction file |
| `publish_to_drive.py` | Internal in-place Drive replacement (merge wiring pending) | [DRIVE_PUBLISHING.md](system/DRIVE_PUBLISHING.md) |
| `pdf_to_linked_slides.py` | Reviewed slide PDF to linked PPTX | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |

A renderer for a registry-built document is `renderers/<name>.py`, matching `build.renderer` in `catalog/resources.json`. When adding a renderer input or changing how builds are invoked, update `select_builds.py` and `tests/` in the same PR. Run `python scripts/validate.py` and `python -m unittest discover -s tests`.

---

# File: `system/AGENTS.md`

## Editing instructions

The files here own the repository's rules; each states what it owns in its opening lines, and [START_HERE.md](START_HERE.md#where-things-belong) maps every rule to its owner. Follow [AI_RULES.md: maintaining instructions](system/AI_RULES.md#maintaining-instructions): change a rule only in its owner, replace superseded wording, and link instead of copying.

After editing any instruction file, run `python scripts/build_agents_md.py` to regenerate the root `AGENTS.md`; `scripts/validate.py` fails while it is stale. Never edit the root `AGENTS.md` itself. `action_labels.json` is data read by the validator.
