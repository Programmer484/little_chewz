# Publishing resources to Google Drive

**Single authoritative publication procedure** for Python-generated PDFs and externally authored resources. Creating belongs to [CREATE.md](CREATE.md), revising to [UPDATE.md](UPDATE.md), shared review checks to [WORKFLOW.md](WORKFLOW.md), and field/status definitions to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). Creating, revising, ordinary PR merges and previewing do not publish.

## Publication prerequisites and release gate

1. Confirm explicit human authorization for the **exact reviewed resource/version**, its stable ID, production type, current publication record and official Drive destination. A holding upload or passing check does not imply approval.
2. Prefer **moving the same holding file** to its official folder to preserve Drive file ID and URL. Verify that the ID remains unchanged; if copying creates a new ID, register the verified new ID and update references. Never guess IDs or folder destinations.
3. Before releasing a **Teacher Guide**, review every referenced resource. A released guide must not depend on holding-folder-only links, missing or unverified official URLs, or `unpublished`/`pending_publish` dependencies. Review PDFs are not official releases. **This is an agent check, not a claim that a cross-resource automated release gate exists.**
4. Verify official file identity, MIME, parent folder and sharing/access as far as the tools allow. User testing in incognito is useful but not a substitute for accurate agent records; do not claim incognito testing the agent cannot perform.
5. **Only after successful official Drive verification**, update `published_url`, compatibility `url`, publication evidence and `status: published` in `catalog/resources.json`. A review `holding_url` remains distinct; neither a valid URL nor metadata access proves anonymous access.

## External resources — agent-managed publication

Worksheets, posters, external PDFs, media and slides use `production_type: external` and are not published through authorized generated-PDF release or Python PDF builds.

1. Move the exact reviewed file to the verified teacher-facing folder, preserving its ID where possible. For a previously published asset, replace the official file **in place** rather than creating duplicates.
2. Read back the official file ID, MIME, folder and access metadata. For slides, [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md) adds mandatory PDF/PPTX pairing, conversion and verification; both must be checked.
3. After successful verification, commit the catalogue record: `published_url`, compatibility `url`, `status: published`, and honest `publication` confirmation (file ID and verification method/time). Retain holding history only where appropriate.
4. On failure, report the precise blocker. A new file stays `unpublished`; where an older verified release exists but a revision has not been verified, preserve the live record and use `pending_publish` as defined in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). Never invent checksums or assert external content parity without evidence.

## First-time generated PDF publication — agent-managed

Move the exact approved generated PDF from holding to the verified official teacher-facing folder (or create a verified official copy if necessary). Read back its ID, MIME, access, and exact file version. Only then register the official URL, ID, publication evidence and `published` status. This establishes the official file for subsequent in-place automated updates; the automated replacement workflow does **not** create first-time destinations.

## Authorized release PR for an established generated PDF

1. The agent confirms the exact reviewed PDF and human approval, reconciles the `edit/<stable-resource-id>` branch with latest `main`, and adds `.github/resource-releases/<PR-number>.json` with the authorized single matching resource ID.
2. The agent merges that resource PR into `main`; **only** the merged generated-PDF resource PR with its explicit marker triggers `.github/workflows/release-on-merge.yml`. Ordinary pushes and other PRs never publish.
3. The workflow checks the accepted source and resource mapping, runs shared validation/tests and builds using `scripts/build_selected.py`. If a newer `main` update superseded the accepted PDF, publishing is blocked.
4. An already-established official `published_url` must identify an editable Drive PDF. The publisher replaces the **same file ID** in place, preserves its name, folder and sharing, then reads back the file's ID and MD5.
5. Only after exact verification does GitHub record the checksum, accepted Git revision, Drive version/time and `published`. If a live older release exists but the update fails, record `pending_publish` and a clear blocker. No unverifiable digest or reported upload success can mark `published`.
6. The release Action provides its report and the matching post-merge `main` PDF preview run. The former edit branch is removed only when publication succeeded and its remote head still matches the merged PR; concurrent additions are preserved.

## Manual fallback and review copies

**Actions → Internal Drive replacement** is a controlled fallback for `generated_pdf` resources with verified existing official destinations. Use dry run first and the same read-back verification. It is not an external-resource publisher or public publishing slash command command.

For draft creation, upload the review PDF to the verified PDF-generated holding folder from `catalog/drive_folders.json`; this is never release. `holding_url`, `published_url`, and compatibility `url` must remain distinct. Do not change an established Drive ID for housekeeping. Draft procedure: [CREATE.md](CREATE.md).

The publisher resolves only recorded official targets. Registry build examples: `{"build":{"renderer":"claude","source":"content/.../welcome.json"}}` or `{"build":{"output":"00-activate-teacher-guide.pdf"}}`. `scripts/select_builds.py` resolves these. No external resource receives a Python build just because it is a PDF.

## On-demand inspection

**Actions → Inspect publication** is manual and read-only. It can compare a generated PDF's recorded checksum and Drive metadata or report evidence for an external file, but cannot prove external content parity. It does not publish files or change status.

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.
