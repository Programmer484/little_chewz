# Publication audit — Exists / Accessible / Correct

**Scope:** Published catalogue resources only. Drafts and pending publications are skipped. A published Teacher Guide must not link to an unpublished resource.

Run **Actions → Inspect published resources** without an ID for everything, or with a resource ID for one published item. Read-only; the manual workflow audits current main.

## EXISTS
- The exact registered Drive file exists and is not in Trash.
- It is in its pre-approved official folder, saved in catalog/drive_folders.json → published.by_resource_id. Never guess the approved folder from the current location.
- Slide decks require checking **both** the PowerPoint and the companion PDF (pdf_url).

## ACCESSIBLE
- Google Drive has **anyone-with-link viewing** enabled.
- Website links open without a sign-in redirect.
- If sharing information is unavailable, report NEEDS REVIEW. Drive permission metadata cannot prove real incognito browser behaviour.

## CORRECT
- The current checksum equals the checksum saved upon approval.
- The generated-PDF publisher already records publication.artifact_md5 and the audit also compares the current GitHub-generated PDF to it.
- Approved external files require publication.approved_md5, and slide PDF companions require publication.pdf_md5. These must be recorded at approval, NOT inferred from the current file during inspection.
- Published Teacher Guide PDFs are downloaded and their **actual hyperlinks** are inspected. References to unpublished resources or absent expected links fail; unregistered links require review.
- Dynamic websites and folders have no stable downloadable checksum: treat content as NEEDS REVIEW until an appropriate approved verification method exists.

## Three results
- **PASS** — verified.
- **FAIL** — provably wrong (missing, trashed, wrong folder, nonpublic, checksum mismatch, or broken published Guide references).
- **NEEDS REVIEW** — cannot establish the fact from evidence (including missing baseline).

Every resource reports Exists / Accessible / Correct independently. Any FAIL makes the overall audit FAIL; otherwise any NEEDS REVIEW keeps the overall result NEEDS REVIEW. GitHub Actions turns green only if all published resources pass and always saves the report.

## Existing publications
Older published resources do not yet all have approved folder and checksum baselines. They will need review until explicitly approved and recorded. Do not automatically trust today's Drive file as the approved file. Existing publication authorization and safeguards remain unchanged.

This is an inspection, not a publisher: it never changes Drive or catalogue data.
