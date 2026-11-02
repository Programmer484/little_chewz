# System improvements

This file tracks **active** work; repository instructions and publication authority live in [WORKFLOW.md](system/WORKFLOW.md) and [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md). Backlog entries never authorize publication.

## Implemented — two resource workflows (2026-10-25)

- Production-based registry: `generated_pdf` vs `external`, source provenance, explicit generated-PDF build mapping, holding vs official URLs and publication evidence.
- Verified Google Drive review holding root and four category folders; existing Slide PDFs review folder remains separate.
- Authorized single-resource generated-PDF PR merge Action, same-ID Drive replacement with MD5 and accepted revision, failure reporting and safe edit-branch cleanup.
- External resources stay agent-created and agent-published; no external `/merge` integration, external checksum automation or GitHub source-creation engine.
- Manual-only read-only publication inspector, with external content parity explicitly unverified.

**Operational prerequisites:** service-account access to specific official Drive targets; agent establishment of each generated PDF's first official destination. Existing legacy items with unknown history retain unverified evidence until independently checked. A passing CI check does not grant Drive access or publication authority.

## SYS-002 — Editable lesson slide generation

**Status:** Optional, not implemented.

Current slides remain separate human-reviewed lesson PDFs; `scripts/pdf_to_linked_slides.py` derives linked PPTX. Do not add speculative slide JSON, reuse the archived continuous 44-slide deck, or automatically publish external slides.

## SYS-003 — Teacher-owned presentation copies

**Status:** Proposed, not implemented.

Teachers may eventually receive independent copies of a lesson deck with hidden/skipped slides, preserving the reviewed master and its clickable links. Confirm the actual PowerPoint/Google Slides presentation behavior, permissions and copy workflow before implementation.

## SYS-004 — Colour and printer-friendly worksheet versions in the Print Pack Builder

**Status:** Proposed, not implemented.

Some worksheets may need a colour version and a separate printer-friendly version (for example, an ink-saving layout without dark backgrounds). The Teacher Guide should keep one link per worksheet rather than separate "colour" and "black and white" links, likely pointing to a Drive folder that holds both versions. The [Print Pack Builder](apps/AGENTS.md) then needs to look one level deeper: offer a Colour / Printer-friendly choice and fetch the matching file. Decide how the two files are recorded in `catalog/resources.json` before implementing. Plain black-and-white printing of a colour PDF needs nothing: teachers choose it in the print window.

## Previously implemented

- Targeted PDF validations and durable preview history: [WORKFLOW.md](system/WORKFLOW.md#previews-and-cleanup).
- Human-reviewed slide PDF to linked PPTX conversion: [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- Historical backlog: [archive/2026-10/](archive/2026-10/README.md).
