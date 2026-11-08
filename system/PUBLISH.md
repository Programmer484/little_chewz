# Publish — on merge or by explicit request

**Merging a PR into `main` publishes it**: every already-live generated PDF the merge affects is republished automatically, so merge only what the human has approved in the preview. Put `[no publish]` in the PR title to merge without publishing. Otherwise an agent publishes only resource IDs the human names (in chat or **Actions → Publish**). Nothing publishes on a schedule or from catalogue detection, and files with no live Drive destination are never published automatically.

## Generated PDFs (Teacher Guides, companions, Welcome, Celebrate)

**The GitHub Actions preview is the review copy; a Drive Holding copy is optional.** Live files update in one of two ways:

- **Publish on merge (automatic).** When a PR merges into `main`, the **Publish** Action builds from the merge commit, finds every generated PDF the merge may affect (`scripts/select_builds.py` against the commit before the merge) that already has a `published_url`, and replaces those files: companions first, then guides, then the Welcome. Files whose bytes are already identical on Drive are left alone. Before merging, check the preview of every live PDF the PR changes; if something is not ready to go live, keep it unmerged or title the PR `[no publish]`.
- **Publish directly.** **Actions → Publish → Run workflow** on `main` with named IDs; dry run first (the default), then a real run. Use it after a `[no publish]` merge or to retry. An agent may instead run `python scripts/publish_to_drive.py <ids>` where `GOOGLE_SERVICE_ACCOUNT_JSON` is available.

Both paths use `scripts/publish_to_drive.py`. It handles only **established** destinations (an existing `published_url`): builds with published links only, rejects unpublished dependencies, replaces the Drive file in place (same ID, link, folder and sharing; Drive keeps the old version), verifies the MD5 read-back, then records `pdf.approved_md5` and `pdf.revision`. IDs publish in the order given and **stop at the first failure**. A first-time official file still needs the Drive file created first ([Create](CREATE.md)), then the move or upload below.

## Safe publication order

1. Read each requested catalogue entry; for Drive-managed files inspect actual Drive metadata, and for externally hosted URLs verify their exact approved destination. Match ID, MIME type and folder. If the approved candidate's bytes/version changed after approval, stop.
2. Reject missing and **unpublished dependencies**. A resource can become public only when every referenced dependency already has `published_url`, or is **named earlier in the same approved batch and successfully published first**. Resolve generated-PDF source refs and any declared catalogue `dependencies`. Reject cycles. Official PDFs must never embed Holding-only links.
3. For generated PDFs, publish only from accepted `main`, rendering with published destinations. GitHub preview links are review copies, never official links.

## First publication of a Drive-managed file

**Move** the exact existing Holding Drive file to the correct Public folder; never copy or reupload it as a new ID. Re-read its ID, destination folder, MIME and sharing. A folder move preserves the file ID/link but does **not** prove anonymous access; confirm public sharing. After success, put the **same URL** into `published_url` and clear `holding_url`. For generated PDFs, record approved MD5 and revision only after published-byte parity is verified.

**Externally hosted URLs** (YouTube, web apps) have no Drive move. The human approves the exact URL and content; the agent records that URL as `published_url` and `human_reviewed_url` only when explicitly told to publish its resource ID. No fake Holding file is created.

## Updating an existing publication

Preserve the established Public Drive ID and URL and **replace the existing public file's content/version in place**. Generated PDFs use the paths above, with no Holding copy required. For other files (worksheets, slides, artwork), a separate Holding copy remains the usual approved candidate: replace the public file in place from it; do not move the Holding copy into Public or change the public link. Verify the resulting live ID, bytes/version, folder and sharing before clearing Holding. Native Google files require native-compatible replacement; slide PDF/PPTX pairs must be checked together.

## Failures and audit

Report every requested ID, destination and outcome. Stop dependent publications after any failure. A Drive mutation may succeed before the catalogue commit; retries must read actual live state and reconcile safely, never create duplicates. Do not mark partially successful batches complete.

**Actions → Inspect** remains a manually triggered, read-only audit of **published resources only**. It is not a release gate or a separate scheduled auditor. It reports missing/private resources, checksum drift, and **FAIL for published parents referencing unpublished dependencies**. It cannot determine whether a linked PDF/video is the *intended* content, so human review remains essential. See [Inspection](INSPECTION.md).
