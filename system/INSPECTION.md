# Publication inspection — Drive sharing + human link review

**Scope:** Published resources only. Inspection does not publish, modify Drive, or alter catalogue statuses.

- **Standard Google Drive links** (even when human-reviewed): confirm the exact file is accessible to the service account, is not in Trash, and has `anyone` viewing permission. No folder placement, PDF bytes, checksums, or content correctness checks.
- **Non-Google-Drive links:** human review only. No automated website probing.
- **Externally owned Drive files:** set `review_mode: "human"` and track the exact URL in `human_review` to bypass service-account checks. Only these explicitly marked Drive links bypass Drive permissions.
- **After review:** change only that URL's value from `pending` to `reviewed`. A changed URL does not inherit approval. Slide decks inspect both the primary and PDF URLs. Recording review on standard Drive links never disables the automated permission check.
- **Missing/invalid URLs, trashed Drive files, and confirmed nonpublic Drive sharing**: FAIL.
- **Service-account access/permission uncertainty**: NEEDS REVIEW, not a claim that the file is missing.
- **Fail fast within a resource** but continue through the catalogue to collect every other issue and review link.

The GitHub Actions summary is one table with failures and URLs awaiting human review; successful resources are omitted. A run fails only for a confirmed FAIL. Outstanding human reviews remain visible but do not falsely fail the workflow.

Generated-PDF publication itself still performs its existing source checksum and Drive read-back checks in `publish_to_drive.py`. Those publishing safeguards are distinct from link inspection.
