# Little Chewz — Companion Resource Guidelines (Draft)

**Purpose:** Support the Teacher Guide without repeating its Teaching Flow. A resource should be understandable when opened by itself.

## Editorial rules
- One clear purpose per document; title it for the activity (e.g., **Songwriting Extension**).
- Start with *what the teacher needs to do*. Use clear verbs, not long lesson-plan sections.
- Include only the steps, prompts, materials, or examples necessary for this specific resource.
- State **additional time** when applicable. Do not present it as part of the core lesson time.
- Preserve original approved content and terminology; don't invent activities to fill an empty template.
- Optional questions should remain optional. Omit generic “Extra Prompt,” “Reflect,” “Learning Focus,” etc., unless they provide real teaching value.
- Do **not** add a “Back to Teaching Flow” link: the resource opens in a new tab.

## Visual rules
- Default: a small **section name**, a clear **resource title**, optional time, and plenty of white space.
- Use the section accent colour *plus text* to identify the origin; colour must not be the only cue.
- No decorative header, badge, page number, or boxed layout by default.
- Allow a badge, illustration, setup photo, or folder motif **only** when it improves comprehension or materially helps navigation.
- Match the Teacher Guide's readable typography and economical colour palette. Avoid dense, decorative pages.
- Keep an **8 pt title-to-section-label spacing** (4 pt more than the previous 4 pt gap). Use the same title style for every supplementary resource.

## Loose generator contract
- Content is JSON. The generator assembles **optional blocks**: paragraph, steps, questions, bullets, heading, note, image, links, spacer.
- There is **no fixed sequence or minimum number of blocks**. Do not force one page, one template per activity, or decorative filler.
- Link external files with approved resource IDs/URLs; verify links and sharing settings before publishing.
- Keep source JSON, PDF generator, and generated PDF separate. Review the rendered result as a teacher before publishing.

## Quick use
```bash
pip install reportlab
python resource_generator.py songwriting_extension.json
python resource_generator.py mission_video_questions.json
```
For approved hyperlinks, use `--registry path/to/Template/resources.json`. The two examples demonstrate the same generator with different resource structures.
