# Publication inspection — Drive sharing + human link review

**Scope:** All resources with an official `published_url`, **including pending replacements**, except classroom slide decks. The inspector validates the existing live destination and never publishes, modifies Drive or calculates resource delivery status.

- **Standard Google Drive links** (even when human-reviewed): confirm the exact file is accessible to the service account, is not in Trash, and has `anyone` viewing permission. No folder placement, PDF bytes, checksums, or content correctness checks.
- **Non-Google-Drive links:** human review only. No automated website probing.
- **Externally owned Drive files:** set `review_mode: "human"` and track the exact URL in `human_review` to bypass service-account checks. Only these explicitly marked Drive links bypass Drive permissions.
- **After review:** change only that URL's value from `pending` to `reviewed`. A changed URL does not inherit approval. Recording review on standard Drive links never disables the automated permission check.
- **Missing/invalid URLs, trashed Drive files, and confirmed nonpublic Drive sharing**: FAIL.
- **Service-account access/permission uncertainty**: NEEDS REVIEW, not a claim that the file is missing.
- **Classroom slides:** skip slide-deck links entirely. Published PPTX files are kept in the official slide folder; their approved source PDFs are recorded in `pdf_url`, not `holding_url`. A separate newly staged revision would use `holding_url`. Neither is checked by the publication inspector.
- **Fail fast within a resource** but continue through the catalogue to collect every other issue and review link.

A separate generated-PDF checksum comparison derives pending publication when a current source PDF is built; link inspection does not determine source parity. The GitHub Actions summary is one table with failures and URLs awaiting human review; successful resources are omitted. A run fails only for a confirmed FAIL. Outstanding human reviews remain visible but do not falsely fail the workflow.

Generated-PDF publication itself still performs its existing source checksum and Drive read-back checks in `publish_to_drive.py`. Those publishing safeguards are distinct from link inspection.
