# Little Chewz: agent instructions

> **Generated file. Do not edit.** Built by `python scripts/build_agents_md.py` from the instruction files below; change a rule in its owning file, then regenerate.
> Repository: https://github.com/Programmer484/little_chewz

You are helping edit the Little Chewz teaching-material repository. This file is the complete, current set of rules, in the order to read them, and can be pasted into any AI chat. Each part is headed by the file that owns it. Paths are relative to the repository root.

If you cannot read the repository directly, ask the user to paste the exact current file before proposing changes to it, and return complete replacement text for each changed file with its path. Never reconstruct file contents, URLs, statuses, or Drive IDs from memory.

## Contents

- `system/AI_RULES.md`
- `START_HERE.md`
- `system/CREATE.md`
- `system/UPDATE.md`
- `system/PUBLISH.md`
- `system/CONTENT_CONTRACT.md`
- `system/WORKFLOW.md`
- `system/EDITORIAL_GUIDE.md`
- `system/action_labels.json`
- `system/RESOURCE_GUIDELINES.md`
- `templates/welcome/README.md`
- `system/SLIDE_CONVERSION.md`
- `system/CHAT_FILE_CREATION.md`
- `SYSTEM_IMPROVEMENTS.md`
- `content/AGENTS.md`
- `catalog/AGENTS.md`
- `templates/AGENTS.md`
- `scripts/AGENTS.md`
- `apps/AGENTS.md`
- `system/AGENTS.md`

---

# File: `system/AI_RULES.md`

## AI rules: routing, boundaries, maintaining instructions

Owns how agents find instructions, the non-negotiable boundaries, and how instructions are maintained. The root `AGENTS.md` is generated from this file and the other instruction files.

This is an editable educational source repository. PDFs are outputs; legacy PDFs are inputs only while awaiting conversion.

### First stop: choose the workflow

Read the independent workflow for the requested action (no slash-command integration exists):

- **Create** a new resource: [CREATE.md](system/CREATE.md). Stage a draft in holding; do not publish.
- **Update** an existing resource: [UPDATE.md](system/UPDATE.md). Revise and review without disturbing the live version.
- **Publish** an approved resource: [PUBLISH.md](system/PUBLISH.md). Verify the official Drive version before recording publication; generated-PDF updates may use an authorized release-PR merge.

For IDs, URLs and statuses read [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md); for shared preview/validation conventions read [WORKFLOW.md](system/WORKFLOW.md).

### Read for the task

1. Read [START_HERE.md](START_HERE.md) for navigation and current capabilities, and [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) for ownership, status, assets, and version authority.
2. Open the file you will change. Its `$instructions` key (stories: `instructions:` frontmatter) names the guides to read first. Each folder's `AGENTS.md` routes everything in it:

   | Changing | Folder guide | Main rules |
   | --- | --- | --- |
   | Lessons, companions, stories, quest status, Welcome | [content/AGENTS.md](content/AGENTS.md) | [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md), [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) |
   | Resource names, links, status, publishing | [catalog/AGENTS.md](catalog/AGENTS.md) | [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) (data), [PUBLISH.md](system/PUBLISH.md) (actions) |
   | Lesson slide PDFs and PPTX | | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |
   | Templates and their artwork | [templates/AGENTS.md](templates/AGENTS.md) | Asset rules in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#resources-slides-and-assets) |
   | Renderers, build selection, validation, publishing scripts | [scripts/AGENTS.md](scripts/AGENTS.md) | [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup) |
   | Teacher web apps (Print Pack Builder) | [apps/AGENTS.md](apps/AGENTS.md) | App README; registry rules in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) |
   | The instructions themselves | [system/AGENTS.md](system/AGENTS.md) | [Maintaining instructions](#maintaining-instructions) |

3. For every edit, follow [WORKFLOW.md](system/WORKFLOW.md). For file creation or binary transfers through a connector, read [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md).

### Non-negotiable boundaries

- Use verified facts, canon, names, dialogue, activities, and resource links. Flag missing or conflicting evidence; never invent a substitute.
- **Derive** resource states `unpublished`, `pending_publish` and `published` using [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md), never store a resource `status` field. For external resources, a distinct staged holding URL signals pending; for generated PDFs, approved/current MD5 differs. Publishing still needs explicit approval and verification. Lesson editorial status in `quest.json` is separate.
- Edit the owning source; do not duplicate resources inside Teacher Guides. Keep required PDF images versioned in GitHub, as separate asset files rather than pre-rendered pages.
- Keep content, visual changes, and publishing actions distinct. Preserve the published seven-slide Activate asset; historical quest-wide slide numbers are not current lesson numbers.
- Work on the **shared lesson branch** by default (`lesson/<quest-id>-<two-digit-stage>-<stage-slug>`), across all lesson resources and chats. Create separate task branches only on explicit user instruction. Reconcile with the remote head and `main`, never force-push, and preserve unrelated work. External files use their original creation tool and lesson catalogue bookkeeping.
- For PDF previews, give the verified **GitHub Actions run URL first**, preferably the post-merge `main` run. Follow [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup); do not use a preview-branch or PR Files link as the primary review link.

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

Prototype in chat, then follow the **independent workflow matching the action**. [AGENTS.md](AGENTS.md) is the generated AI entry point. Shared definitions and checks are in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) and [WORKFLOW.md](system/WORKFLOW.md).

### Choose a workflow

- **[Create](system/CREATE.md):** for genuinely **new** resources only; stage a review copy in holding and stop before publication.
- **[Update](system/UPDATE.md):** for **existing** resources; revise on the shared lesson branch, validate, and preserve the live release.
- **[Publish](system/PUBLISH.md):** after explicit human authorization, deliver the exact reviewed resource, verify the official Drive file, then save the official URL and approved checksum; resource status derives automatically. Existing generated PDFs use a guarded release-PR merge within this workflow.

