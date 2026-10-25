# Classroom slide PDF → PowerPoint

Owns the slide PDF review, PPTX conversion, and in-place Drive replacement routine. Status rules belong to [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md); general saving and reporting follow [WORKFLOW.md](WORKFLOW.md). Human review is separate from publication status; nothing here publishes without authorization.

## Routine

1. **Iterate on the PDF.** A human downloads the **lesson-specific PDF** from the [Slide PDFs Drive folder](https://drive.google.com/drive/u/0/folders/1Qryh6aiuHsZqiTpzP_BvulK-W43EK45g). Human and AI iterate on that PDF (page order, content, clickable links). It is the review artifact; the PowerPoint is never the editing source. Keep each lesson's slides separate. Do not update Drive while iterating.
2. **Approval gate.** The human must explicitly approve the **exact final PDF** and intended lesson. A past approval, GitHub merge, generated PPTX, or passing conversion check does not approve a changed PDF. The approved PDF's actual page count and order are authoritative: lesson metadata and outlines are context, never a slide-count requirement, so do not add or remove slides to match them. Ask only when the approved artifact itself is ambiguous.
3. **Convert and check** (below).
4. **Replace both existing Drive files in place:** the PDF and its paired existing binary `.pptx` (not a copy, new file, or native Google Slides conversion). A missing PPTX destination is a blocker, not permission to create one. Stage and check both deliverables before replacing either.
5. **Read back and report** the exact file IDs and approval scope. Only the exact reviewed version, replaced and verified, may become `published`; uploading alone never advances status.

## Conversion

From the repository root after `pip install -r requirements.txt`:

    python scripts/pdf_to_linked_slides.py reviewed.pdf -o reviewed.pptx --json conversion-report.json

Default: **PyMuPDF render 1.5x → Pillow JPEG quality 92 → python-pptx**. Every PDF page becomes one full-bleed slide image, so text is intentionally not selectable. PDF URI and internal page links become transparent PowerPoint hotspots in their original clickable positions. **Unsupported PDF actions fail by default**. Do not pass `--allow-unsupported-links` on a publication build.

For exceptionally small type: `--scale 2 --quality 94`. Preserve the PDF's original aspect ratio; mixed-aspect input fails.

A previous **seven-page** Set the Table benchmark took approximately **1.1 seconds**, yielding a **5.07 MB** PPTX with both link annotations preserved (about **66% smaller** than its earlier PPTX). This is an indicative local benchmark, not an upload-time guarantee.

## Required checks before and after replacement

1. Verify pages and links against the approved PDF; the PPTX must match it exactly.
2. Run the converter; require **zero warnings**, exact page/slide count, one full-slide image per slide, and URL/internal-link parity. A picture of a play button is **not** working media unless it has a preserved link.
3. Open text-heavy and linked slides visually. Test all links in PowerPoint; **after opening the PPTX in Google Slides, use Present mode and test links again**. File validation alone cannot prove Google Slides click behavior or Drive media permissions.
4. Before upload, read target Drive metadata and verify expected **file ID and MIME type** (PDF: `application/pdf`; PPTX: `application/vnd.openxmlformats-officedocument.presentationml.presentation`). Replace bytes via Drive **files.update** / connected app's `update_file(fileId, file_uri, mime_type)`, not upload/create or rename. Preserve file IDs, folder placement, and sharing.
5. Read back both files' metadata (IDs, MIME types, updated sizes/times) and confirm the PPTX opens and its external links work. If one replacement fails, report the partial state and retry/restore deliberately; never claim the pair was published successfully.

## Verified current Drive targets (2026-10-22)

| Lesson | Existing PDF file ID | Existing PPTX file ID | Current review state |
| --- | --- | --- | --- |
| Activate | `1l_QwHQPRvKCL_n43xlvTyDHFxQy8poE_` | **Not located** | Published seven-slide PDF. Do not create/replace a PPTX without locating or approving a destination. |
| Set the Table | `1r5w-EWU3N47iz5p02NSOsmN-P7Kv7QJt` | `1PQnFI3ryAvTj70NNKmlWqfbdkOcDUPkd` | **Approved 7-slide PDF and PPTX replaced in place on 2026-10-22.** |

The PDFs are in the folder above. The Set the Table PowerPoint was located separately as `Set_The_Table_Slides.pptx`; it is a stored PPTX, not a native Google Slides file. Its file ID is also recorded with the lesson resource in `catalog/resources.json`. Confirm these IDs and MIME types **afresh** for each publication.

**Latest Set the Table publication (2026-10-22):** human selected the seven-slide edition: slide 6 “Which Word Fits?”, slide 7 “Friendship Mystery #1”. The original six-page PDF's other pages remain visually unchanged; both approved Drive files were updated in place and two audio URL link annotations are preserved on slide 4. Verified remote sizes: PDF 11,933,343 bytes, PPTX 5,034,225 bytes. External PDF link-sharing to unauthenticated viewers has **not** been verified; do not change permissions without approval. The uploaded Activate PDF is seven pages with a video URL link on pages 4 and 5; no Activate PPTX target was identified.

## Future editable slides

Editable slide-JSON generation remains **unimplemented** (see [SYS-002](../SYSTEM_IMPROVEMENTS.md#sys-002--editable-lesson-slide-generation)). This utility only packages an approved PDF into a PowerPoint and restores PDF link annotations; it is not a slide editor, an automatic GitHub preview target, or an autonomous Drive publisher.
