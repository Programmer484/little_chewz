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

## SYS-005 — Colour and printer-friendly worksheet versions in the Print Pack Builder

**Status:** Proposed, not implemented.

Some worksheets may need a colour version and a separate printer-friendly version (for example, an ink-saving layout without dark backgrounds). The Teacher Guide should keep one link per worksheet rather than separate "colour" and "black and white" links, likely pointing to a Drive folder that holds both versions. The [Print Pack Builder](apps/AGENTS.md) then needs to look one level deeper: offer a Colour / Printer-friendly choice and fetch the matching file. Decide how the two files are recorded in `catalog/resources.json` before implementing. Plain black-and-white printing of a colour PDF needs nothing: teachers choose it in the print window.

## SYS-006 — Google Form–triggered teacher resource sharing

**Status:** Proposed, not implemented.

Explore a teacher registration/request workflow using **Google Forms + Google Apps Script + Google Drive**. On form submission, capture the teacher's email and requested resource(s), check eligibility or approval where needed, grant access only to the specific approved Drive files/folders, and email the appropriate links. A Google Sheet may track submissions, access decisions, and sharing actions.

Before implementation, decide whether access is immediate or manually approved, how purchases/teacher eligibility are verified (form submission alone is not verification), what access scope and expiration/revocation rules apply, and how to avoid exposing paid or unpublished materials. Respect the existing holding-versus-official publication boundary; **never let a form submission publish resources or bypass review**. Confirm Apps Script trigger ownership, Google Workspace sharing restrictions, duplicate submissions, failures, and the audit trail before enabling automated permission changes.

## SYS-007 — Print Pack Builder settings page for default group size

**Status:** Proposed, not implemented.

The [Print Pack Builder](apps/AGENTS.md) prefills each group activity's **Groups** field with students ÷ 4, rounded up. Add a small settings page where a teacher sets their own default students per group, saved in the browser like the class size. Keep the per-activity Groups field as the override; do not reintroduce a group-size field on the lesson page.

## Previously implemented

- Targeted PDF validations and durable preview history: [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup).
- Human-reviewed slide PDF to linked PPTX conversion: [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- Historical backlog: [archive/2026-10/](archive/2026-10/README.md).
