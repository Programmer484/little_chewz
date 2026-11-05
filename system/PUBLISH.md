# Publish — explicit, human-directed delivery only

**No publishing on merge, schedule, catalogue detection or checksum differences.** An agent publishes **only specific resource IDs named by the human**, after they approve the exact final Holding artifact.

## Safe publication order

1. Read each requested catalogue entry and actual Holding/Public Drive metadata. Match ID, MIME type, verified folder, expected version/MD5 (where available), and the human-approved candidate. If its bytes/version changed after approval, stop.
2. Reject missing and **unpublished dependencies**. A resource can become public only when every referenced dependency already has `published_url`, or is **explicitly named in the same approved batch and successfully published first**. Resolve generated-PDF source refs and any declared catalogue `dependencies`. Reject cycles. Official PDFs must never embed Holding-only links.
3. For generated PDFs, ensure the intended GitHub revision is accepted and render release output using published destinations. Do not assume GitHub preview links are official.

## First publication

**Move** the exact existing Holding Drive file to the correct Public folder; never copy or reupload it as a new ID. Re-read its ID, destination folder, MIME and sharing. A folder move preserves the file ID/link but does **not** prove anonymous access; confirm public sharing. After success, put the **same URL** into `published_url` and clear `holding_url`. For generated PDFs, record approved MD5 and revision only after published-byte parity is verified.

## Updating an existing publication

Preserve the established Public Drive ID and URL. The separate Holding file is the approved candidate; **replace the existing public file's content/version in place**. Do not move the Holding copy into Public or change the public link. Verify the resulting live ID, bytes/version, folder and sharing before clearing Holding. Native Google files require native-compatible replacement; slide PDF/PPTX pairs must be checked together. `scripts/publish_to_drive.py` is an optional agent-invoked helper for **explicitly directed**, established generated-PDF destinations; it rejects unpublished dependencies and verifies the exact accepted PDF bytes.

## Failures and audit

Report every requested ID, destination and outcome. Stop dependent publications after any failure. A Drive mutation may succeed before the catalogue commit; retries must read actual live state and reconcile safely, never create duplicates. Do not mark partially successful batches complete.

**Actions → Inspect** remains a manually triggered, read-only audit of **published resources only**. It is not a release gate or a separate scheduled auditor. It reports missing/private resources, checksum drift, and **FAIL for published parents referencing unpublished dependencies**. It cannot determine whether a linked PDF/video is the *intended* content, so human review remains essential. See [Inspection](INSPECTION.md).
