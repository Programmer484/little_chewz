# Publishing generated PDFs to Google Drive

This is the **Python-generated PDF** automation boundary. External worksheets, posters, image-generated PDFs, media and slide PDF/PPTX pairs are published manually by an agent according to [CREATE.md](CREATE.md) and [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). `/create` and `/update` are agent instructions, not Python command programs.

## Generated PDF publication after an authorized /merge

1. The agent confirms the exact reviewed PDF and human approval, reconciles the `edit/<stable-resource-id>` branch with latest `main`, and adds `.github/resource-releases/<PR-number>.json` with the authorized single matching resource ID.
2. The agent merges that resource PR into `main`; **only** the merged generated-PDF resource PR with its explicit marker triggers `.github/workflows/release-on-merge.yml`. Ordinary pushes and other PRs never publish.
3. The workflow checks the accepted source and resource mapping, runs shared validation/tests and builds using `scripts/build_selected.py`. If a newer `main` update superseded the accepted PDF, publishing is blocked.
4. An already-established official `published_url` must identify an editable Drive PDF. The publisher replaces the **same file ID** in place, preserves its name, folder and sharing, then reads back the file's ID and MD5.
5. Only after exact verification does GitHub record the checksum, accepted Git revision, Drive version/time and `published`. If a live older release exists but the update fails, record `pending_publish` and a clear blocker. No unverifiable digest or reported upload success can mark `published`.
6. The release Action provides its report and the matching post-merge `main` PDF preview run. The former edit branch is removed only when publication succeeded and its remote head still matches the merged PR; concurrent additions are preserved.

First-time official publication is **agent-managed**: the agent moves/copies the accepted generated PDF from holding to the proper teacher-facing Drive folder, verifies the file, and registers its `published_url`, actual ID and first publication confirmation. No automated new-file creation is attempted. Subsequent accepted revisions use the automatic in-place path.

## Manual fallback and review copies

The existing **Actions → Internal Drive replacement** workflow remains a controlled manual fallback for registered `generated_pdf` resources with established destinations. Use dry run first. Its status/version updates use the same verifier. It is **not** a user-facing `/publish` command or an external-resource publisher.

For `/create`, an agent builds the PDF preview and uploads it to the verified `PDF-generated resources` holding folder in `catalog/drive_folders.json`. This holding copy is never an official release. `holding_url`, `published_url`, and the compatibility `url` must remain distinct, and existing Drive IDs must not be changed merely for housekeeping.

The publisher's destination is resolved only from the resource's recorded official file. Example generated registry build mapping: `{"build":{"renderer":"claude","source":"content/.../welcome.json"}}`; ordinary Teacher Guides use `{"build":{"output":"00-activate-teacher-guide.pdf"}}`. `scripts/select_builds.py` resolves these output names. No external asset receives a Python build just because it is a PDF.

## On-demand inspection

**Actions → Inspect publication** is manual-only and read-only. For generated PDFs it can compare current rendered checksum, recorded published checksum and Drive metadata. For external resources it can confirm Drive metadata or report the missing evidence but **cannot infer content parity**. The inspector never changes status or republishes files.

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.
