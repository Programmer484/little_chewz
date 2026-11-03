# Publication inspection — Drive access and exact URL review

**Scope:** Every catalogue resource with a `published_url`, including pending replacements and classroom slides. The inspector is read-only; it never publishes, moves Drive files or changes catalogue metadata.

- **Any Google Drive / Google Docs URL:** verify ID, accessibility to the service account, not in Trash, and an `anyone` public permission. No ownership exception or manual review bypass. If Google refuses metadata/permissions, report NEEDS REVIEW rather than claiming inaccessible implies absent.
- **Generated PDF (has `pdf`):** after confirming public permissions, compare the official Drive file's `md5Checksum` with `pdf.approved_md5`. Missing approved/Drive checksum = NEEDS REVIEW; mismatch = FAIL. The first verified generated-PDF publication captures the baseline; never infer one from an unverified historical link.
- **Non-Drive URL:** exact matching `human_reviewed_url` passes. Otherwise require human review automatically (NEEDS REVIEW), with no manual `review_mode` or `human_review` assignment. Approval is invalidated if the published URL changes.
- **Slides:** check the published presentation's Google URL; do not inspect its separately recorded `pdf_url` source or staged `holding_url` copy.
- **Unpublished resources:** skip if `published_url` is null.
- **Results:** PASS confirms the corresponding check; FAIL for confirmed bad/missing published links, private permissions or wrong generated PDF bytes; NEEDS REVIEW means uncertainty or pending human approval. Only FAIL makes the manually triggered full inspection workflow red. Generated publication workflows treat FAIL and NEEDS REVIEW as release blockers.

The Action summary shows only problem links, not every passing file. The JSON report includes outcomes and a separate downloadable .txt artifact records sanitized API operation, file ID, status and reason; no raw exception text or credentials. The inspector never checks PDF hyperlinks, live site responses, ownership, folder placement or source content parity. A separate `publication_state.py` build compares current GitHub output with `pdf.approved_md5` to derive pending edits. The Drive publisher verifies exact bytes and writes the approved checksum/revision only after read-back.
