# Migration report — October 15, 2026

## What was inspected

- User-provided Google Drive root and its visible immediate folder structure.
- `Lesson_Plan_Template/`: editorial AGENTS, README, Python Teacher Guide generator, URL registry and one Activate JSON.
- `Resource_Template.zip`: companion resource generator, companion editorial instructions and three resource JSON sources.
- Attached `Full Guide Revised.pdf` (29 pages), `Full Guide.pdf` (109 pages), `Bake off Betrayal.pdf` (44-slide PDF), `Little Chewz Demo.pdf` (five-page outreach PDF).
- Live `Activate_Teacher_Guide.pdf` and the live seven-page `Activate_Slides.pdf`.

## Verified architectural findings

1. Source types and generated PDFs are mixed in public-facing folders.
2. The Teacher Guide has a JSON/PyMuPDF generator; companion questions have another JSON/ReportLab generator. Both are good reusable foundations.
3. The original Teacher Guide instructions call the registry `Template/resources.json`; the current Drive folder contains `resource_links.json`. This draft standardizes one `catalog/resources.json`.
4. Live `Activate_Slides.pdf` has seven pages: Tongsley video slide 4 and Callie slide 5. These match the newer Activate JSON, not the older Revised Guide's whole-deck positions.
5. Source files for six other stages are not visible in the inspected Drive structure; their lesson text can be recovered from the Revised Guide in an *audited one-time migration*.
6. `passport` in current registry links to School Pass Instructions rather than the actual color/B&W passport sheets.
7. The optional Songwriting Extension JSON exists in the source ZIP, but the observed public Drive folder contains a PDF and it should not be linked as newly published until approved.

## Done inside this package

- Built a single AI entrypoint and explicit metadata/status rules.
- Preserved approved editorial guidance and both existing shared generators.
- Centralized current approved URLs under one catalog file.
- Migrated actual current Activate JSON, plus an image cover source, without changing content wording.
- Migrated three existing companion-resource source JSON files, adding stable IDs and review states.
- Added a sample source taxonomy and templates for worksheets, references, slide decks, media and stories.
- Added lightweight validation and source-to-export build scripts.
- Preserved raw text of two original historical/teacher read-alouds as **draft transcriptions** requiring content verification.
- Added explicitly labelled unconverted stages instead of inventing missing source data.

## Still needed before a live Drive move

1. Approve the canonical folder tree and decide whether to use a Git repository as source with Drive as distribution, or Drive raw files as source.
2. Decide continuous quest slideshow versus separate stage decks.
3. Transcribe/verify the remaining six guide stages and priority student materials; tag the actual origin and reviewer.
4. Migrate the rest of the distinct student and teacher resource types by priority, without flattening visual worksheets into the wrong resource generator.
5. Populate remaining resource links and audit Drive access/sharing; make sure teacher-facing links point to printable chooser/variants.
6. Generate, visually QA and replace old PDFs in place only after approval; archive old source duplicates after confirming the new source is complete.

**No live Drive items were moved, deleted, renamed, replaced, or republished in preparing this package.**

## GitHub migration decisions (2026-10-18)

- Destination: `Programmer484/little_chewz`. Migrate AI-editable sources and generators first, retaining Google Drive as the unchanged live distribution location.
- Quest slideshow: **one continuous deck**. Existing seven-slide Activate and historical 44-slide version are not silently fused or renumbered.
- Remaining six stages: **explicit skeletons**, not rewritten lesson content and not buildable `lesson.json`.
- Layout/content design of further resource types and link reconciliation: later work.
- Replacing/archiving published Drive files: **not part of this migration**.

## Superseding slideshow decision (2026-10-19)

The October 18 decision for a continuous quest-wide deck is superseded. Future slides will be independently generated and maintained **per lesson**, using lesson-local numbering. Edit individual slides and regenerate only the affected lesson's slides. Retain the approved Activate segment unchanged; the historical 44-slide quest deck is a legacy reference only. No slide renderer, new generated slide set or Drive publication is implied by this policy change.
