# Companion resource guidelines (Draft)

Companions support the Teacher Guide without repeating its Teaching Flow. Each must make sense when opened alone. These guidelines retain their draft status; this cleanup does not approve content.

## Writing

- Give each document one clear purpose and an activity-specific title, such as **Songwriting Extension**.
- Start with what the teacher needs to do. Include only necessary steps, prompts, materials, and examples; avoid long lesson-plan sections.
- State additional time when applicable, separately from core lesson time.
- Preserve approved content and terminology. Never invent activities to fill a template.
- Keep optional questions optional. Omit generic prompts or learning-focus sections unless they add practical value.
- Do not add a “Back to Teaching Flow” link; the resource opens in a new tab.

## Presentation

- Default to a small section name, clear resource title, optional time, and ample white space.
- Identify the origin with section accent colour plus text; never rely on colour alone.
- No decorative header, badge, page number, or boxed layout by default. Use illustrations, setup photos, badges, or folder motifs only when they aid comprehension or navigation.
- Match the Teacher Guide's readable typography and economical palette. Use one title style across companions and **8 pt title-to-section-label spacing**.
- Keep question banks easy to scan. An illustrated instruction page is appropriate when it demonstrates setup, printing, assembly, or use.
- For multiple resource variants, link the Teacher Guide to one instruction/chooser PDF that links to the separate versions.

## Source and generation

Companions use JSON with optional `paragraph`, `steps`, `questions`, `bullets`, `heading`, `note`, `image`, `links`, and `spacer` blocks. No fixed block order, minimum count, one-page requirement, or decorative filler. Start from `templates/teacher_companion/TEMPLATE.json`.

Use the ownership and approved-link rules in [CONTENT_CONTRACT.md](CONTENT_CONTRACT.md). Layout implementation lives in `scripts/renderers/teacher_companion.py`; follow [WORKFLOW.md](WORKFLOW.md) for checking, previews, and publication. See [START_HERE.md](../START_HERE.md#local-checks-and-approved-previews) for current commands.