Use one `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch per lesson unless you explicitly request a separate task branch. No chat slash-command integration exists; ordinary GitHub merges and previews do not publish.

### Where things belong

| Location | Owns |
| --- | --- |
| [AI_RULES.md](system/AI_RULES.md) | AI routing, non-negotiable boundaries, and how instructions are maintained |
| [AGENTS.md](AGENTS.md) | **Generated** from every instruction file (`scripts/build_agents_md.py`); auto-loaded by agents and pasteable into chats. Never edit directly. |
| Each folder's `AGENTS.md` | Which instructions apply to the files in that folder |
| `content/` | Lesson wording, companions, stories, artwork, and lesson delivery status |
| `catalog/quests.json` | Navigation to quest manifests |
| `catalog/resources.json` | Stable IDs, production classification, holding/published URLs, builds and publication records |
| `catalog/drive_folders.json` | Verified holding folders (including separate Slide PDFs) and official folder configuration |
| [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) | Types, paths, version authority, statuses, source/output boundaries, and asset rules (including asset-first templates) |
| [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md) | Teacher Guide writing and presentation requirements |
| [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) | Companion writing and presentation requirements |
| [action_labels.json](system/action_labels.json) | Allowed action labels and internal row types |
| [WORKFLOW.md](system/WORKFLOW.md) | Shared validation, preview, and review/reporting conventions |
| [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) | Slide PDF review, approval, linked-PowerPoint conversion, and in-place Drive replacement |
| [PUBLISH.md](system/PUBLISH.md) | Single publication owner for generated PDFs and external resources, checks and verification |
| [CHAT_FILE_CREATION.md](system/CHAT_FILE_CREATION.md) | Creating source files and transferring binary assets |
| [UPDATE.md](system/UPDATE.md) | Standalone resource revision workflow |
| [CREATE.md](system/CREATE.md) | Standalone draft creation and holding-folder staging |
| `templates/` | Templates for supported lesson and companion sources, plus the `welcome` page style (clean pages and quest navigation) |
| `scripts/validate.py` | Implemented automatic content checks |
| `scripts/renderers/` | Shared PDF layout and generation code |
| `scripts/select_builds.py`, `scripts/build_selected.py` | Select and build affected eligible PDF previews |
| `tests/` | Checks for the tools |
| `.github/workflows/` | Automated validation and retained PDF previews after PR updates and `main` merges |
| `exports/` | Generated PDFs; never the editable source |
| `apps/` | Standalone teacher web apps, such as the [Print Pack Builder](apps/print-pack-builder/README.md); read-only consumers of the catalogue, never publishers |
| [SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md) | Tooling backlog; each entry records its implementation status |

### Find a lesson

Follow `catalog/quests.json` → the quest's `quest.json` (lesson status and folder) → `lessons/<stage>/lesson.json` when it exists. An optional short `stage.json` is historical provenance only, not a status owner. The current quest lives at `content/confetti-cake-cottage/quest-01-bake-off-betrayal/`.

Lesson folders run from `00-activate` through `06-celebrate`. Companions live under `resources/teacher_companion/`; raw stories and letters live under `story/`. Derive lifecycle status from official URL / holding URL or generated checksum before publishing: a folder or URL does not prove its latest source is live.

### Current capabilities

- Only `generated_pdf` resources (Teacher Guides, Python-rendered companions, Welcome) use editable GitHub branches and an authorized release-PR merge/checksum pipeline. First release needs manual destination setup.
- `external` resources (including PDFs made outside the renderer, posters, images, worksheets and slide pairs) stay in holding until an agent manually publishes and verifies them. No automatic external release or checksum tracking.
- [Drive holding](https://drive.google.com/drive/folders/1UJYL2ADO7_pfrLSK1BpzstaHCoBmx-jJ) now mirrors the official four categories: `01_TEACHER_GUIDES`, `02_CLASSROOM_SLIDES`, `03_STUDENT_MATERIALS`, `04_EXTRA_RESOURCES`. Existing subfolders retain their Drive IDs; legacy Slide PDF originals remain in their separate review folder. Holding is not publication.
- Use Create, Update, and Publish workflow documents directly; no chat slash commands are configured.

- Automated builds discover authored lessons and companions through the quest catalog and registry. All valid existing sources can be previewed; registry-built documents (including Welcome) are handled the same way.
- Every existing valid source can generate a preview; five lessons without a `lesson.json` are not renderable. Previews do not publish.
- Slides are maintained per lesson under the content contract. Editable slide generation is not implemented; the **approved-PDF-to-linked-PPTX converter** is available separately (`scripts/pdf_to_linked_slides.py`). [Slide conversion standard](system/SLIDE_CONVERSION.md).
- The validator checks selected required fields, resource references, registry IDs/HTTPS destinations, covers, action labels, and step order. It checks `lesson.json`, but does not fully validate every content structure, test Drive access, or prove external content parity. An on-demand read-only inspection workflow is available.

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

Relevant PR updates **and merges to `main`** run validation and tests, then render only affected registered PDFs as permanent browser previews; documentation-only changes produce validation-only runs. Review links, retention, and manual runs follow [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup). [Browse PDF previews runs](https://github.com/Programmer484/little_chewz/actions/workflows/build-resources.yml).

The original inventories and superseded slideshow decisions are in [archive/2026-10/](archive/2026-10/README.md); they are not operating instructions.

---

# File: `system/CREATE.md`

## Create a NEW resource

**Use only when a resource does not yet exist.** Check `catalog/resources.json`, the lesson source and Google Drive first. If its stable ID or intended file already exists, stop creation and use [UPDATE.md](system/UPDATE.md)—do not create duplicates or overwrite an existing resource. Use [WORKFLOW.md](system/WORKFLOW.md) for common validation, review and saving.

### Branch ownership

- Default to the **existing lesson branch**, `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` (for example `lesson/ccc-q01-02-secret-ingredients`). Create it from current `main` only if it does not exist. All new Teacher Guides, companions and lesson-associated sources for that lesson share the branch.
- Do **not** create separate task branches, nested-looking feature branches or PRs for individual resources unless the user explicitly requests one. Git branches do not nest. Non-lesson-wide items (for example Welcome) use their existing ownership branch; if none exists, use a dedicated resource branch.
- Reconcile the lesson branch with latest remote changes and `main` before editing; never force-push or override another agent.

### New Python-generated PDF

1. Confirm school, lesson, resource type, **unused stable ID**, source path, and supported build renderer/output.
2. Author editable JSON and required separate versioned assets on the lesson branch; use the repository renderer, validate, test, and inspect pages and working hyperlinks.
3. Upload a new **Teacher Guide** PDF under `01_TEACHER_GUIDES/PDF-generated resources`; a generated **companion** belongs under `04_EXTRA_RESOURCES/Other resources`. Use the configured existing holding folder ID, then read back the Drive ID and URL. The special Welcome material retains its established folder routing.
4. Register `production_type: generated_pdf`, source/build mapping, `holding_url`, and `published_url: null` in `catalog/resources.json`. Review PDFs can link to unpublished resources using their existing permanent Drive IDs.
5. Push the lesson branch, open/update its review PR and share the Actions review and holding link. **Stop without publication.**

### New external worksheet, artwork, slide or media

### Student-facing worksheet PDFs — US Letter

- When creating a resource registered as `student_worksheet`, make **every PDF page US Letter (8.5 × 11 in / 612 × 792 pt)**, portrait or landscape.
- Before uploading the worksheet to Drive holding, run `python scripts/pdf_page_size.py path/to/worksheet.pdf` and fix any failed pages. Inspect the printed layout; do not stretch A4 content to fit.
- **Only** student-facing worksheets have this paper-size rule. Do not resize Teacher Guides, companions, references, artwork or classroom slide PDFs.

1. Create the new resource with the original authoring tool (not the repository PDF renderer); register `production_type: external`.
2. Upload to the matching verified holding category in `catalog/drive_folders.json`, and read back its ID, MIME and URL. Existing legacy Slide PDF originals retain their separate approved review folder until explicitly moved.
3. Add only catalogue bookkeeping on the lesson branch: `holding_url`, resource identity, source provenance and `published_url: null`. If no source branch is needed, save the catalogue change through the lesson's ordinary GitHub PR; do not create a resource-specific branch by default.
4. Preserve the verified Drive URL for links in review PDFs. Once published by **moving the same file**, the ID and URL remain unchanged.

### End of creation

Creation ends with a verified new resource staged in holding, registered and ready for review. **Never publish, change the official `published_url` or promote Drive files** during Create. A subsequent revision follows [UPDATE.md](system/UPDATE.md); an explicitly authorized release follows [PUBLISH.md](system/PUBLISH.md). Status and URL semantics belong to [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md).

---

# File: `system/UPDATE.md`

## Update an existing resource

Use this workflow when asked to **revise, fix, or replace an existing resource**, whether draft or published. Resolve its stable ID, exact GitHub source and Drive IDs from current records. If the resource does not exist, use [CREATE.md](system/CREATE.md) instead. This is a **review operation, not publication**. See [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) for status/URL semantics and [WORKFLOW.md](system/WORKFLOW.md) for shared checks.

### Python-generated PDFs

1. Use the existing shared `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch; only create it from `main` if absent. Reconcile its latest head with `main`. Do not create a separate task branch unless explicitly requested; preserve concurrent edits and never force-push.
2. Edit authorized JSON/text source and separate required assets; keep the current official file ID, live URL and publication evidence unchanged.
3. Validate, test, render through the existing repository PDF renderer and inspect the pages and clickable links.
4. Upload or replace the **review PDF in holding**, keeping its existing category: Teacher Guides under `01_TEACHER_GUIDES`, companions under `04_EXTRA_RESOURCES`. Preserve the file ID when possible and update `holding_url` only if needed.
5. Save source to GitHub, open/update the PR and share the actual Actions run and review copy. A passing build or ordinary merge is not publication.

