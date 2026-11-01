# System improvements

This file tracks **active** work; repository instructions and publication authority live in [WORKFLOW.md](system/WORKFLOW.md) and [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Backlog entries never authorize publication.

## Implemented — two resource workflows (2026-10-25)

- Production-based registry: `generated_pdf` vs `external`, source provenance, explicit generated-PDF build mapping, holding vs official URLs and publication evidence.
- Verified Google Drive review holding root and four category folders; existing Slide PDFs review folder remains separate.
- Authorized generated-PDF PR merge Action supporting multiple explicitly approved resource IDs per release, with per-resource ownership checks, same-ID Drive replacement, MD5 and accepted revision verification, failure reporting and safe edit-branch cleanup.
- External resources stay agent-created and agent-published; no external `/merge` integration, external checksum automation or GitHub source-creation engine.
- Manual-only read-only publication inspector, with external content parity explicitly unverified.

**Operational prerequisites:** service-account access to specific official Drive targets; agent establishment of each generated PDF's first official destination. Existing legacy items with unknown history retain unverified evidence until independently checked. A passing CI check does not grant Drive access or publication authority.

## SYS-002 — Editable lesson slide generation

**Status:** Optional, not implemented.

Current slides remain separate human-reviewed lesson PDFs; `scripts/pdf_to_linked_slides.py` derives linked PPTX. Do not add speculative slide JSON, reuse the archived continuous 44-slide deck, or automatically publish external slides.

## SYS-003 — Teacher-owned presentation copies

**Status:** Proposed, not implemented.

Teachers may eventually receive independent copies of a lesson deck with hidden/skipped slides, preserving the reviewed master and its clickable links. Confirm the actual PowerPoint/Google Slides presentation behavior, permissions and copy workflow before implementation.

## SYS-004 — Verify teacher access to published Drive resources

**Status:** Low priority, proposed; not implemented.

Add a **read-only** audit for Google Drive resources marked `published`, starting with those linked by current Teacher Guides. Verify the exact official file ID, intended reader permissions (including inherited access where applicable), and, when practical, actual access as a teacher without publisher credentials. Report `accessible`, `access problem`, or `unable to verify` with the affected resource ID; never mistake authenticated owner access or recorded publication status for teacher access. Do not automatically change permissions or publish resources. Run on demand or periodically rather than on every content edit; keep the existing manual publication-access checks until the audit exists.

## Previously implemented

- Targeted PDF validations and durable preview history: [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup).
- Human-reviewed slide PDF to linked PPTX conversion: [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- Historical backlog: [archive/2026-10/](archive/2026-10/README.md).
