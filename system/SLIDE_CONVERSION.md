# Classroom slide PDF → PowerPoint (technical standard)

**Workflow owner:** [WORKFLOW.md](WORKFLOW.md#classroom-slide-pdf-to-powerpoint). This file documents the converter and verified destinations; it does not grant publication approval.

## Established workflow

A human downloads the **lesson-specific PDF** from the [Slide PDFs Drive folder](https://drive.google.com/drive/u/0/folders/1Qryh6aiuHsZqiTpzP_BvulK-W43EK45g). Human and AI iterate on that PDF (including page order and clickable links). Treat that exact revised PDF as the review artifact; do **not** edit the PowerPoint during iterations or treat a generated PPTX as editable source. After explicit human approval of the exact PDF, generate a PPTX from it and replace **both existing Drive files in place**: the PDF and its paired `.pptx`. The PowerPoint is updated directly as a binary `.pptx`, not converted to a newly created Google Slides file.

## Conversion

From the repository root after `pip install -r requirements.txt`:

    python scripts/pdf_to_linked_slides.py reviewed.pdf -o reviewed.pptx --json conversion-report.json

Default: **PyMuPDF render 1.5x → Pillow JPEG quality 92 → python-pptx**. Every PDF page becomes one full-bleed slide image, so text is intentionally not selectable. PDF URI and internal page links become transparent PowerPoint hotspots in their original clickable positions. **Unsupported PDF actions fail by default**. Do not pass `--allow-unsupported-links` on a publication build.

For exceptionally small type: `--scale 2 --quality 94`. Preserve the PDF's original aspect ratio; mixed-aspect input fails.

A previous **seven-page** Set the Table benchmark took approximately **1.1 seconds**, yielding a **5.07 MB** PPTX with both link annotations preserved (about **66% smaller** than its earlier PPTX). This is an indicative local benchmark, not an upload-time guarantee or a benchmark of the newer six-page PDF.

## Required checks before and after replacement

1. Compare the final PDF with the **approved** page count, order, designs, and clickable destinations; page-count differences are review blockers, not automatic renumbering.
2. Run the converter; require **zero warnings**, exact page/slide count, one full-slide image per slide, and URL/internal-link parity. A picture of a play button is **not** working media unless it has a preserved link.
3. Open text-heavy and linked slides visually. Test all links in PowerPoint; **after opening the PPTX in Google Slides, use Present mode and test links again**. File validation alone cannot prove Google Slides click behavior or Drive media permissions.
4. Before upload, read target Drive metadata and verify expected **file ID and MIME type** (PDF: `application/pdf`; PPTX: `application/vnd.openxmlformats-officedocument.presentationml.presentation`). Replace bytes via Drive **files.update** / connected app's `update_file(fileId, file_uri, mime_type)`, not upload/create or rename. Preserve file IDs, folder placement, and sharing.
5. Read back both files' metadata (IDs, MIME types, updated sizes/times) and confirm the PPTX opens and its external links work. If one replacement fails, report the partial state and retry/restore deliberately; never claim the pair was published successfully.

## Verified current Drive targets (2026-10-22)

| Lesson | Existing PDF file ID | Existing PPTX file ID | Current review state |
| --- | --- | --- | --- |
| Activate | `1l_QwHQPRvKCL_n43xlvTyDHFxQy8poE_` | **Not located** | Published seven-slide PDF. Do not create/replace a PPTX without locating or approving a destination. |
| Set the Table | `1r5w-EWU3N47iz5p02NSOsmN-P7Kv7QJt` | `1PQnFI3ryAvTj70NNKmlWqfbdkOcDUPkd` | **Not approved for replacement**. |

The PDFs are in the folder above. The Set the Table PowerPoint was located separately as `Set_The_Table_Slides.pptx`; it is a stored PPTX, not a native Google Slides file. Its file ID is also recorded with the lesson resource in `catalog/resources.json`. Confirm these IDs and MIME types **afresh** for each publication.

**Current discrepancy:** the PDF uploaded for Set the Table in the 2026-10-22 review is **six pages** with two song-link annotations on page 4; `lessons/01-set-the-table/stage.json` still describes **seven slides**, including “Which Word Fits?” at slide 6. Resolve this explicitly with the human before approving or publishing. The uploaded Activate PDF is seven pages, with one video link each on pages 4 and 5. Neither upload itself is approval.

## Separate future system

Editable slide-JSON generation remains **unimplemented** (see `SYSTEM_IMPROVEMENTS.md` SYS-002). This utility only packages an approved PDF into a PowerPoint and restores PDF link annotations; it is not a slide editor, an automatic GitHub preview target, or an autonomous Drive publisher.