### External resources

### Student-facing worksheet PDFs — preserve US Letter

- When updating a resource registered as `student_worksheet`, keep **every PDF page US Letter (8.5 × 11 in / 612 × 792 pt)**, portrait or landscape.
- After revising and **before uploading** the replacement review copy, run `python scripts/pdf_page_size.py path/to/worksheet.pdf`. Fix any page-size failures without distorting content.
- This requirement does **not** apply to Teacher Guides, companions, references, artwork or classroom slide PDFs.

1. Edit using the original creation tool; do not invent a Python renderer or separate per-resource branch.
2. Replace the same holding Drive file in place where possible; otherwise stage a new review copy in the verified appropriate holding folder.
3. Verify ID, MIME, size, URL, visuals, text and links. Slide-specific PDF/PPTX review checks are in [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
4. Save catalogue bookkeeping on the shared lesson branch through its existing PR when available. Preserve the published file, verified `published_url`, compatibility `url` and current publication evidence; a new holding URL distinct from the official URL derives a pending update; do not replace the official link.

### Finish

Report the review copy, GitHub PR/record, checks and blockers. **Do not replace or move the official Drive file as part of an update.** When the user later approves publication of that exact version, follow [PUBLISH.md](system/PUBLISH.md).

---

# File: `system/PUBLISH.md`

## Publishing resources to Google Drive

**Single authoritative publication procedure** for Python-generated PDFs and externally authored resources. Creating belongs to [CREATE.md](system/CREATE.md), revising to [UPDATE.md](system/UPDATE.md), shared review checks to [WORKFLOW.md](system/WORKFLOW.md), and field and derived-status definitions to [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Creating, revising, ordinary PR merges and previewing do not publish.

### Publication prerequisites and release gate

1. Confirm explicit human authorization for the **exact reviewed resource/version**, its stable ID, production type, current publication record and official Drive destination. A holding upload or passing check does not imply approval.
2. Prefer **moving the same holding file** to its official folder to preserve Drive file ID and URL. Verify that the ID remains unchanged; if copying creates a new ID, register the verified new ID and update references. Do not confuse a valid link with publication; **folder placement and successful verification authorize recording an official link**. Never guess IDs or folders.
3. **Automated release gate:** Before publishing a generated Teacher Guide (or companion), check every referenced registry ID: require a verified official `published_url`; otherwise block. This is enforced in the guarded merge publisher **and** the direct Drive replacement command. For external resources, an agent must perform the equivalent registry check before delivery; no external-resource release automation exists. A resource's original Drive URL may stay identical when moved from holding to official—the gate checks the official URL, not a stored status.
4. Verify official file identity, MIME, parent folder and sharing/access as far as the tools allow. User testing in incognito is useful but not a substitute for accurate agent records; do not claim incognito testing the agent cannot perform.
5. **Only after successful official Drive verification**, update `published_url`, compatibility `url`, publication evidence (no stored resource status) in `catalog/resources.json`. When moving the same file, the permanent URL is unchanged. Clear `holding_url` when an external replacement goes live; a different holding link is the pending-update signal for all non-generated resources, including slides. Published resources always link through `published_url`, including in preview PDFs. Never manufacture a different link. Neither a URL nor metadata access alone proves anonymous access.

### External resources — agent-managed publication

Worksheets, posters, external PDFs, media and slides use `production_type: external` and are not published by the generated-PDF release mechanism or Python PDF builds.

1. Move the exact reviewed file to the verified teacher-facing folder, preserving its ID where possible. For a previously published asset, replace the official file **in place** rather than creating duplicates.
2. Read back the official file ID, MIME, folder and access metadata. For slides, [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) adds mandatory PDF/PPTX pairing, conversion and verification; both must be checked.
3. After successful verification, commit the catalogue record: `published_url`, compatibility `url`, and honest `publication` confirmation (file ID and verification method/time). Retain holding history only where appropriate.
4. On failure, report the precise blocker. An unapproved new file has no official URL. For a revised external file, preserve the official URL and stage the new version under a different `holding_url`; derived state becomes `pending_publish`. Never invent checksums or assert external content parity without evidence. Prefer automated Drive metadata checks; reserve human incognito testing for access behavior tools cannot prove.

### First-time generated PDF publication — agent-managed
#### Student worksheet PDF check before external publication

For any `student_worksheet` PDF, run `python scripts/pdf_page_size.py path/to/worksheet.pdf` **before uploading or replacing the official Drive file**. Every page must be US Letter (8.5 × 11 inches), portrait or landscape. This check is for student-facing worksheets **only**; do not change Teacher Guide, companion or slide page sizes. External resources are still published by an agent rather than the generated-PDF publisher.


Move the exact approved generated PDF from holding to the verified official teacher-facing folder (or create a verified official copy if necessary). Read back its ID, MIME, access, and exact file version. Only then register the official URL, ID and publication evidence; the resource state derives automatically. This establishes the official file for subsequent in-place automated updates; the automated replacement workflow does **not** create first-time destinations.

### Authorized release PR for an established generated PDF

1. The agent confirms the exact reviewed PDF and human approval, reconciles the **shared `lesson/<quest-id>-<stage>` branch** (legacy `edit/<resource-id>` accepted) with latest `main`, and adds `.github/resource-releases/<PR-number>.json` listing only the explicitly authorized resource IDs. Each listed resource must belong to that branch and independently pass publication checks; other lesson resources on the branch do not automatically publish.
2. The agent merges that resource PR into `main`; **only** the merged generated-PDF resource PR with its explicit marker triggers `.github/workflows/release-on-merge.yml`. Ordinary pushes and other PRs never publish.
3. The workflow checks the accepted source and resource mapping, runs shared validation/tests and builds using `scripts/build_selected.py`. If a newer `main` update superseded the accepted PDF, publishing is blocked.
4. An already-established official `published_url` must identify an editable Drive PDF. The publisher replaces the **same file ID** in place, preserves its name, folder and sharing, then reads back the file's ID and MD5.
5. Only after exact verification does GitHub record the approved checksum, accepted Git revision and Drive version/time. Before upload, a changed GitHub-generated PDF derives as `pending_publish` when its checksum differs; after verified replacement it derives as `published`. On failure, leave the old approved checksum intact and report a blocker. No unverifiable digest or reported upload success can mark `published`.
6. The release Action provides its report and matching post-merge `main` PDF preview. **Keep the shared lesson branch** for subsequent work. Legacy per-resource `edit/` branches may be cleaned up only after verified release and only if they have not advanced; preserve concurrent additions.

### Manual fallback and review copies

**Actions → Internal Drive replacement** is a controlled fallback for `generated_pdf` resources with verified existing official destinations. Use dry run first and the same read-back verification. It is not an external-resource publisher or a user-facing publishing command.

For draft creation, stage a Teacher Guide PDF under the configured `01_TEACHER_GUIDES` holding folder, or a generated companion under `04_EXTRA_RESOURCES`; use the verified folder IDs in `catalog/drive_folders.json`. This is never publication. `holding_url` is a draft pointer, `published_url` the official pointer and `url` only legacy compatibility. The holder may be the same original file before initial release; never treat it as a second version by string inequality alone. Do not change an established Drive ID for housekeeping. Draft procedure: [CREATE.md](system/CREATE.md).

The publisher resolves only recorded official targets. Registry build examples: `{"build":{"renderer":"welcome","source":"content/.../welcome.json"}}` or `{"build":{"output":"00-activate-teacher-guide.pdf"}}`. `scripts/select_builds.py` resolves these. No external resource receives a Python build just because it is a PDF.

### Automatic publication inspection

The **authorized release** and **Internal Drive replacement** workflows automatically inspect each newly published resource after saving its verified publication record; a FAIL or NEEDS REVIEW makes that publication workflow red. **Actions → Inspect published resources** remains an optional manual full/targeted check. The inspector is read-only and checks every resource with an official `published_url` (including those with a pending update): Google Drive public permissions unless marked for human review, and exact-URL human review for external links. Only a confirmed FAIL makes the job red; NEEDS REVIEW remains visible in a compact link table. The inspector does not compare PDF content, folders or Teacher Guide hyperlinks. See [INSPECTION.md](system/INSPECTION.md) for the single audit rule set. External links requiring manual review record `human_review` by exact URL. Publication approval and checksum safeguards remain separate from the lightweight link inspector.

### One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.

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
| Companion blocks | `resources/teacher_companion/*.json` within the quest; resource delivery is derived from publication evidence |
| Raw stories and letters | `story/*.md` within the quest |
| Stable IDs, production method, holding/published URLs, builds and publication evidence | `catalog/resources.json` |
| Shared starting structures | `templates/teacher_guide/`, `templates/teacher_companion/`, `templates/welcome/` (clean page style and quest navigation) |
| Verified review and official Drive folder configuration | `catalog/drive_folders.json` |
| Shared document generation | `scripts/renderers/` |
| Generated PDFs | `exports/` only |

Each resource has one content owner. Teacher Guides reference resources by stable ID; they do not copy whole resource text. Keep templates and renderers shared, outside quests.

Use lowercase kebab-case for new content filenames and folders, retaining established paths. Lesson order is `00-activate`, `01-set-the-table`, `02-secret-ingredients`, `03-the-showdown`, `04-chew-on-this`, `05-plate-it-forward`, `06-celebrate`. Stable content IDs follow `ccc-q01-<stage>-<slug>`; never use a filename, extension, location, or changing display title as identity. Preserve existing IDs and published Drive file IDs.

### Content types

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

### Production workflows and delivery states

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
| `holding_url` | Optional staged replacement/draft URL. For non-generated resources, a distinct holding file means an update is pending. Clear it when the approved replacement goes live. Same Drive file ID is not a distinct draft. |
| `published_url` | Verified official destination; may be the **same URL as the former holding URL** if the same file was moved without changing its Drive ID |
| `url` | Legacy compatibility link; never establishes publication. If `published_url` exists, **both preview and release** link only to it; otherwise a draft preview may use `holding_url` or `url`. |
| `publication` | Explicit evidence/uncertainty: verification, method, confirmed revision/version, file ID, and generated-PDF MD5 only when actually checked |
| `human_review` | Exact-URL map: `{"https://...": "pending"}` or `reviewed`. Required for published non-Drive links; optional for standard Drive or generated links. Approval is invalidated when the URL changes. |\n| `review_mode` | Optional `human` for externally owned Drive links, bypassing automated Drive checks. Human review does not bypass checks for ordinary Drive links. |\n| `print` | Optional, student worksheets only: `{"cards_per_sheet": N}` when each page holds N identical cards, counted from the actual file. Read by the [Print Pack Builder](apps/AGENTS.md) to print sheets instead of one page per card. |

When an externally published resource is converted to `generated_pdf`, keep its live URL and `external_agent` publication evidence unchanged; the validator accepts that evidence without a digest until the next verified generated release replaces the file in place. For legacy resources whose Drive history is uncertain, preserve existing links, notes and delivery status; record publication verification as `unverified` or `unknown` rather than inventing a digest or pretending a historic upload was confirmed.

Resource delivery has **three derived states**; never store a separate resource `status` field:

| Derived state | Rule |
| --- | --- |
| `unpublished` | No `published_url` |
| `pending_publish` | An official URL exists **and** a distinct holding file exists (external resources), or the current GitHub-generated PDF MD5 differs from the approved `publication.artifact_md5` (generated PDFs) |
| `published` | An official URL exists and no pending change was detected |

Compare holding and published **Drive file IDs**, not incidental sharing URL parameters. For generated PDFs, the current PDF must be built before comparing MD5. A missing approved/current checksum is **unknown parity**, not proof of a match; inspection and publication approval handle that separately. The official resource remains available while an update is pending.

**Human approval remains mandatory.** Staging or a checksum change never publishes a resource. The publisher retains the established official file ID, checks Drive read-back, then saves the new approved MD5. External publication records an official link only after verification; clear the holding link after release. For legacy uncertain records, retain explicit verification uncertainty, never invent approval.

**Separate lesson status:** `quest.json.learning_sequence[].status` is the editorial lesson lifecycle and remains stored. Resource publication state is calculated by `scripts/publication_state.py` from `catalog/resources.json`, not stored. A lesson and its Teacher Guide may have different states.

Publishing and initial official-link authorization belong to [PUBLISH.md](system/PUBLISH.md). Generated guides/companions require every linked resource to have an official URL, even if its next version is pending. Inspection checks the existing published destination independently of whether a newer version is staged. There is no external auto-publisher or scheduled inspector.

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

## Shared editing and review checks

Use alongside the independent [Create](system/CREATE.md) and [Update](system/UPDATE.md) workflows. This file owns common validation, preview, source coordination and reporting conventions, **not publication**. Release steps live in [PUBLISH.md](system/PUBLISH.md); status definitions in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md).

### Source and branch hygiene

- Read the owning file's `$instructions` pointer and verify current stable ID, GitHub revision, catalogue record and Drive metadata before writing.
- Default to a shared remote `lesson/<quest-id>-<two-digit-stage>-<stage-slug>` branch for all work on that lesson. Reuse it across chats and resources; reconcile concurrent changes against its latest head and `main`, without force-pushing. **Only create a separate task branch when the user explicitly requests it.** Commit required images separately from text.
- Externally authored resources stay in their own creation tool and save catalogue changes on the lesson branch, not the generated-PDF pipeline. Non-lesson resources retain their established owner branch.
- Commit source changes, verify remote state and exclude secrets, temporary transfers and generated exports. Preserve unrelated work.

### Validation and previews

- Run `python scripts/validate.py` for content changes and relevant tests for tooling changes. Render generated PDFs with the repository renderer; inspect layout, content and links, and verify the review file in its holding folder.
- `scripts/select_builds.py` and `scripts/build_selected.py` are the supported Python preview path. Valid authored sources can be previewed regardless of delivery status; absent lesson sources produce no placeholders. Manual selection accepts an exact output filename or `all`.
- PR updates and `main` pushes validate and rebuild affected PDFs. Changes to sources, used assets, renderers, referenced resource links or shared dependencies rebuild their consumers. Documentation-only and publication-evidence-only changes generally do not rebuild PDFs; changing an official resource URL rebuilds linked PDFs.
- Give the verified **GitHub Actions run URL first** for PDF reviews (prefer the successful post-merge `main` run). Previews remain under `pdf-preview-history/previews/<run-id>/`; workflow artifacts expire sooner. Never automatically merge or delete historical preview branches.

### Report and stop

Report saved file locations, checks, preview links and unresolved blockers. Holding uploads, validation passes and ordinary merges **never prove publication**. For authorized official releases, linked-resource preflight, external publication, generated-PDF release merging and approved URL/checksum changes use [PUBLISH.md](system/PUBLISH.md).

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

**Preparation lists only what the teacher must do before students arrive**, not the lesson's resources. The test: does it need lead time, or would meeting it for the first time in front of the class go badly? If not, link it at its step. Most of a lesson can be taught by walking through the guide, so Preparation is usually the slides, sometimes a long reading, and the print pack.

- Under **CORE RESOURCES**, link the lesson slideshow to review. When the slides play video, the description also says to test one (`Review slides; test a video`), because blocked or silent video is the likeliest thing to break mid-lesson. One test covers every video on the same host; checking that each video is still online is the repository's job, not the teacher's. Do not list the videos separately; their direct links stay at their steps as a fallback.
- Add a long reading the teacher leads, such as a full chapter (`Read ahead`), and anything to buy, book or set up, such as food (allergies first), devices or a room change. Put safety-critical choices first and name the decision. Short read-alouds, answer keys, extra questions, extensions and audio alternatives stay at their steps.
- Under **PRINT YOUR CHOICES** (`prep_heading`), link the lesson's print pack once: catalogue entry `<lesson-id>-print-pack`, which opens the Print Pack Builder at that lesson. It replaces lists of printable worksheets. Until the builder is deployed this entry is an unpublished placeholder, which blocks the guide's release, so add it only to guides being prepared for the builder.
- Link every other resource only at its point of use in Teaching Flow (`GIVE`, `READ`, `LISTEN`, `MORE`). Before removing a resource from Preparation, check that a step links it; otherwise move its link into that step. The Print Pack Builder finds worksheets at their steps.
- Give each preparation link a short, action-oriented `—` description, such as `Review slides 1–7`, `Read ahead` or `Choose activities, print once`. Omit routine supplies. Do not compress preparation links into an italic `prep_note` paragraph; use a note only for essential setup that cannot fit on a resource line.

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

Companions (question banks, extensions, answer keys and other teacher pages) support the Teacher Guide without repeating its Teaching Flow. Each must make sense when opened alone. These guidelines retain their draft status; this cleanup does not approve content.

### Writing

- Give each document one clear purpose and an activity-specific title, such as **Songwriting Extension**.
- Start with what the teacher needs to do. Include only necessary steps, prompts, materials, and examples; avoid long lesson-plan sections.
- State additional time when applicable, separately from core lesson time.
- Preserve approved content and terminology. Never invent activities to fill a template.
- Keep optional questions optional. Omit generic prompts or learning-focus sections unless they add practical value.
- Do not add a “Back to Teaching Flow” link; the resource opens in a new tab.

### Presentation

Every companion uses the shared resource masthead and footer, rendered by `scripts/renderers/teacher_companion.py`; do not restyle individual documents.

- **Masthead (page 1):** school crest, `CONFETTI CAKE COTTAGE · QUEST 01`, the section label in its accent colour (`PART 2 · SECRET INGREDIENTS`), a resource-type tag at the top right, the title, one grey meta line, then a full-width accent rule. Later pages carry a one-line running header.
- **Section and colour** come from the companion's `stage` and `quest.json`, using the Teacher Guide's section palette. Never set them by hand; colour always appears with the section name.
- **Resource-type tag** comes from `kind`: `questions`, `extension`, `answer_key`, `instructions` or `reference`. Add a new kind to `RESOURCE_TAGS` in the renderer only when a real resource needs it.
- **Title:** short and matching the resource's catalogue title, so the Teacher Guide link and the document agree. No section names or dashes in the title.
- **Meta line:** two or three short facts in `meta`: whether it is optional, added time, and when or with what to use it (`Optional · Adds about 15–25 minutes · Follows Small Bite 1: School Song`).
- **Footer:** `LITTLE CHEWZ · CHEWLANDIA ACADEMY` and `page / total` on every page.
- **Numbered lists (tight column, approved 2026-10-31):** numbers on the margin in the section colour, same size and baseline as their text; text 12 pt after the widest number. `questions` and `answers` rows are separated by hairline dividers with equal 11 pt optical space above and below; `steps` show a bold title line and are separated by whitespace only. Dividers and gaps never strand at a page edge.
- **Group labels:** `heading` blocks render as small tracked caps in the section colour, for groups such as `Core · Clue Tracker page 1`.
- No other decorative headers, badges or boxes. Use illustrations or setup photos only when they aid comprehension.
- For multiple resource variants, link the Teacher Guide to one instruction/chooser PDF that links to the separate versions.

### Source and generation

Companions use JSON with required `title`, `kind`, `stage` and `meta`, an optional `intro`, and optional `paragraph`, `steps`, `questions`, `answers`, `bullets`, `heading`, `note`, `image`, `links`, and `spacer` blocks. List blocks number continuously across a document; set `start` on a block to restart. No fixed block order, minimum count, one-page requirement, or decorative filler. Start from `templates/teacher_companion/TEMPLATE.json`.

Use the ownership and approved-link rules in [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Layout implementation lives in `scripts/renderers/teacher_companion.py`; follow [WORKFLOW.md](system/WORKFLOW.md) for checking, previews, and publication. See [START_HERE.md](START_HERE.md#local-checks-and-approved-previews) for current commands.

---

# File: `templates/welcome/README.md`

## `welcome` template: clean page style and quest navigation

A left-aligned A4 page style for Little Chewz documents, matching the Confetti Cake Cottage School look: cream page, crest or Little Chewz logo, brush headline, coral numbers and labels, hairline dividers. It includes a quest navigation page that links each stage to its Teacher Guide.

- `TEMPLATE.json`: skeleton document showing every block type (`lede`, `paragraphs`, `list`, `callout`, `nav`).
- Renderer: [`scripts/renderers/welcome.py`](scripts/renderers/welcome.py), with ReportLab and pypdf. Each page's spacing stretches to fill the page; a page that overflows fails loudly.
- `assets/`: school crest and Little Chewz logo (extracted from the Welcome PDF) and open-licensed fonts. New artwork goes here as separate files, never as a pre-rendered full page ([asset rule](system/CONTENT_CONTRACT.md#resources-slides-and-assets)).

```bash
python scripts/renderers/welcome.py \
  content/confetti-cake-cottage/quest-01-bake-off-betrayal/welcome/welcome.json \
  --output exports/01-welcome.pdf
```

### Navigation links

`nav` rows name a stable resource ID from `catalog/resources.json`. A row shows **Open Guide** and becomes clickable only when that entry has an official HTTPS `published_url`; otherwise it shows **Coming Soon**. Never put Drive URLs in the document JSON.

### Fonts

The Canva originals (Better Faster, Glacial Indifference) are only partially embedded in the source PDF and Better Faster is commercial, so they cannot be reused. This template uses SIL OFL stand-ins: Lobster for headlines and Outfit for body text. Licences are in `assets/fonts/`.

### Status and builds

A document using this style is registered in `catalog/resources.json` with `"build": {"renderer": "welcome", "source": "<path to its JSON>"}`. That makes it a PR preview target named `<resource-id>.pdf`, rebuilt when its JSON, anything in its folder, these assets, or the renderer changes. The same build feeds **Publish to Drive** ([PUBLISH.md](system/PUBLISH.md)). Rendering does not publish anything.

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

### Verified existing Drive targets (metadata checked 2026-10-25)

| Lesson | Existing PDF file ID | Existing PPTX file ID | Documented review state |
| --- | --- | --- | --- |
| Activate | `1l_QwHQPRvKCL_n43xlvTyDHFxQy8poE_` | `1ShiqFB8Ac4QiVU3qUOXmQxu14s1UgCom` | The catalogue records the seven-slide deck as published; both Drive files exist. The linked PPTX contains the two video URLs according to the resource note. |
| Set the Table | `1r5w-EWU3N47iz5p02NSOsmN-P7Kv7QJt` | `1PQnFI3ryAvTj70NNKmlWqfbdkOcDUPkd` | Human-approved seven-slide PDF and linked PPTX, recorded as published on 2026-10-22. |
| Secret Ingredients | `1G5xRfBaqu3GSkgQf3XPozuI6I5CEE747` | `1ENvg9yCzZDE0ujRQ8aNosfz3afAKWffK` | Human-approved five-slide PDF and PPTX, recorded as published on 2026-10-25; presenter-mode hyperlinks were confirmed in the catalogue note. |

**Read-back scope:** On 2026-10-25, Drive returned each of these six exact IDs with the expected MIME type (`application/pdf` for PDFs; `application/vnd.openxmlformats-officedocument.presentationml.presentation` for PPTX). This metadata check does **not** independently reapprove artwork, slide content, presenter-mode links, external access, or PDF/PPTX content parity. Verify those afresh before every new publication. Preserve the file IDs, destination folders and sharing on replacements.

**Set the Table historical details (2026-10-22):** Human selected the seven-slide edition: slide 6 “Which Word Fits?” and slide 7 “Friendship Mystery #1”; the original six-page PDF's other pages stayed visually unchanged. The approved upload included two audio URL links on slide 4. Drive read-back sizes for the published PDF and PPTX are 11,933,343 and 5,034,225 bytes respectively. Unauthenticated viewer access has not been independently confirmed; do not change permissions without approval.

**Activate update:** An older note from 2026-10-22 said its PPTX destination was not located. That is superseded by the verified existing PPTX file ID above and the current resource catalogue. The Activate PDF remains the original published seven-slide asset; no new approval or upload is implied by locating the PPTX.

### Future editable slides

Editable slide-JSON generation remains **unimplemented** (see [SYS-002](SYSTEM_IMPROVEMENTS.md#sys-002--editable-lesson-slide-generation)). This utility only packages an approved PDF into a PowerPoint and restores PDF link annotations; it is not a slide editor, an automatic GitHub preview target, or an autonomous Drive publisher.

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

# File: `SYSTEM_IMPROVEMENTS.md`

## System improvements

This file tracks **active** work; repository instructions and publication authority live in [WORKFLOW.md](system/WORKFLOW.md) and [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Backlog entries never authorize publication.

### Implemented — two resource workflows (2026-10-25)

- Production-based registry: `generated_pdf` vs `external`, source provenance, explicit generated-PDF build mapping, holding vs official URLs and publication evidence.
- Verified Google Drive review holding root and four category folders; existing Slide PDFs review folder remains separate.
- Authorized generated-PDF PR merge Action supporting multiple explicitly approved resource IDs per release, with per-resource ownership checks, same-ID Drive replacement, MD5 and accepted revision verification, failure reporting and safe edit-branch cleanup.
- External resources stay agent-created and agent-published; no external `/merge` integration, external checksum automation or GitHub source-creation engine.
- Manual-only read-only publication inspector, with external content parity explicitly unverified.

**Operational prerequisites:** service-account access to specific official Drive targets; agent establishment of each generated PDF's first official destination. Existing legacy items with unknown history retain unverified evidence until independently checked. A passing CI check does not grant Drive access or publication authority.

### SYS-002 — Editable lesson slide generation

**Status:** Optional, not implemented.

Current slides remain separate human-reviewed lesson PDFs; `scripts/pdf_to_linked_slides.py` derives linked PPTX. Do not add speculative slide JSON, reuse the archived continuous 44-slide deck, or automatically publish external slides.

### SYS-003 — Teacher-owned presentation copies

**Status:** Proposed, not implemented.

Teachers may eventually receive independent copies of a lesson deck with hidden/skipped slides, preserving the reviewed master and its clickable links. Confirm the actual PowerPoint/Google Slides presentation behavior, permissions and copy workflow before implementation.

### SYS-004 — Verify teacher access to published Drive resources

**Status:** Low priority, proposed; not implemented.

Add a **read-only** audit for Google Drive resources marked `published`, starting with those linked by current Teacher Guides. Verify the exact official file ID, intended reader permissions (including inherited access where applicable), and, when practical, actual access as a teacher without publisher credentials. Report `accessible`, `access problem`, or `unable to verify` with the affected resource ID; never mistake authenticated owner access or recorded publication status for teacher access. Do not automatically change permissions or publish resources. Run on demand or periodically rather than on every content edit; keep the existing manual publication-access checks until the audit exists.

### SYS-005 — Colour and printer-friendly worksheet versions in the Print Pack Builder

**Status:** Proposed, not implemented.

Some worksheets may need a colour version and a separate printer-friendly version (for example, an ink-saving layout without dark backgrounds). The Teacher Guide should keep one link per worksheet rather than separate "colour" and "black and white" links, likely pointing to a Drive folder that holds both versions. The [Print Pack Builder](apps/AGENTS.md) then needs to look one level deeper: offer a Colour / Printer-friendly choice and fetch the matching file. Decide how the two files are recorded in `catalog/resources.json` before implementing. Plain black-and-white printing of a colour PDF needs nothing: teachers choose it in the print window.

### SYS-006 — Google Form–triggered teacher resource sharing

**Status:** Proposed, not implemented.

Explore a teacher registration/request workflow using **Google Forms + Google Apps Script + Google Drive**. On form submission, capture the teacher's email and requested resource(s), check eligibility or approval where needed, grant access only to the specific approved Drive files/folders, and email the appropriate links. A Google Sheet may track submissions, access decisions, and sharing actions.

Before implementation, decide whether access is immediate or manually approved, how purchases/teacher eligibility are verified (form submission alone is not verification), what access scope and expiration/revocation rules apply, and how to avoid exposing paid or unpublished materials. Respect the existing holding-versus-official publication boundary; **never let a form submission publish resources or bypass review**. Confirm Apps Script trigger ownership, Google Workspace sharing restrictions, duplicate submissions, failures, and the audit trail before enabling automated permission changes.

### SYS-007 — Print Pack Builder settings page for default group size

**Status:** Proposed, not implemented.

The [Print Pack Builder](apps/AGENTS.md) prefills each group activity's **Groups** field with students ÷ 4, rounded up. Add a small settings page where a teacher sets their own default students per group, saved in the browser like the class size. Keep the per-activity Groups field as the override; do not reintroduce a group-size field on the lesson page.

### Previously implemented

- Targeted PDF validations and durable preview history: [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup).
- Human-reviewed slide PDF to linked PPTX conversion: [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- Historical backlog: [archive/2026-10/](archive/2026-10/README.md).

---

# File: `content/AGENTS.md`

## Editing teaching content

Every source file in this folder opens with a `$instructions` key (stories: an `instructions:` frontmatter line) naming the guides to read before editing it. `scripts/validate.py` requires it, and the templates carry it, so new files get it too.

| Editing | Read first |
| --- | --- |
| `<school>/<quest>/quest.json` | [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states). It owns lesson delivery status; branch-only edits do not change it. |
| `lessons/<stage>/lesson.json` | [EDITORIAL_GUIDE.md](system/EDITORIAL_GUIDE.md), then [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) |
| `lessons/<stage>/stage.json` | Provenance only. To convert a lesson, start from [templates/teacher_guide/TEMPLATE.json](templates/teacher_guide/TEMPLATE.json). |
| `resources/teacher_companion/*.json` | [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md) |
| `story/*.md` | [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md); approved text only, wording preserved |
| `welcome/` (registry-built documents) | [templates/welcome/README.md](templates/welcome/README.md) |
| Lesson slides (Drive PDFs, not stored here) | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |
| Covers, icons, artwork | [Asset rules](system/CONTENT_CONTRACT.md#resources-slides-and-assets): separate image files, covers as cut `cover.pdf` |

Linked resource names, URLs and companion publication evidence live in [catalog/resources.json](catalog/AGENTS.md); resource status is derived rather than stored.

**Student worksheets print from the guide.** The [Print Pack Builder](apps/AGENTS.md) reads each `lesson.json`: a `student_worksheet` under `GIVE` is printed for everyone, under `MORE` it is an optional checkbox, and inside `step.options` it follows the A/B/C choice. Adding a worksheet to a guide, and publishing it in the catalogue, makes it printable with no other step. Keep each worksheet's description stating its copies (`One per student`, `One per group of 3–4`).

After editing, run `python scripts/validate.py` and save through a PR per [WORKFLOW.md](system/WORKFLOW.md).

---

# File: `catalog/AGENTS.md`

## Editing the catalogue

- `resources.json` owns stable linked-resource IDs, production type, provenance, holding and official URLs, build mapping, publication evidence (resource status is derived, never stored). See [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#production-workflows-and-delivery-states).
- Use `generated_pdf` only for existing Python-rendered PDF outputs with GitHub editable sources and explicit `build`. Externally authored PDFs remain `external`, as do slides and image-based resources.
- `drive_folders.json` owns four holding category folder IDs mirroring the official Drive layout; existing nested subfolders retain their IDs. Legacy Slide PDF originals remain separate. Never invent file or folder IDs. A holding file is not published **even when its permanent URL will be unchanged**.
- [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) owns status definitions; **[PUBLISH.md](system/PUBLISH.md) alone owns the actions and verification that permit recording an official `published_url`**. Legacy records can remain explicitly unverified. Add `human_review: {"<exact URL>": "pending"}` for reviewable links; set to `reviewed` only after a human checks that URL. For externally owned Drive files, add `review_mode: "human"`; ordinary Drive links always retain automatic public-permission checks.
- Published resources always render their `published_url`, in both review and release PDFs. Any external resource (including slides) may have a **distinct** staged holding link indicating `pending_publish`; a link to the same Drive file ID is not pending. The link inspector skips slide decks. Draft previews may use holding links; release builds require every referenced resource to have an official URL. Generated PDFs use approved/current MD5 parity, not holding links.
- `quests.json` indexes quest manifests; each quest's `quest.json` owns lesson-source delivery status, separate from linked resource status.

Follow [CREATE.md](system/CREATE.md) for new drafts, [UPDATE.md](system/UPDATE.md) for revisions, and [PUBLISH.md](system/PUBLISH.md) for release; [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) owns slide-specific conversion. Run `python scripts/validate.py` after changes.

---

# File: `templates/AGENTS.md`

## Editing templates

Templates are starting structures for supported source types: `teacher_guide/` (lesson.json), `teacher_companion/`, and the `welcome/` page style with its assets. `fonts/` holds the bundled Lato (OFL) used by the Teacher Guide and companion renderers; it is the same Lato 2.015 CI used before it was bundled. Add a template only for a source type with a working authoring workflow.

- **Build templates from individual assets.** Logos, crests, icons, and illustrations go in the template's `assets/` folder as separate image files that the renderer places around live text. Never generate or rasterize a whole page as one image. Full rule: [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md#resources-slides-and-assets).
- Each `TEMPLATE.json` opens with the same `$instructions` pointer its sources need, so copies inherit it. `scripts/validate.py` checks this.
- Renderers live in `scripts/renderers/`, not here ([scripts/AGENTS.md](scripts/AGENTS.md)).

---

# File: `scripts/AGENTS.md`

## Editing tooling

| File | Purpose | Read first |
| --- | --- | --- |
| `renderers/teacher_guide.py` | Teacher Guide PDF layout | [EDITORIAL_GUIDE.md §7](system/EDITORIAL_GUIDE.md#7-generator-engineering-boundaries) |
| `renderers/teacher_companion.py` | Companion PDF layout | [RESOURCE_GUIDELINES.md](system/RESOURCE_GUIDELINES.md#presentation) |
| `renderers/welcome.py` | Welcome page style | [templates/welcome/README.md](templates/welcome/README.md) |
| `select_builds.py`, `build_selected.py` | Explicit generated-PDF output mappings and previews | [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup) |
| `validate.py` | Objective source/registry checks and instructions freshness | [AI_RULES.md](system/AI_RULES.md#maintaining-instructions) |
| `build_agents_md.py` | Regenerate root `AGENTS.md` | Run after any instruction edit |
| `publication_state.py` | One derived publication-state rule for all resources | [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) |
| `publish_to_drive.py` | Generated-PDF in-place Drive replacement/checksum | [PUBLISH.md](system/PUBLISH.md) |
| `release_on_merge.py` | Single authorized generated-PDF merge selection and release | [PUBLISH.md](system/PUBLISH.md) |
| `inspect_publications.py` | Read-only Drive permission / exact-URL human-review audit of published resources | [PUBLISH.md](system/PUBLISH.md#on-demand-inspection) |
| `pdf_to_linked_slides.py` | Human-reviewed slide PDF to linked PPTX | [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md) |

PDF previews and releases use official `published_url` whenever present, and draft previews use holding links otherwise. `publication_checks.py` rejects release dependencies without an official URL; `publication_state.py` derives resource status from distinct external holding URLs or generated-PDF MD5 parity. Only Python-generated PDFs enter the build-and-publish pipeline. External resources have no automatic GitHub merge publisher or source-generation engine; agents handle Drive holding and official publication directly.

When changing renderer inputs or build selection, update `select_builds.py` and relevant tests. Run `python scripts/validate.py` and `python -m unittest discover -s tests` after edits.

---

# File: `apps/AGENTS.md`

## Editing apps

`apps/` holds standalone teacher-facing web apps. They are separate from the Python Teacher Guide pipeline: they read repository records but never edit lesson sources, set publication status, or publish to Drive.

| App | Purpose | Read first |
| --- | --- | --- |
| `print-pack-builder/` | Teachers pick lesson activities and class numbers and download one combined student-worksheet PDF | [print-pack-builder/README.md](apps/print-pack-builder/README.md) |

- **No separate print configuration.** The Print Pack Builder reads every `lesson.json` and `catalog/resources.json` at build time ([how guides map to the builder](apps/print-pack-builder/README.md#where-lessons-come-from)): `GIVE` worksheets are included, `MORE` worksheets are checkboxes, `step.options` are pick-one choices, and only `type: student_worksheet` links count. A worksheet becomes downloadable when its catalogue entry has a valid official `published_url`. Never add per-lesson lists, allowlists or Drive IDs to the app.
- **Editing a guide edits the builder.** When you add, move or remove a student worksheet in a `lesson.json`, the builder changes with it; describe its copies in the guide ("One per student", "One per group of 3–4"). For cards printed several to a page, add `"print": {"cards_per_sheet": N}` to the catalogue entry, counted from the actual PDF.
- The site runs without a login (`REQUIRE_ACCESS: "false"`), which is only acceptable because published student worksheets are shared publicly on Drive. Require the login before publishing a worksheet that must stay private.
- Do not commit real worksheets, credentials or `.dev.vars`; demo files are synthetic (`npm run fixtures`).
- Use a dedicated non-lesson branch for app work. After editing, run `npm run check` in the app folder; CI runs the same in `.github/workflows/print-pack-builder.yml`.

---

# File: `system/AGENTS.md`

## Editing instructions

The files here own the repository's rules; each states what it owns in its opening lines, and [START_HERE.md](START_HERE.md#where-things-belong) maps every rule to its owner. Follow [AI_RULES.md: maintaining instructions](system/AI_RULES.md#maintaining-instructions): change a rule only in its owner, replace superseded wording, and link instead of copying.

After editing any instruction file, run `python scripts/build_agents_md.py` to regenerate the root `AGENTS.md`; `scripts/validate.py` fails while it is stale. Never edit the root `AGENTS.md` itself. `action_labels.json` is data read by the validator.
