# Publishing resources to Google Drive

This is the official delivery guide. [EDIT.md](EDIT.md) owns editing, and [WORKFLOW.md](WORKFLOW.md) owns GitHub PDF previews and tests. **For generated PDFs, the GitHub preview is the review copy; Drive holding is not required.**

## First-time generated PDF (Teacher Guide or companion)

1. **Create and review in GitHub.** Start with the appropriate source template, save the editable JSON and iterate through GitHub Actions PDF previews until the version is explicitly approved. The existing system already creates **new** PDFs through these renderers.
2. **Accept the source.** Merge the approved PR into `main`. Use the final PDF rendered from that accepted source, resolving official links that must be clickable. For a Teacher Guide, publish needed student printouts and companion resources first; this is a simple content-link check, not a separate Drive-release ceremony.
3. **Upload directly to the official Drive folder.** Use a capable connected Drive upload bot, or have the person upload the PDF manually. A Teacher Guide belongs under `01_TEACHER_GUIDES`, a companion under `04_TEACHER_RESOURCES`, inside the permitted project root. **No generated-PDF holding upload or subsequent folder move.** The current automated generated-PDF publisher cannot create a first-time official file ID; the connected Drive upload action can create a file, subject to its byte-transfer limitations.
4. **Record the official link.** Once the new file ID/URL is observed, set `published_url` to that actual URL and `holding_url: null` in `catalog/resources.json`. Record the generated PDF's local MD5 and accepted GitHub revision in the handoff as the *source baseline*.
5. **Inspect after uploading.** Run **Actions → Inspect** for the resource. It checks public access and checksum evidence. Record `pdf.approved_md5` and `pdf.revision` only if the official Drive file's bytes are verified to match the accepted generated PDF. If an upload tool added PDF metadata, keep the official URL, omit unverifiable checksum fields and report `NEEDS REVIEW`; do not claim byte parity or require an unnecessary second upload for content reasons.

**Default:** one human approval, direct upload, record the link, one post-upload inspection. Do not make the person perform a staging upload, move, first-time release marker or repeated upfront permission checks.

## Updating an existing generated PDF

1. Edit the same GitHub JSON source and review a fresh Actions PDF preview. Keep the existing official Drive file untouched while iterating; no holding copy is required.
2. After approval and merge, upload the accepted PDF as a **new version of the same official Drive file** (manually through Drive's Manage versions, or using an authorized in-place upload). Preserve its file ID, URL and sharing.
3. Run inspection and update the accepted checksum/revision only after confirmed byte parity. Report discrepancies instead of silently claiming an exact match.

**Optional automated replacement:** The existing `.github/workflows/release-on-merge.yml` still supports established official generated PDFs. To invoke it, add `.github/resource-releases/<PR-number>.json` listing approved IDs before merging the resource PR. That Action performs stricter pre-upload dependency/access checks, replaces the same Drive ID, verifies MD5 and records revision. Ordinary merges do not publish. **Actions → Publish Directly** is an internal dry-run/replacement fallback for already-established Drive files; neither Action creates the first official destination.

## Externally authored resources

Worksheets, slides, posters and other PDFs without a catalogue `pdf` renderer are edited in their original authoring tools. Holding is useful for these **unapproved or in-progress external revisions**, particularly student worksheets. Approved new external files may also go directly into their official folders. Validate that every student-material PDF page is US Letter before upload; slides additionally follow [SLIDE_CONVERSION.md](SLIDE_CONVERSION.md). Preserve existing Drive file IDs for updates. After an official upload or move, record the observed `published_url`, clear the released `holding_url` and inspect access. The generated-PDF publisher does not handle external resources.

## Inspection and evidence

- `published_url` is the verified destination link, **not** a claim of source/Drive byte identity.
- The locally generated MD5 is a useful source baseline. Only write `pdf.approved_md5` and `pdf.revision` after exact official-Drive read-back/parity. Missing evidence is an open inspection item, not permission to fabricate a checksum.
- **Actions → Inspect** is read-only. It checks Drive access, sharing and recorded generated-PDF checksum. It reports `NEEDS REVIEW` for missing approved checksum and `FAIL` for mismatches. The inspection does **not** check layout, embedded PDF links or folder placement; review these while approving the PDF or at the final upload. See [INSPECTION.md](INSPECTION.md).
- Human approval is always explicit. Do not invent file IDs, verify an unperformed transfer, or conflate a successful upload with exact byte parity.

## One-time setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project (for example `little-chewz-publish`).
2. **APIs & Services → Library**: enable **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (for example `drive-publisher`). Skip the optional role and access steps.
4. Open the service account → **Keys → Add key → Create new key → JSON**. A key file downloads. Treat it like a password.
5. In Drive, share each target file or its folder with the service account's email (`…@…iam.gserviceaccount.com`) as **Editor**, with notifications off.
6. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `GOOGLE_SERVICE_ACCOUNT_JSON`, value: the entire contents of the key file. Then delete the downloaded key file.

The service account can only see files explicitly shared with it. Remove its access in Drive, or delete the key in Cloud Console, to revoke publishing.
