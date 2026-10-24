# System improvements

This file tracks **active** system work. The original migration and completed CI proposals are preserved in [archive/2026-10/](archive/2026-10/README.md).

Live editing, status and publishing rules belong to [WORKFLOW.md](system/WORKFLOW.md), [CONTENT_CONTRACT.md](system/CONTENT_CONTRACT.md) and [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md). A backlog item never grants permission to publish to Drive.

## SYS-002 — Editable lesson slide generation

**Status:** Planned, not implemented. **Priority:** Optional.

Current slides are independently maintained human-reviewed lesson PDFs. The supported `scripts/pdf_to_linked_slides.py` tool derives image-based, linked PowerPoint files from an approved PDF.

An eventual editable slide renderer could regenerate a single changed slide or the affected lesson from reviewed editable sources. Build this only when a real editing need justifies it. Do not add placeholder slide JSON, reuse the old continuous 44-slide deck, introduce unused templates, or automatically publish to Drive.

## SYS-003 — Teacher-owned presentation copies

**Status:** Proposed, not implemented. **Priority:** To be decided.

Allow each teacher to make or receive their **own copy of a lesson's slide deck**, then mark slides they do not want to show as **skipped/hidden during presentation**, without deleting the slides or changing the master deck.

**Desired result:**
- Each teacher can independently choose which slides appear in their presentation.
- Hidden slides remain available for the teacher to restore later.
- The approved master deck and other teachers' copies stay unchanged.
- Preserve slide order, clickable media/resource links, and lesson-local numbering wherever the presentation format supports them.

**To determine before implementation:** Teacher access and the copy-delivery workflow (for example, a copyable Google Slides presentation versus a downloadable PowerPoint). Confirm that the chosen format actually supports skipping slides during its presenter/slideshow mode and that copied media links continue to work. This is a teacher-facing convenience feature, **not** permission to edit or republish the approved master.

## Already implemented

- GitHub Actions validation, targeted PDF previews, and permanent browser previews on a shared history branch: [WORKFLOW.md](system/WORKFLOW.md#pdf-build-selection).
- Approved lesson PDF to linked PPTX conversion: [SLIDE_CONVERSION.md](system/SLIDE_CONVERSION.md).
- Prior designs and completed proposals: [historical system improvements](archive/2026-10/SYSTEM_IMPROVEMENTS_ORIGINAL.md).
