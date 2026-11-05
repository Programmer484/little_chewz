# Manual published-resource audit

The existing **Actions → Inspect** is the **only** audit: read-only, on demand, **never scheduled**, never a publish gate. It examines catalogue entries **only when `published_url` is present**, including published resources with staged revisions; it skips unpublished resources as audit targets.

For each published item:
- Inspect its **published** URL, not Holding or slide-source URLs. Check Drive ID, existence, non-Trash state and anonymous sharing where measurable. Confirmed private/trashed is FAIL; unverifiable access is NEEDS REVIEW. For non-Drive URLs, matching exact `human_reviewed_url` gives PASS, otherwise NEEDS REVIEW.
- For generated PDFs, compare the live Drive MD5 to verified `pdf.approved_md5`; mismatch is FAIL, missing evidence is NEEDS REVIEW.
- **Reject all unpublished dependencies:** infer `ref`/navigation IDs from registered generated-PDF sources and use explicit `dependencies` IDs for externally authored files. A published parent's missing or unpublished dependency yields **FAIL**, even if its Holding URL opens. The unpublished dependency itself is **not audited**.
- Report PASS/FAIL/NEEDS REVIEW with safe diagnostics. Confirmed FAIL makes the manual Action fail; an inconclusive check is not misreported as a confirmed failure.

This does **not** parse arbitrary hyperlinks inside externally authored PDFs, verify YouTube content, test folder placement or decide whether a teacher-facing link goes to the correct lesson. The human checks that in the exact final artifact, ideally signed out. Publishing rules live in [Publish](PUBLISH.md).
