# Publishing resources to Google Drive

**Single authoritative publication procedure** for Python-generated PDFs and externally authored resources. Creating belongs to [CREATE.md](CREATE.md), revising to [UPDATE.md](UPDATE.md), shared review checks to [WORKFLOW.md](WORKFLOW.md), and field and derived-status definitions to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). Creating, revising, ordinary PR merges and previewing do not publish.

## Publication prerequisites and release gate

1. Confirm explicit human authorization for the **exact reviewed resource/version**, its stable ID, production type, current publication record and official Drive destination. A holding upload or passing check does not imply approval.
2. Prefer **moving the same holding file** to its official folder to preserve Drive file ID and URL. Verify that the ID remains unchanged; if copying creates a new ID, register the verified new ID and update references. Do not confuse a valid link with publication; **folder placement and successful verification authorize recording an official link**. Never guess IDs or folders.
3. **Automated pre-publication gate:** Before replacing a generated Teacher Guide, companion or Welcome PDF, require an official `published_url` for every referenced registry resource, then live-inspect those published links **and** the existing target Drive URL. Both `FAIL` and `NEEDS REVIEW` block the upload, including in dry runs. This is enforced inside the shared publisher used by the guarded merge release and Internal Drive replacement. For external resources, an agent must perform the equivalent check before delivery; no external-resource release automation exists. A resource's original Drive URL may stay identical when moved from holding to official—the gate checks the official URL, not a stored status.
4. Verify official file identity, MIME, parent folder and sharing/access as far as the tools allow. User testing in incognito is useful but not a substitute for accurate agent records; do not claim incognito testing the agent cannot perform.
5. **Only after successful official Drive verification**, update `published_url` in `catalog/resources.json`; generated PDFs also retain their verified `pdf.approved_md5` and `pdf.revision`. When moving the same file, the permanent URL is unchanged. Clear `holding_url` when an external replacement goes live; a different holding link is the pending-update signal for all non-generated resources, including slides. Slide PDF source files stay in `pdf_url`, not `holding_url`. Published resources always link through `published_url`, including in preview PDFs. Never manufacture a different link. Neither a URL nor metadata access alone proves anonymous access.

## External resources — agent-managed publication

Worksheets, posters, externally produced PDFs, media and slides omit `pdf` and are not published by the generated-PDF release mechanism or Python PDF builds.

1. Move the exact reviewed file to the verified teacher-facing folder, preserving its ID where possible. For a previously published asset, replace the official file **in place** rather than creating duplicates.
2. Read back the official file ID, MIME, folder and access metadata. For slides, [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md) adds mandatory PDF/PPTX pairing, conversion and verification; both must be checked.
3. After successful verification, commit the catalogue's verified official `published_url` (and clear `holding_url` for the released version). Keep verification evidence in the publication workflow report rather than duplicating a history record in every resource.
4. On failure, report the precise blocker. An unapproved new file has no official URL. For a revised external file, preserve the official URL and stage the new version under a different `holding_url`; derived state becomes `pending_publish`. Never invent checksums or assert external content parity without evidence. Prefer automated Drive metadata checks; reserve human incognito testing for access behavior tools cannot prove.

## First-time generated PDF publication — agent-managed
### Student worksheet PDF check before external publication

For any `student_material` PDF, run `python scripts/pdf_page_size.py path/to/worksheet.pdf` **before uploading or replacing the official Drive file**. Every page must be US Letter (8.5 × 11 inches), portrait or landscape. This check is for student-facing worksheets **only**; do not change Teacher Guide, companion or slide page sizes. External resources are still published by an agent rather than the generated-PDF publisher.


Move the exact approved generated PDF from holding to the verified official teacher-facing folder (or create a verified official copy if necessary). Read back its ID, MIME, access, and exact file version. Only then register the official URL, ID and publication evidence; the resource state derives automatically. This establishes the official file for subsequent in-place automated updates; the automated replacement workflow does **not** create first-time destinations.

## Authorized release PR for an established generated PDF

1. The agent confirms the exact reviewed PDF and human approval, reconciles the **shared `lesson/<quest-id>-<stage>` branch** (legacy `edit/<resource-id>` accepted) with latest `main`, and adds `.github/resource-releases/<PR-number>.json` listing only the explicitly authorized resource IDs. Each listed resource must belong to that branch and independently pass publication checks; other lesson resources on the branch do not automatically publish.
2. The agent merges that resource PR into `main`; **only** the merged generated-PDF resource PR with its explicit marker triggers `.github/workflows/release-on-merge.yml`. Ordinary pushes and other PRs never publish.
3. The workflow checks the accepted source and resource mapping, runs shared validation/tests and builds using `scripts/build_selected.py`. If a newer `main` update superseded the accepted PDF, publishing is blocked.
4. An already-established official `published_url` must identify an editable Drive PDF. The publisher replaces the **same file ID** in place, preserves its name, folder and sharing, then reads back the file's ID and MD5.
5. Only after exact verification does GitHub write `pdf.approved_md5` and `pdf.revision`; the Drive version/time remain in the workflow report. Before upload, a changed GitHub-generated PDF derives as `pending_publish` when its checksum differs; after verified replacement it derives as `published`. On failure, leave the old approved checksum intact and report a blocker. No unverifiable digest or reported upload success can mark `published`.
6. The release Action provides its report and matching post-merge `main` PDF preview. **Keep the shared lesson branch** for subsequent work. Legacy per-resource `edit/` branches may be cleaned up only after verified release and only if they have not advanced; preserve concurrent additions.

## Manual fallback and review copies

**Actions → Internal Drive replacement** is a controlled fallback for `generated_pdf` resources with verified existing official destinations. Use dry run first and the same read-back verification. It is not an external-resource publisher or a user-facing publishing command.

For draft creation, stage a Teacher Guide PDF under the configured `01_TEACHER_GUIDES` holding folder, or a generated companion under `04_TEACHER_RESOURCES`; use the verified folder IDs in `catalog/drive_folders.json`. This is never publication. `holding_url` is a draft pointer, `published_url` the official pointer. The holder may be the same original file before initial release; never treat it as a second version by string inequality alone. Do not change an established Drive ID for housekeeping. Draft procedure: [CREATE.md](CREATE.md).

The publisher resolves only recorded official targets. Generated PDF metadata examples: `{"pdf":{"renderer":"welcome","source":"content/.../welcome.json"}}` or `{"pdf":{"renderer":"teacher_guide","output":"00-activate-teacher-guide.pdf"}}`. `scripts/select_builds.py` resolves these. A non-generated resource has no `pdf` object.

## Pre-publication dependency inspection

Both generated-PDF release paths run the existing publication inspector **before** modifying Drive. The publisher scopes inspection to the PDF's referenced registry resources (including Welcome navigation) and its own established target URL; it does not scan the whole registry. It requires `PASS` for every item: a Drive resource must exist, be accessible to the service account, not be in Trash and have public anyone-with-the-link permissions. Generated-PDF **dependencies** must match their recorded `pdf.approved_md5`; non-Drive destinations require exact `human_reviewed_url` approval. `FAIL` **and** `NEEDS REVIEW` are release blockers. The target PDF's *old* approved MD5 is not used in the pre-upload inspection because it is about to be replaced; public access and destination editability are checked, and its exact new bytes/file ID are verified by Drive read-back after upload. **Neither release workflow performs a second post-publication inspection.**

**Actions → Inspect published resources** remains a separate manually triggered full/targeted, read-only audit. It checks all published resources (or one specified resource), including slides and pending replacements; only confirmed `FAIL` makes that standalone workflow red, while `NEEDS REVIEW` stays advisory. See [INSPECTION.md](INSPECTION.md). The inspector never verifies embedded PDF hyperlinks, live non-Drive site responses, ownership, folder placement or source content parity.

At an **initial generated-PDF publication**, establish `pdf.approved_md5` and `pdf.revision` only from verified uploaded bytes. The in-place generated-PDF publisher records a missing baseline automatically after successful Drive read-back. For historical links lacking a verified baseline, never invent one; inspection reports NEEDS REVIEW until properly checked.

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.
